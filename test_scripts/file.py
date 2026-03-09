import asyncio
from pymobiledevice3.lockdown import create_using_usbmux


async def main():
    lockdown = await create_using_usbmux()
    print(lockdown.all_values.get("DeviceName"))

asyncio.run(main())
# async def main():
#     lockdown = await create_using_usbmux()
#     afc = AfcService(lockdown)

#     folders = await afc.listdir("/DCIM")

#     for folder in folders:
#         files = await afc.listdir(f"/DCIM/{folder}")
#         for f in files:
#             print(f"/DCIM/{folder}/{f}")
#     data = await afc.get_file_contents("/DCIM/100APPLE/IMG_0621.HEIC")

#     with open("IMG_0621.HEIC", "wb") as f:
#         f.write(data)

# asyncio.run(main())
