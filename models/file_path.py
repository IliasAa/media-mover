from pathlib import Path
from helper.file_helper_functions import is_image_file, is_video_file
from models.dataclass.data_class import DirectoryOrder
from models.devices import Device


class FilePathConstructor:
    def __init__(self, device_id: str,
                 order_of_directories: list[DirectoryOrder]):
        self.device_id = device_id
        self.order_of_directories = order_of_directories

    async def resolve_directory(self, dir_key: str, file_info):
        if dir_key == "device":
            return file_info.device.get_device_name().replace(" ", "_").lower() or "unknown_device"
        if dir_key == "exif_data":
            sorted_dirs = await self.add_relevant_exif_data(file_info.source_path, file_info.device)
            # Combine into a single path string or multiple directories
            return "/".join(d.directory for d in sorted_dirs)

        return dir_key

    async def construct_destination_path(self, file_info) -> str:
        self.dirs_in_order = []

        for d in self.order_of_directories:
            dir_name = await self.resolve_directory(d.directory, file_info)
            self.dirs_in_order.append((d.order, dir_name))
        # Sort by order
        self.dirs_in_order.sort(key=lambda x: x[0])

        print(f"Constructed directories in order: {self.dirs_in_order}")

        # Extract directory names only
        ordered_dirs = [d for _, d in self.dirs_in_order]

        # Build path safely
        destination_path = Path(*ordered_dirs)

        return str(destination_path)

    async def add_relevant_exif_data(self, source_path,  device: Device):
        if device is not None:
            if is_image_file(source_path):
                exif_dirs = await device.get_exif_from_image(source_path, order=1)
                # Sort by order dynamically
                return sorted(exif_dirs.values(), key=lambda x: x.order)

            elif is_video_file(source_path):
                exif_dirs = await device.get_exif_from_video(source_path, order=1)
                return sorted(exif_dirs.values(), key=lambda x: x.order)

        return None
