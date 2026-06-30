from enum import Enum
import gc
import os
import tempfile
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.afc import AfcService, datetime
from helper.file_helper_functions import (
    find_date_in_text,
    is_media_file,
    is_video_file,
    extract_metadata_fast,
)
from models.dataclass.data_class import DirectoryOrder
from models.devices import Device
from models.devices.device_type import DeviceType
from pillow_heif import register_heif_opener


class IosTags(Enum):
    # possibly incomplete
    DATETIME = "DateTime"
    DATETIME_ORIGINAL = "DateTimeOriginal"
    FILE_MODIFY_DATE = "FileModifyDate"
    FILE_ACCESS_DATE = "FileAccessDate"
    CREATE_DATE = "CreateDate"
    CREATION_DATE = "CreationDate"
    MODEL = "Model"
    LENS_MODEL = "LensModel"
    AUTHOR = "Author"
    DESCRIPTION = "Description"
    USER_COMMENT = "UserComment"


DATE_KEYS = [IosTags.DATETIME.value,
             IosTags.DATETIME_ORIGINAL.value,
             IosTags.CREATE_DATE.value,
             IosTags.CREATION_DATE.value,
             IosTags.FILE_MODIFY_DATE.value,
             IosTags.FILE_ACCESS_DATE.value]


MEDIA_FOLDER = "/DCIM"


