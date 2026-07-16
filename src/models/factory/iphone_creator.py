from models.devices import Device
from .device_creator import DeviceCreator
from models.devices.iPhone.iphone import IphoneDevice


class IphoneCreator(DeviceCreator):
    """
    Note that the signature of the method still uses the abstract product type,
    even though the concrete product is actually returned from the method. This
    way the Creator can stay independent of concrete product classes.
    """

    def factory_method(self, raw_device) -> Device:
        return IphoneDevice(
            udid=raw_device.serial,
            connection_type=getattr(raw_device, "connection_type", "usb")
        )
