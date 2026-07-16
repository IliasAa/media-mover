import subprocess
import json


def modify_image_metadata(image_bytes: bytes):
    result = subprocess.run(
        ["exiftool", "-ee", "-j", "-"],
        input=image_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    data = json.loads(result.stdout)
    print(json.dumps(data, indent=2))

    return data