class IphoneDevice(Device):
    def __init__(self, udid: str, connection_type: str = "usb"):
        self.type = DeviceType.IOS
        self.udid = udid
        self.connection_type = connection_type
        self.lock_down = None
        self.registered_paths = []
        # self.device_manager = None
        self.unique_names = set()
        register_heif_opener()

    def __repr__(self):
        return (
            f"Name: {self.get_device_name()}, "
            f"IphoneDevice(udid={self.udid},"
            f"connection={self.connection_type})"
        )

    async def connect(self):
        self.lock_down = await create_using_usbmux(self.udid)
        # self.device_manager = AfcService(self.lockdown)

    async def open_afc(self):
        """Create a fresh AfcService on whatever loop is currently running."""
        self.lock_down = await create_using_usbmux(self.udid)
        return AfcService(self.lock_down)

    async def get_all_files(self):
        afc = await self.open_afc()
        folders = await afc.listdir(MEDIA_FOLDER)

        for folder in folders:
            files_in_folder = await afc.listdir(
                f"{MEDIA_FOLDER}/{folder}"
            )

            for f in files_in_folder:
                if not is_media_file(f):
                    continue

                name = os.path.splitext(f)[0]

                if name in self.unique_names:
                    if is_video_file(f):
                        continue
                    else:
                        prefix = f"{MEDIA_FOLDER}/{folder}/{name}"
                        self.registered_paths = [
                            p for p in self.registered_paths
                            if not p.startswith(prefix)
                        ]

                self.unique_names.add(name)
                self.registered_paths.append(f"{MEDIA_FOLDER}/{folder}/{f}")

        return self.registered_paths

    async def get_file_content(self, file_path):
        afc = await self.open_afc()
        try:
            return await afc.get_file_contents(file_path)
        except Exception as e:
            print(f"Error getting file content for {file_path}: {e}")
            return None

    async def get_partial_file(self, file_path: str, max_bytes: int) -> bytes:
        """Download only the first max_bytes of a file for metadata only."""
        afc = await self.open_afc()
        try:
            resolved_path = await afc.resolve_path(file_path)
            info = await afc.stat(resolved_path)
            read_size = min(max_bytes, int(info["st_size"]))
            handle = await afc.fopen(resolved_path, "r")
            if not handle:
                return None
            try:
                return await afc.fread(handle, read_size)
            finally:
                await afc.fclose(handle)
        except Exception as e:
            print(f"Error reading partial file {file_path}: {e}")
            return None

    async def copy_file_to_path(self, source_path: str, destination_path: str):
        afc = await self.open_afc()
        try:
            await afc.pull(
                source_path,
                destination_path,
                progress_bar=False,
            )
        except Exception as e:
            print(f"Error copying {source_path} to {destination_path}: {e}")
            raise

    def get_device_name(self):
        return self.lock_down.all_values.get("DeviceName")

    def _has_embedded_date(self, metadata: dict) -> bool:
        embedded_date_keys = [
            IosTags.DATETIME.value,
            IosTags.DATETIME_ORIGINAL.value,
            IosTags.CREATE_DATE.value,
            IosTags.CREATION_DATE.value,
        ]
        return any(metadata.get(key) for key in embedded_date_keys)

    def _has_contextual_metadata(self, metadata: dict) -> bool:
        contextual_keys = [
            IosTags.MODEL.value,
            IosTags.LENS_MODEL.value,
            IosTags.AUTHOR.value,
            IosTags.DESCRIPTION.value,
        ]
        return any(metadata.get(key) for key in contextual_keys)

    def _is_empty_value(self, value) -> bool:
        """Check if a value is empty or should be ignored."""
        if value is None:
            return True
        empty_values = ("", "none", "null")
        return str(value).strip().lower() in empty_values

    def _extract_description_value(self, metadata: dict) -> str:
        """Extract and format description from metadata.

        Checks USER_COMMENT first for screenshot detection,
        then falls back to DESCRIPTION.
        """
        user_comment = metadata.get(IosTags.USER_COMMENT.value)
        if user_comment:
            user_comment_str = str(user_comment).strip().lower()
            if "screenshot" in user_comment_str:
                return "screenshot"

        description = metadata.get(IosTags.DESCRIPTION.value)
        if description:
            return str(description).strip().lower().replace(" ", "_")

        return None

    def _extract_metadata_from_bytes(self,
                                     source_path: str,
                                     data: bytes) -> dict:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(source_path)[1],
        ) as tmp_file:
            tmp_file.write(data)
            tmp_file_path = tmp_file.name
        try:
            return extract_metadata_fast(tmp_file_path)
        finally:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    async def _extract_metadata_from_device_file(self,
                                                 source_path: str) -> dict:
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(source_path)[1],
            ) as tmp_file:
                tmp_file_path = tmp_file.name

            afc = await self.open_afc()
            await afc.pull(
                source_path,
                tmp_file_path,
                progress_bar=False,
            )
            return extract_metadata_fast(tmp_file_path)
        except Exception as e:
            print(f"Error extracting full metadata for {source_path}: {e}")
            return {}
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    async def _extract_metadata_with_fallback(self,
                                              source_path: str,
                                              partial_bytes: int) -> dict:
        partial_data = await self.get_partial_file(source_path, partial_bytes)
        if partial_data is None:
            raise ValueError("No data returned for metadata extraction")

        metadata = self._extract_metadata_from_bytes(source_path, partial_data)
        del partial_data

        if self._has_embedded_date(metadata) and self._has_contextual_metadata(
            metadata
        ):
            return metadata

        full_metadata = await self._extract_metadata_from_device_file(
            source_path,
        )
        if full_metadata:
            return full_metadata
        return metadata

    async def get_exif_from_image(self, source_path, order=1) -> tuple:
        """
        Extract relevant EXIF tags as DirectoryOrder objects.
        Keys: EXIF tag names
        Values: DirectoryOrder(order, value)
        """
        try:
            metadata = await self._extract_metadata_with_fallback(
                source_path,
                512 * 1024,
            )
            gc.collect()  # Force garbage collection to free memory

            extracted_data = {}

            found_date = False

            for key in DATE_KEYS:
                if key in metadata:
                    year = find_date_in_text(metadata[key])
                    if year is None:
                        continue

                    if (key == IosTags.FILE_MODIFY_DATE.value or
                            key == IosTags.FILE_ACCESS_DATE.value):
                        year = f"{year}/probably_foreign"
                    extracted_data["year"] = DirectoryOrder(
                        order=order+1,
                        directory=str(year)
                    )
                    found_date = True
                    break

            if not found_date:
                extracted_data["year"] = DirectoryOrder(
                    order=order+1,
                    directory=f"{datetime.now().year}_no_exif"
                )

            if IosTags.MODEL.value in metadata:
                desc_value = str(
                    metadata[IosTags.MODEL.value]
                    ).strip().lower().replace(" ", "_")
                extracted_data["model"] = DirectoryOrder(
                    order=order+2,
                    directory=desc_value
                )

            if (
                IosTags.DESCRIPTION.value in metadata
                or IosTags.USER_COMMENT.value in metadata
            ):
                desc_value = self._extract_description_value(metadata)
                if not self._is_empty_value(desc_value):
                    print(f"Description found for {source_path}: "
                          f"{desc_value}")
                    extracted_data["description"] = DirectoryOrder(
                        order=order+3,
                        directory=desc_value
                    )

            lens_model = metadata.get(IosTags.LENS_MODEL.value)
            if lens_model and "front" in str(lens_model).lower():
                extracted_data["camera"] = DirectoryOrder(
                    order=order+4,
                    directory="selfie"
                )
            return extracted_data

        except Exception as e:
            print(f"Error extracting EXIF data from image bytes: {e}")
            return {"year": DirectoryOrder(
                order=order+1, directory=f"{datetime.now().year}_no_exif")}

    async def get_exif_from_video(self, source_path, order=1) -> dict:
        try:
            metadata = await self._extract_metadata_with_fallback(
                source_path,
                2 * 1024 * 1024,
            )
            gc.collect()  # Force garbage collection to free memory

            extracted_data = {}
            found_date = False

            for key in DATE_KEYS:
                if key in metadata:
                    year = find_date_in_text(metadata[key])
                    if year is None:
                        continue

                    if (key == IosTags.FILE_MODIFY_DATE.value or
                            key == IosTags.FILE_ACCESS_DATE.value):
                        year = f"{year}/probably_foreign"

                    extracted_data["year"] = DirectoryOrder(
                        order=order+1,
                        directory=str(year)
                    )
                    found_date = True
                    break

            if not found_date:
                extracted_data["year"] = DirectoryOrder(
                    order=order+1,
                    directory=f"{datetime.now().year}_no_exif"
                )

            if IosTags.MODEL.value in metadata:
                model_value = str(metadata[IosTags.MODEL.value])
                extracted_data["model"] = DirectoryOrder(
                    order=order+2,
                    directory=model_value.strip().lower().replace(" ", "_"),
                )

            if (
                IosTags.AUTHOR.value in metadata
                and "ReplayKitRecording"
                in str(metadata[IosTags.AUTHOR.value])
            ):
                extracted_data["camera"] = DirectoryOrder(
                    order=order+4,
                    directory="screen_recording",
                )

            if (
                IosTags.LENS_MODEL.value in metadata
                and "front" in str(metadata[IosTags.LENS_MODEL.value]).lower()
            ):
                extracted_data["camera"] = DirectoryOrder(
                    order=order+4,
                    directory="selfie",
                )

            if IosTags.DESCRIPTION.value in metadata:
                extracted_data["description"] = DirectoryOrder(
                    order=order+3,
                    directory="foreign",
                )

            return extracted_data

        except Exception as e:
            print(f"Error extracting EXIF data from video bytes: {e}")
            return {
                "year": DirectoryOrder(
                    order=order+1, directory=f"{datetime.now().year}_no_exif"
                )
            }

    def get_device_id(self):
        return self.lock_down.all_values.get("UniqueDeviceID")

    def get_device_model(self):
        return self.lock_down.all_values.get("ProductType")

    def get_device_type(self):
        return "iPhone"
