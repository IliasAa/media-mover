from pathlib import Path
from helper.file_helper_functions import get_video_date
from test_scripts.convert_HEIC_test import convert_single_file

src = Path("C:/Users/ilias/Desktop/from_dir")
dst = Path("C:/Users/ilias/Desktop/to_dir/2023/from_dir")

file_name = 'IMG_2707.HEIC'

file_path = src / file_name
new_file_path = dst / file_name.replace(".HEIC", ".jpg")

# Convert to string if needed
convert_single_file(str(file_path), str(new_file_path), 60)


