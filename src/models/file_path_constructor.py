import re
from pathlib import Path
from helper.file_helper_functions import find_date_in_text
from models.dataclass.data_class import DirectoryOrder, DirectoryOrderConfig
from models.devices.iPhone.metadata_extractor import MetaDataExtractor
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
            
        sorted_dirs = {}
        
        dir_parent = self.get_dir_parent(file_info.source_path)
        if dir_parent is not None and device is None:
            sorted_dirs[dir_parent.directory] = dir_parent

        exif_dirs = await self.add_relevant_exif_data(
            file_info.source_path, device)
        if exif_dirs:
            sorted_dirs.update(exif_dirs)

        sorted_dirs = dict(
            sorted(sorted_dirs.items(), key=lambda item: item[1].order)
        )

        return device_name + "/".join(
            str(d.directory).strip("/") for d in sorted_dirs.values()
            if d is not None and d.directory
        )

    async def construct_destination_path(self,
                                         file_info, device: Device) -> str:

        dir_name = await self.resolve_directory(file_info, device)

        destination_path = Path(dir_name)

        return str(destination_path)

    async def add_relevant_exif_data(self, source_path,  device: Device):
        if device is not None:
            return await device.get_exif_from_media_file(
                source_path,
                self.directory_config
            )
        else:
            metadata_extractor = MetaDataExtractor(device=None)
            return await metadata_extractor.get_exif_from_media_file(
                source_path,
                self.directory_config
            )
            
    def get_dir_parent(self, source_path):
        if (len(Path(source_path).parents) <= 1):
            return None
        
        dir_parent = Path(source_path).parent.name
        date = find_date_in_text(dir_parent)
        
        if (date is not None):
            date_str = str(date)
            dir_parent_without_date = dir_parent.replace(date_str, "")
            
            if re.search(r"[A-Za-z]{3,}", dir_parent_without_date):
                dir_parent = dir_parent_without_date.replace(" ", "_").replace("-", "_").replace(":", "_").replace(".", "_").lower().strip("_")
                return DirectoryOrder(
                    directory=dir_parent,
                    order=3
                )
            return None
        return None