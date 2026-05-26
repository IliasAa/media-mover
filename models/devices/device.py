from abc import ABC, abstractmethod


class Device(ABC):

    def __init__(self, udid: str, connection_type: str = "usb"):
        self.type = None
        self.udid = udid
        self.connection_type = connection_type
        self.registered_paths = []

    """
    The Device interface declares a set of methods for managing devices.
    """
    @abstractmethod
    async def connect(self):
        """
        Connect to the device. This method should be implemented by concrete
        device classes to establish a connection and prepare for file
        retrieval.
        """

    @abstractmethod
    def get_device_name(self):
        """
        Get the name of the device.
        """

    @abstractmethod
    async def get_all_files(self):
        """
        Get all files from the device.
        """

    @abstractmethod
    async def get_file_content(self, file_path):
        """
        Get the content of a specific file from the device.
        """

    @abstractmethod
    async def copy_file_to_path(self, source_path: str, destination_path: str):
        """
        Copy a file from the device to a local destination path.
        """

    @abstractmethod
    def get_device_id(self):
        """
        Get the unique identifier of the device.
        """

    @abstractmethod
    def get_device_type(self):
        """
        Get the type of the device.
        """

    # Do not know if other devices use same metadata retrieval methods
    # iPhones, can move to IphoneDevice if needed.
    @abstractmethod
    async def get_exif_from_image(self, data: bytes, order: int = 1) -> dict:
        """
        Get the EXIF data from an image file on the device.
        """

    @abstractmethod
    async def get_exif_from_video(self, data: bytes, order: int = 1) -> dict:
        """
        Get the metadata from a video file on the device.
        """
