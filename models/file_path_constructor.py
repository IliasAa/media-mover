from pathlib import Path
from models.dataclass.data_class import DirectoryOrderConfig
from models.devices import Device


class FilePathConstructor:
    def __init__(self, device_id: str,
                 directory_config: DirectoryOrderConfig):

        self.device_id = device_id
        self.directory_config = directory_config

    async def resolve_directory(self,
                                file_info,
                                device: Device):
        device_name = ""
        # This one handles the case where no directories are specified,
        # but device folders are enabled
        if (self.directory_config.with_device_folders):
            device_name = (device.get_device_name().replace(
                " ", "_").lower() or "unknown_device") + "/"

        sorted_dirs = await self.add_relevant_exif_data(
            file_info.source_path, device)

        return device_name + "/".join(
            d.directory for d in sorted_dirs.values())

    async def construct_destination_path(self,
                                         file_info, device: Device) -> str:

        dir_name = await self.resolve_directory(file_info, device)

        # Build path safely
        destination_path = Path(dir_name)

        return str(destination_path)

    async def add_relevant_exif_data(self, source_path,  device: Device):
        if device is not None:
            return await device.get_exif_from_media_file(
                source_path,
                self.directory_config
            )

        return None
