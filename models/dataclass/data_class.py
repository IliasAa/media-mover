from dataclasses import dataclass
from models.devices import Device


@dataclass
class DirectoryOrder:
    directory: str
    order: int


@dataclass
class FileInfo:
    source_path: str
    filename: str
    year: int
    device: Device
    constructed_path: str = None
