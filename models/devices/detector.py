from pymobiledevice3.usbmux import list_devices
from models.factory import DeviceCreator, IphoneCreator


class DeviceDetector:
    async def detect(self):
        devices = []

        # detect iPhones
        iphone_devices = await self.detect_iphone()
        devices.extend(iphone_devices)

        # detect Android
        android_devices = await self.detect_android()
        devices.extend(android_devices)

        return devices

    async def detect_iphone(self):
        raw_devices = await list_devices()
        devices = []
        creator = IphoneCreator()

        for raw_device in raw_devices:
            device = self.create_device(raw_device, creator)
            devices.append(device)

        return devices

    async def detect_android(self):
        # placeholder for future ADB detection
        return []

    def create_device(self, device, device_creator: DeviceCreator):
        self.creator = device_creator
        return self.creator.factory_method(device)
