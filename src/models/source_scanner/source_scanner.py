import hashlib
import os
import pickle
from helper.file_helper_functions import (
    is_media_file
)

FILE_HASH_FILE = "progress.pkl"

class SourceScanner:
    def __init__(self, source_path):
        self.source_path = source_path
        self.files = self.get_hash_file()

    def scan(self):
        self.files = self.get_hash_file()
        """Scan the source path for media files."""
        for root, _, files in os.walk(self.source_path):
            for file in files:
                if is_media_file(file):
                    print(f"Found media file: {file}")
                    full_path = os.path.join(root, file)
                    identity = self.calculate_hash(full_path)
                    self.files.add(identity)
        
        self.save_hash_file(self.source_path, self.files)

    @staticmethod
    def calculate_hash(file_path):
        """Calculate quick identity for a file using size and first chunk."""
        try:
            stat = os.stat(file_path)
            file_size = stat.st_size
            hash_md5 = hashlib.md5()
            hash_md5.update(str(file_size).encode())
            with open(file_path, "rb") as f:
                chunk = f.read(8192)
                hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, IOError):
            return None
    
    @staticmethod
    def save_hash_file(source_path, files):
        """Save the hash file to the target path."""
        if not source_path:
            return
        hash_file_path = os.path.join(source_path, FILE_HASH_FILE)
        os.makedirs(source_path, exist_ok=True)
        with open(hash_file_path, "wb") as f:
            pickle.dump(files, f)
            
    def get_hash_file(self):
        """Get the path to the hash file."""
        hash_file_path = os.path.join(self.source_path, FILE_HASH_FILE)
        if os.path.exists(hash_file_path):
            with open(hash_file_path, "rb") as f:
                self.files = pickle.load(f)
                print(f"Loaded {len(self.files)} files from hash file.")
                return self.files
        return set()
        
    
