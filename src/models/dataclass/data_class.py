from dataclasses import dataclass
import enum

from models.devices.device import Device


class Directory(enum.Enum):
    YEAR = "year"
    DEVICE = "device"
    MODEL = "model"
    LOCATION = "location"
    SCREENSHOT = "screenshot"
    SCREEN_RECORDING = "screen_recording"
    FOREIGN = "foreign"
    SELFIE = "selfie"
    NO_DATA = "no_data"


@dataclass
class DirectoryOrderConfig:
    directories_orders: list[DirectoryOrder]
    with_device_folders: bool = False
    with_date_folders: bool = True
    directories_neglected: list[Directory] = None


@dataclass
class DirectoryOrder:
    order: int
    directory: Directory = None
    exif_tags: dict[str, list[str]] = None


@dataclass
class FileInfo:
    source_path: str
    filename: str
    year: int
    device: Device
    constructed_path: str = None
