import asyncio
import threading

from models.devices import DeviceDetector
from models.source_scanner.source_scanner import SourceScanner
from screens.export.export_screen import ExportScreen
from models.file_transfer.file_transfer import FileTransferManager


class ExportController:
    def __init__(self, master, fileTransferManager: FileTransferManager):
        self.subject = fileTransferManager
        self.detector = DeviceDetector()
        self.scanner = SourceScanner(source_path="")
        self.devices = []
        self.show_export_screen(master)
        # Register the ExportScreen as an observer to the FileTransferManager
        self.subject.attach(self.my_frame)

    def _run_in_thread(self, coro_func, *args):
        """Run an async method in an isolated background thread."""
        def thread_target():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(coro_func(*args))
            finally:
                loop.close()

        threading.Thread(target=thread_target, daemon=True).start()

    def show_export_screen(self, master):
        '''Display the export screen on the main application window'''
        self.my_frame = ExportScreen(master=master, controller=self)
        self.my_frame.grid(row=0,
                           column=1,
                           columnspan=2,
                           rowspan=2,
                           sticky="nsew",
                           padx=10, pady=10)

    def start_progress_safe(self):
        self._run_in_thread(self.start_progress)

    def check_for_connected_devices_safe(self):
        self._run_in_thread(self.check_for_connected_devices)

    def save_progress_safe(self):
        self._run_in_thread(self.save_progress)    

    async def check_for_connected_devices(self):
        '''Check for connected devices and update the export screen
        accordingly'''
        try:
            detected_devices = await self.detector.detect()
            for device in detected_devices:
                await device.connect()
                if (
                    device.get_device_name()
                    not in self.get_all_device_names()
                ):
                    await device.get_all_files()
                    self.devices.append(device)

            self.my_frame.after(0, self.my_frame.set_found_devices)
        except Exception as e:
            print(f"Error detecting devices: {e}")

    def get_all_device_names(self):
        '''Return a list of all detected device names'''
        return [device.get_device_name() for device in self.devices]

    async def start_progress(self):
        await self.subject.start_progress(self.devices)

    def clear_progress(self):
        self.subject.clear_progress()
        
    def scan_progress_safe(self):
        '''Scan the source directory for media files and update the export screen'''
        def thread_target():
            self.scanner.source_path = self.subject.to_directory
            self.scanner.scan()
            self.subject.hash_set = self.scanner.files
            print(f"Scanned {len(self.subject.hash_set)} files in the source directory.")
        
        threading.Thread(target=thread_target, daemon=True).start()

    def scan_progress(self):
        '''Scan the source directory for media files and update the export screen'''
        self.scan_progress_safe()

    async def save_progress(self):
        await self.subject.create_and_copy_to_folder()

    def set_from_directory(self, from_directory):
        '''Set the source directory for file transfer'''
        self.subject.from_directory = from_directory

    def set_to_directory(self, to_directory):
        '''Set the destination directory for file transfer'''
        self.subject.to_directory = to_directory
        self.scanner.source_path = to_directory
        self.subject.hash_set = self.scanner.get_hash_file()

    def toggle_blurry(self):
        self.subject.filter_blurry = not self.subject.filter_blurry

    def toggle_date_folders(self):
        self.subject.create_date_folders = (
            not self.subject.create_date_folders
        )

    def toggle_lookalikes(self):
        self.subject.filter_lookalikes = not self.subject.filter_lookalikes

    def toggle_hashes(self):
        self.subject.save_hashes = not self.subject.save_hashes
