import hashlib
import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
import re
import pickle
from datetime import date
from pillow_heif import register_heif_opener
import ffmpeg


image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.heic', '.jpg')
video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mov', '.mp4' )


# Function to check if a file is a media file based on its extension
def is_media_file(filename):
    return filename.lower().endswith(image_extensions + video_extensions)

def is_image_file(filename):
    return filename.lower().endswith(image_extensions)

def is_video_file(filename):    
    return filename.lower().endswith(video_extensions)

def is_HEIC_file(filename):
    return filename.lower().endswith('.heic') or filename.lower().endswith('.heif')
    
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()

def getParentDirectory(file_path):
    return os.path.basename(os.path.dirname(file_path))

def convert_to_JPG(filename):
    base, ext = os.path.splitext(filename)
    return base + '.jpg' if ext.lower() == '.heic' or ext.lower() == '.heif' else filename
    
# Desperate move to find the date in the file path if not found in metadata
def find_date_in_text(file_path):
    date_regex = r'\b\d{4}'
    dates = re.findall(date_regex, file_path)
    if (len(dates) > 0):
        found_date = dates[0]
        if found_date.startswith("20") or found_date.startswith("19"):
            return dates[0]
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
                print(f"EXIF Tag: {tag_name}, Value: {value}")
                if tag_name == 'DateTimeOriginal':
                    return find_date_in_text(value)
            print("")
        else:
            print(f"No EXIF data found for {file_path}")
            return find_date_in_text(file_path)

    
    except Exception as e:
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
            
        
        
    except Exception as e:
        return find_date_in_text(file_path)
        

# Function to calculate unique hash for a file used for deduplication
def calculate_hash(file_path):
    """Calculate the hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()