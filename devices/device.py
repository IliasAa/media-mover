from abc import ABC, abstractmethod


class Device(ABC):
    """
    The Device interface declares a set of methods for managing devices.
    """

    @abstractmethod
    def get_device_name(self):
        """
        Get the name of the device.
        """
        pass

    @abstractmethod
    def get_all_files(self):
        """
        Get all files from the device.
        """
        pass

    @abstractmethod
    def get_device_id(self):
        """
        Get the unique identifier of the device.
        """
        pass

    @abstractmethod
    def get_device_type(self):
        """
        Get the type of the device.
        """
        pass
