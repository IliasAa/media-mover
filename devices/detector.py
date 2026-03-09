from pymobiledevice3.usbmux import list_devices
from devices.factory import DeviceFactory


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

        for raw_device in raw_devices:
            device = DeviceFactory.create_iphone(raw_device)
            devices.append(device)

        return devices

    async def detect_android(self):
        # placeholder for future ADB detection
        return []
