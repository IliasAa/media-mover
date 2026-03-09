from pymobiledevice3.lockdown import create_using_usbmux
from devices.device import Device


class IphoneDevice(Device):
    def __init__(self, udid: str, connection_type: str = "usb"):
        self.type = "iphone"
        self.udid = udid
        self.connection_type = connection_type
        self.lockdown = None

    def __repr__(self):
        return (
            f"IphoneDevice(udid={self.udid},"
            f"connection={self.connection_type})"
        )

    async def connect(self):
        self.lockdown = await create_using_usbmux(self.udid)

    def get_device_name(self):
        return self.lockdown.all_values.get("DeviceName")

    def get_all_files(self):
        return self.lockdown.all_values.get("MediaDirectory")

    def get_device_id(self):
        return self.lockdown.all_values.get("UniqueDeviceID")

    def get_device_type(self):
        return "iPhone"
