import gc
import hashlib
import json
import os
import re
from collections import defaultdict
import subprocess
import threading

import ffmpeg
from PIL import Image
from PIL.ExifTags import TAGS

from models.dataclass.data_class import FileInfo

image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.heic', '.jpg')
video_extensions = ('.mp4',
                    '.avi',
                    '.mov',
                    '.mkv',
                    '.flv',
                    '.wmv',
                    '.mov',
                    '.mp4',
                    '.hevc')


# Function to check if a file is a media file based on its extension
def is_media_file(filename):
    return filename.lower().endswith(image_extensions + video_extensions)


def is_image_file(filename):
    return filename.lower().endswith(image_extensions)


def is_video_file(filename):
    return filename.lower().endswith(video_extensions)


def is_HEIC_file(filename):
    return filename.lower().endswith('.heic') or filename.lower().endswith(
        '.heif')


def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()


def get_parent_directory(file_path):
    return os.path.basename(os.path.dirname(file_path))


def convert_to_JPG(filename):
    base, ext = os.path.splitext(filename)
    return base + '.jpg' if ext.lower() == '.heic' or \
        ext.lower() == '.heif' else filename


# Desperate move to find the date in the file path if not found in metadata
def find_date_in_text(file_path):
    date_regex = r'\b\d{4}'
    dates = re.findall(date_regex, file_path)
    if (len(dates) > 0):
        found_date = dates[0]
        if found_date.startswith("20") or found_date.startswith("19"):
            return int(dates[0])
    return None  # Return current year if no date found


# Function to get the date from the image metadata or file path
def get_image_date(file_path):
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            print(f"EXIF data for {file_path}:")
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                # print(f"EXIF Tag: {tag_name}, Value: {value}")
                if tag_name == 'DateTime' or tag_name == 'DateTimeOriginal':
                    return find_date_in_text(value)
            print("")
        else:
            print(f"No EXIF data found for {file_path}")
            return find_date_in_text(file_path)

    except Exception:
        # Find all matches in the text
        return find_date_in_text(file_path)


def get_video_date(file_path):
    try:
        metadata = ffmpeg.probe(file_path)
        streams = metadata.get("streams", [])

        for stream in streams:
            tags = stream.get("tags", {})
            if "creation_time" in tags:
                return find_date_in_text(tags["creation_time"])

        return find_date_in_text(file_path)

    except Exception:
        return find_date_in_text(file_path)


# Function to calculate unique hash for a file used for deduplication
def calculate_hash(file_path):
    """Calculate the hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_hash_for_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_generator_text(collected_files: dict[str, 'FileInfo'], to_directory: str, total_items: int) -> str:
    """
    Generate a text-based tree for collected files.

    collected_files: dict mapping source_path -> FileInfo
    to_directory: base directory name for the tree
    total_items: total number of items processed
    """
    if not collected_files:
        return "No files are processed."
    tree_text = f"{total_items} amount of files to be processed:\n"
    tree_text += f"{len(collected_files)} files processed:\n"
    tree_text += f"📂{to_directory}\n"
    dict_tree = defaultdict(list)

    print(f"Generating tree for {len(collected_files)} files.")

    # Build nested dict structure
    for source_path, file_info in collected_files.items():
        constructed_path = file_info.constructed_path or "unknown_path"
        normalized_path = os.path.normpath(constructed_path)
        path_parts = normalized_path.split(os.sep)

        current_dict = dict_tree
        for part in path_parts:
            if is_media_file(part):
                # Stop descending at the file itself
                break
            if part not in current_dict:
                current_dict[part] = {}
            current_dict = current_dict[part]

        # Add the filename at the leaf
        current_dict[file_info.filename] = {}

    # Recursive function to build text
    def recurse(d: dict, prefix=""):
        lines = []
        for i, (key, subdict) in enumerate(sorted(d.items())):
            connector = "└─ " if i == len(d) - 1 else "├─ "
            if subdict:  # Directory
                lines.append(f"{prefix}{connector}📂{key}")
                extension = "    " if i == len(d) - 1 else "│   "
                lines.extend(recurse(subdict, prefix + extension))
            else:  # File
                lines.append(f"{prefix}{connector}📄{key}")
        return lines

    tree_lines = recurse(dict_tree)
    tree_text += "\n".join(tree_lines)
    return tree_text


TAGS_NEEDED = [
    "-Model",
    "-LensModel",
    "-Description",
    "-UserComment",
    "-Author",
    "-DateTimeOriginal",
    "-CreateDate",
    "-ModifyDate",
    "-FileModifyDate",
    "-FileAccessDate",
]


def modify_image_metadata(image_bytes: bytes) -> dict:
    result = subprocess.run(
        ["exiftool", "-j", *TAGS_NEEDED, "-"],
        input=image_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    data = json.loads(result.stdout)
    del result  # Free memory immediately after use
    gc.collect()
    if not data:
        return {}

    return data[0]


def modify_image_metadata_from_file(file_path: str) -> dict:
    result = subprocess.run(
        ["exiftool", "-j", *TAGS_NEEDED, file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    data = json.loads(result.stdout)
    del result  # Free memory immediately after use
    gc.collect()
    if not data:
        return {}

    return data[0]


class ExifToolProcess:
    """Stay-open exiftool singleton. One process shared across all files."""
    _instance = None
    _class_lock = threading.Lock()

    def __init__(self):
        self._proc = subprocess.Popen(
            ["exiftool", "-stay_open", "True", "-@", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self._lock = threading.Lock()

    @classmethod
    def get(cls) -> "ExifToolProcess":
        with cls._class_lock:
            if cls._instance is None or cls._instance._proc.poll() is not None:
                cls._instance = cls()
        return cls._instance

    def extract(self, file_path: str) -> dict:
        cmd = (
            "\n".join(TAGS_NEEDED)
            + f"\n-j\n{file_path}\n-execute\n"
        )
        with self._lock:
            self._proc.stdin.write(cmd.encode())
            self._proc.stdin.flush()
            lines = []
            while True:
                line = self._proc.stdout.readline().decode(errors="replace")
                if "{ready}" in line:
                    break
                lines.append(line)
        raw = "".join(lines).strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            return data[0] if data else {}
        except json.JSONDecodeError:
            return {}

    def close(self):
        try:
            self._proc.stdin.write(b"-stay_open\nFalse\n")
            self._proc.stdin.flush()
            self._proc.wait(timeout=5)
        except Exception:
            self._proc.kill()


def extract_metadata_fast(file_path: str) -> dict:
    """Extract EXIF metadata using the shared stay-open exiftool process."""
    return ExifToolProcess.get().extract(file_path)
