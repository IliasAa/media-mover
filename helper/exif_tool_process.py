import subprocess
import threading
import json

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
