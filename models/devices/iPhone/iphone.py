import os
import tempfile

from pillow_heif import register_heif_opener
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.afc import AfcService

from helper.exif_tool_process import extract_metadata_fast
from helper.file_helper_functions import (
    is_media_file,
    is_video_file,
)

from models.dataclass.data_class import DirectoryOrderConfig
from models.devices import Device
from models.devices.device_type import DeviceType
from models.devices.iPhone.metadata_extractor import MetaDataExtractor

MEDIA_FOLDER = "/DCIM"


class IphoneDevice(Device):
    def __init__(self, udid: str, connection_type: str = "usb"):
        self.type = DeviceType.IOS
        self.udid = udid
        self.connection_type = connection_type
        self.lock_down = None
        self.registered_paths = []
        self.metadata_extractor = MetaDataExtractor(device=self)
        self.unique_names = set()
        self._afc_cache = None  # Persistent AFC connection for file transfers
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

        length = 0
        for folder in folders:
            files_in_folder = await afc.listdir(
                f"{MEDIA_FOLDER}/{folder}"
            )
            length += len(files_in_folder)

            for f in files_in_folder:
                if not is_media_file(f):
                    print(f"Skipping non-media file: {f}")
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
        print(f"Total media files found on device {self.get_device_name()}: {length}")
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
        # Reuse cached AFC connection to avoid expensive new connections per file
        if self._afc_cache is None:
            self._afc_cache = await self.open_afc()
        
        try:
            await self._afc_cache.pull(
                source_path,
                destination_path,
                progress_bar=False,
            )
        except Exception as e:
            print(f"Error copying {source_path} to {destination_path}: {e}")
            # On connection error, close cached connection and retry with fresh one
            try:
                self._afc_cache = None
                afc = await self.open_afc()
                await afc.pull(
                    source_path,
                    destination_path,
                    progress_bar=False,
                )
            except Exception as retry_e:
                print(f"Retry failed for {source_path}: {retry_e}")
                raise

    def get_device_name(self):
        return self.lock_down.all_values.get("DeviceName")

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

    def get_exif_from_image(self, data: bytes, order: int = 1) -> dict:
        return self.metadata_extractor.get_exif_from_image(data, order)

    def get_exif_from_video(self, data: bytes, order: int = 1) -> dict:
        return self.metadata_extractor.get_exif_from_video(data, order)

    def get_exif_from_media_file(self,
                                 source_path,
                                 directory_order_config: DirectoryOrderConfig):
        return self.metadata_extractor.get_exif_from_media_file(
            source_path, directory_order_config
        )

    def get_device_id(self):
        return self.lock_down.all_values.get("UniqueDeviceID")

    def get_device_model(self):
        return self.lock_down.all_values.get("ProductType")

    def get_device_type(self):
        return "iPhone"

    def cleanup_afc_cache(self):
        """Close the cached AFC connection after export is complete."""
        self._afc_cache = None
