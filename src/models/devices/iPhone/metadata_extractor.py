from datetime import datetime
from enum import Enum
import gc
import os
import tempfile

from helper.exif_tool_process import extract_metadata_fast
from helper.file_helper_functions import find_date_in_text, is_image_file
from models.dataclass.data_class import DirectoryOrder, DirectoryOrderConfig


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

MAX_IMAGE_BYTES = 512 * 1024
MAX_VIDEO_BYTES = 2 * 1024 * 1024


class MetaDataExtractor:
    def __init__(self, device):
        self.device = device

    def _is_empty_value(self, value) -> bool:
        """Check if a value is empty or should be ignored."""
        if value is None:
            return True
        empty_values = ("", "none", "null")
        return str(value).strip().lower() in empty_values

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

    def get_partial_file_from_local(self, source_path: str, partial_bytes: int) -> bytes:
        """Extract partial file data from local file system."""
        try:
            with open(source_path, 'rb') as f:
                return f.read(partial_bytes)
        except Exception as e:
            print(f"Error reading partial file from local: {e}")
            return None
    def extract_metadata_from_local(self, source_path: str) -> dict:
        return extract_metadata_fast(source_path)

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

    async def _extract_metadata_with_fallback(self,
                                              source_path: str,
                                              partial_bytes: int) -> dict:
        if self.device is None:
            partial_data = self.get_partial_file_from_local(source_path, partial_bytes)
        else:
            partial_data = await self.device.get_partial_file(source_path,
                                                          partial_bytes)

        if partial_data is None:
            raise ValueError("No data returned for metadata extraction")

        metadata = self._extract_metadata_from_bytes(source_path, partial_data)
        del partial_data

        if self._has_embedded_date(metadata) and self._has_contextual_metadata(
            metadata
        ):
            return metadata

        if self.device is None:
            full_metadata = self.extract_metadata_from_local(source_path)
        else:
            full_metadata = await self.device._extract_metadata_from_device_file(
                source_path,
            )
    
        if full_metadata:
            return full_metadata
        return metadata

    def _extract_year_metadata(self, metadata: dict, order: int) -> dict:
        """Extract year from metadata with date key prioritization."""
        found_date = False
        extracted_data = {}

        for key in DATE_KEYS:
            if key in metadata:
                year = find_date_in_text(metadata[key])
                if year is None:
                    continue

                # If the modified date it is probably foreign
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

        return extracted_data

    def _extract_model_metadata(self, metadata: dict, order: int) -> dict:
        """Extract model from metadata."""
        extracted_data = {}

        if IosTags.MODEL.value in metadata:
            model_value = str(metadata[IosTags.MODEL.value]).strip(
                ).lower().replace(" ", "_")
            extracted_data["model"] = DirectoryOrder(
                order=order+2,
                directory=model_value
            )

        return extracted_data

    def extract_metadata_new():
        pass

    async def get_exif_from_media_file(
            self, source_path,
            directory_order_config: DirectoryOrderConfig) -> dict:
        """
        Extract relevant EXIF tags as DirectoryOrder objects.
        Keys: EXIF tag names
        Values: DirectoryOrder(order, value)
        """
        try:
            if is_image_file(source_path):
                metadata = await self._extract_metadata_with_fallback(
                    source_path,
                    MAX_IMAGE_BYTES,
                )
            else:
                metadata = await self._extract_metadata_with_fallback(
                    source_path,
                    MAX_VIDEO_BYTES,
                )
            gc.collect()
            extracted_data = {}
            if directory_order_config.with_date_folders:
                extracted_data.update(
                    self._extract_year_metadata(metadata, 1))

            if directory_order_config.with_device_folders:
                extracted_data.update(
                    self._extract_model_metadata(metadata, 2))

            for directory_order in directory_order_config.directories_orders:
                for exif_tag, expected_values in (
                    directory_order.exif_tags.items()
                ):
                    if exif_tag in metadata:
                        value = str(metadata[exif_tag]).strip().lower()
                        if any(v.lower() in value for v in expected_values):
                            directory_name = directory_order.directory
                            extracted_data[directory_name] = DirectoryOrder(
                                order=directory_order.order,
                                directory=directory_name,
                            )
            return extracted_data

        except Exception as e:
            print(f"Error extracting EXIF data from image bytes: {e}")
            return {
                "year": DirectoryOrder(
                    order=1, directory=f"{datetime.now().year}_no_exif"
                )
            }
