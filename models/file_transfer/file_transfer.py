from ast import List
import os
import shutil
from helper.file_helper_functions import (
    is_media_file,
    is_image_file,
    is_video_file,
    get_parent_directory,
    get_image_date,
    calculate_hash,
    is_HEIC_file,
)
import concurrent.futures
from datetime import date
from screens.observer import Observer
from models.subject import Subject


class FileTransferManager(Subject):
    _observers: List[Observer] = []
    collected_files: dict = {}
    collected_duplicates: dict = {}
    date_register: dict = {}
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

    def start_progress(self):
        if (self.from_directory and self.to_directory):
            self.collect_all_media_from_directory(self.from_directory)
            # self.notify()
            self.add_date_name(self.collected_files)
            self.handle_no_date_files()
            # self.create_and_copy_to_folder()
            self.notify()
            self.heic_files = dict(filter(
                lambda item: self.is_heic_image(item),
                self.collected_files.items()))

            self.non_heic_files = dict(filter(
                lambda item: not self.is_heic_image(item),
                self.collected_files.items()))

    def collect_all_media_from_directory(self, root):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for root_dir, dirs, files in os.walk(self.from_directory):
                for filename in files:
                    futures.append(
                        executor.submit(self.process_file, root_dir, filename))
            concurrent.futures.wait(futures)

    def process_file(self, root, filename):
        if is_media_file(filename):
            file_path = os.path.join(root, filename)
            file_hash = calculate_hash(file_path)

            if file_hash not in self.hash_set_photos:
                self.hash_set_photos.add(file_hash)

                if is_image_file(filename):
                    self.amount_of_photos_collected += 1
                    # Separate the heic from other file types.
                    target_dict = (
                        self.heic_files if is_HEIC_file(filename)
                        else self.collected_files
                    )
                    file_info = [
                        filename,
                        get_parent_directory(file_path)
                    ]
                    target_dict[file_path] = file_info
                elif is_video_file(filename):
                    self.amount_of_videos_collected += 1
                    print(f"Collected video: {file_path}")
                    file_info = [
                        filename,
                        get_parent_directory(file_path)
                    ]
                    self.collected_files[file_path] = file_info

            else:
                self.amount_of_duplicates += 1
                file_info = [
                    filename,
                    get_parent_directory(file_path)
                ]
                self.collected_duplicates[file_path] = file_info

    def add_date_name(self, files_dict):
        for origin_path, info in files_dict.items():
            date = get_image_date(origin_path)
            parent_directory = info[1]

            # Register date for parent directory if not already set
            if parent_directory not in self.date_register and date is not None:
                self.date_register[parent_directory] = date
            # Handle files with no date
            if date:
                self.collected_files.setdefault(origin_path, info).append(date)
            else:
                parent_date = self.date_register.get(parent_directory)
                if parent_date is None:
                    self.no_date_files.append(origin_path)
                else:
                    file_entry = self.collected_files.setdefault(
                        origin_path, info
                    )
                    file_entry.append(parent_date)

    def handle_no_date_files(self):
        for file_path in self.no_date_files:
            item = self.collected_files.get(file_path)
            date_registered = self.date_register.get(item[1])
            if (date_registered is not None):
                self.collected_files[file_path].append(date_registered)
            else:
                date_now = date.today().year
                self.collected_files[file_path].append(date_now)

    def create_and_copy_to_folder(self):
        for file_path, info in self.collected_files.items():
            date = str(info[2])
            parent_path = os.path.join(self.to_directory, date, self.root)
            self.progress += 1
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)

            try:
                file_name = info[0]
                new_file_path = os.path.join(parent_path, file_name)
                self.items.append(new_file_path)
                shutil.copy2(file_path, new_file_path)
                # print(f"Copied {file_name} to {parent_path}")
            except Exception as e:
                print(f"Error copying {file_name}: {e}")

    def is_heic_image(self, extension):
        return is_HEIC_file(extension[0])
