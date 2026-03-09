from devices.iphone import IphoneDevice


class DeviceFactory:

    @staticmethod
    def create_iphone(raw_device):
        return IphoneDevice(
            udid=raw_device.serial,
            connection_type=getattr(raw_device, "connection_type", "usb")
        )
