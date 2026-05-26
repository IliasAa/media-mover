from ast import List
import asyncio
from models.devices import DeviceDetector
from models.devices.device import Device
from screens.export.export_screen import ExportScreen
from models.file_transfer.file_transfer import FileTransferManager


class ExportController:
    def __init__(self, master, fileTransferManager: FileTransferManager,
                 async_loop: asyncio.AbstractEventLoop):
        self.subject = fileTransferManager
        self.async_loop = async_loop
        self.detector = DeviceDetector()
        self.devices = []
        self.show_export_screen(master)
        self._progress_lock = asyncio.Lock()
        # Register the ExportScreen as an observer to the FileTransferManager
        self.subject.attach(self.my_frame)
        # self.check_for_connected_devices()

    def show_export_screen(self, master):
        '''Display the export screen on the main application window'''
        self.my_frame = ExportScreen(master=master, controller=self)
        self.my_frame.grid(row=0,
                           column=1,
                           columnspan=2,
                           rowspan=2,
                           sticky="nsew",
                           padx=10, pady=10)

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

    async def start_progress_safe(self):
        async with self._progress_lock:
            await self.start_progress()

    def clear_progress(self):
        self.subject.clear_progress()

    async def save_progress(self):
        await self.subject.create_and_copy_to_folder()

    def set_from_directory(self, from_directory):
        '''Set the source directory for file transfer'''
        self.subject.from_directory = from_directory

    def set_to_directory(self, to_directory):
        '''Set the destination directory for file transfer'''
        self.subject.to_directory = to_directory

    def toggle_blurry(self):
        self.subject.filter_blurry = not self.subject.filter_blurry

    def toggle_date_folders(self):
        self.subject.create_date_folders = not self.subject.create_date_folders

    def toggle_lookalikes(self):
        self.subject.filter_lookalikes = not self.subject.filter_lookalikes

    def toggle_hashes(self):
        self.subject.save_hashes = not self.subject.save_hashes
