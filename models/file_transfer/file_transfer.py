from ast import List
import gc
from io import BytesIO
import os
import shutil

from models.dataclass.data_class import FileInfo
from models.devices import Device
from helper.file_helper_functions import (
    is_media_file,
    is_image_file,
    is_video_file,
    calculate_hash,
)
import concurrent.futures
from models.file_path import FilePathConstructor, DirectoryOrder
from screens.observer import Observer
from models.subject import Subject

order = [
    DirectoryOrder(
        directory="device", order=1),
    DirectoryOrder(
        directory="exif_data", order=2),
]


class FileTransferManager(Subject):
    _observers: List[Observer] = []
    collected_files: dict = {}
    collected_duplicates: dict = {}
    date_register: dict = {}
    amount_of_files_collected: int = 0
    amount_of_photos_collected: int = 0
    amount_of_videos_collected: int = 0
    amount_of_duplicates: int = 0
    hash_set_photos: set = set()
    no_date_files: list = []
    items: list = []
    heic_files: dict = {}
    non_heic_files: dict = {}
    progress: int = 0
    filter_blurry: bool = False
    filter_lookalikes: bool = False
    create_date_folders: bool = False
    save_hashes: bool = False
    from_directory: str = ""
    to_directory: str = ""
    path_constructor: FilePathConstructor = None

    def __init__(self):
        self.root = os.path.basename(self.from_directory)

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    """
    The subscription management methods.
    """

    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """
        for observer in self._observers:
            observer.update(self)

    def clear_progress(self):
        self.collected_files = {}
        self.collected_duplicates = {}
        self.date_register = {}
        self.amount_of_photos_collected = 0
        self.amount_of_videos_collected = 0
        self.amount_of_duplicates = 0
        self.hash_set_photos = set()
        self.no_date_files = []
        self.items = []
        self.heic_files = {}
        self.non_heic_files = {}
        self.progress = 0
        self.filter_blurry = False
        self.filter_lookalikes = False
        self.create_date_folders = False
        self.save_hashes = False
        self.from_directory = ""
        self.to_directory = ""
        self.notify()

    async def start_progress(self, devices: List[Device]):
        if (
            self.from_directory and self.to_directory
            or len(devices) > 0
        ):
            for device in devices:
                await self.collect_all_media_from_device(device)
            self.collect_all_media_from_directory()
            # self.notify()

    async def collect_all_media_from_device(self, device: Device):
        try:
            self.path_constructor = FilePathConstructor(
                device_id=device.get_device_id(),
                order_of_directories=order
            )
            count = 0
            self.amount_of_files_collected += len(device.registered_paths)
            for path in device.registered_paths:
                await self.process_file_from_device(device, path)
                if count % 20 == 0:
                    self.notify()
                    gc.collect()
                count += 1
            self.notify()

        except Exception as e:
            print(f"Error collecting media from device "
                  f"{device.get_device_name()}: {e}")

    def collect_all_media_from_directory(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for root_dir, __, files in os.walk(self.from_directory):
                for filename in files:
                    futures.append(
                        executor.submit(self.process_file, root_dir, filename))
            concurrent.futures.wait(futures)

    async def process_file_from_device(self, device: Device, path: str):
        if is_media_file(path):
            if path not in self.collected_files:
                if is_image_file(path):
                    self.amount_of_photos_collected += 1
                    file_info = FileInfo(
                        source_path=path,
                        filename=os.path.basename(path),
                        year=None,
                        device=device
                    )
                    file_info.constructed_path = (
                        await self.path_constructor
                        .construct_destination_path(
                            file_info,
                            device
                        )
                    )
                    self.collected_files[path] = file_info
                elif is_video_file(path):
                    self.amount_of_videos_collected += 1
                    file_info = FileInfo(
                        source_path=path,
                        filename=os.path.basename(path),
                        year=None,
                        device=device
                    )
                    file_info.constructed_path = (
                        await self.path_constructor
                        .construct_destination_path(
                            file_info, device
                        )
                    )
                    self.collected_files[path] = file_info

    def process_file(self, root, filename, device=None):
        if is_media_file(filename):
            file_path = os.path.join(root, filename)
            file_hash = calculate_hash(file_path)

            if file_hash not in self.hash_set_photos:
                self.hash_set_photos.add(file_hash)
                if is_image_file(filename):
                    self.amount_of_photos_collected += 1
                    # Separate the heic from other file types.
                    file_info = FileInfo(
                        source_path=file_path,
                        filename=filename,
                        year=None,
                        device=device
                    )
                    self.collected_files[file_path] = file_info
                elif is_video_file(filename):
                    self.amount_of_videos_collected += 1
                    file_info = FileInfo(
                        source_path=file_path,
                        filename=filename,
                        year=None,
                        device=device
                    )
                    self.collected_files[file_path] = file_info

            else:
                self.amount_of_duplicates += 1
                file_info = FileInfo(
                    source_path=file_path,
                    filename=filename,
                    year=None,
                    device=device
                )
                self.collected_duplicates[file_path] = file_info

    async def create_and_copy_to_folder(self):
        if self.to_directory == "":
            print("No destination directory set. Skipping file copy.")
            return

        for file_path, info in self.collected_files.items():
            constructed_path = (
                self.to_directory + "/" + info.constructed_path
            )
            self.progress += 1
            if not os.path.exists(constructed_path):
                os.makedirs(constructed_path)

            device = info.device

            try:
                file_name = info.filename
                new_file_path = os.path.join(
                    constructed_path, file_name
                )
                if device is not None:
                    try:
                        file_bytes = (
                            await device.get_file_content(
                                info.source_path
                            )
                        )
                        file_bytes = BytesIO(file_bytes)
                        with open(new_file_path, "wb") as destination_file:
                            destination_file.write(file_bytes.read())
                    except RuntimeError as re:
                        print(f"Event loop error for {file_name}: {re}")
                        continue
                else:
                    shutil.copy2(file_path, new_file_path)
                # print(f"Copied {file_name} to {constructed_path}")
            except Exception as e:
                print(f"Error copying {file_name}: {e}")
