import os

from matplotlib.animation import FFMpegBase
from sympy import pprint
from helper.file_helper_functions import *
import concurrent.futures
from datetime import date
import ffmpeg

class FileTransferManager:
    def __init__(self, pos_vars, progressbar):
        self.pos_vars = pos_vars
        self.from_directory = "C:/Users/ilias/Desktop/from_dir"
        self.to_directory = "C:/Users/ilias/Desktop/to_dir"
        self.progressbar = progressbar
        self.root = os.path.basename(self.from_directory)
        
        self.amount_of_photos_collected = 0
        self.amount_of_videos_collected = 0
        self.amount_of_duplicates = 0
        
        # format is {origin_file_path: [filename, file_extension, parent_directory]}
        self.heic_files = {}
        self.collected_files = {}
        self.collected_duplicates = {}
        self.date_register = {}
        
        self.hash_set_photos = set()
        
        # List of files where the date could not be retrieved
        self.no_date_files = []
        

    def start_progress(self):
        # if (self.pos_vars['from_directory'].get() and 
        #     self.pos_vars['to_directory'].get()):
            
            self.progressbar.start()
            self.collectAllMediaFromDirectory(self.from_directory)
            self.addDateName(self.collected_files)
            self.handleNoDateFiles()
            print("Files sorted: ", self.date_register)
            for parent_dir, date in self.collected_files.items():
                print(f"Parent Directory: {parent_dir}, Date: {date}")
            for parent_dir, date in self.heic_files.items():
                print(f"Parent Directory: {parent_dir}, Date: {date}")
            self.createAndCopyToFolder()
            
            
            self.heic_files = dict(filter(lambda item: self.isHEICImage(item), self.collected_files.items()))
            self.non_heic_files = dict(filter(lambda item: not self.isHEICImage(item), self.collected_files.items()))
            
            
            
    def collectAllMediaFromDirectory(self, root):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for root_dir, dirs, files in os.walk(self.from_directory):
                for filename in files:
                    futures.append(executor.submit(self.processFile(root_dir, filename)))
            concurrent.futures.wait(futures)
        
                            

    def processFile(self, root, filename):
            if is_media_file(filename):
                           
                file_path = os.path.join(root, filename)
                file_hash = calculate_hash(file_path)
                
                if file_hash not in self.hash_set_photos:
                    self.hash_set_photos.add(file_hash)

                    if is_image_file(filename):
                        self.amount_of_photos_collected += 1
                        ## Separate the heic from other file types.
                        target_dict = self.heic_files if is_HEIC_file(filename) else self.collected_files
                        target_dict[file_path] = [filename, getParentDirectory(file_path)]
                    elif is_video_file(filename):
                        self.amount_of_videos_collected += 1
                        print(f"Collected video: {file_path}")
                        self.collected_files[file_path] = [filename, getParentDirectory(file_path)]

                else:
                    self.amount_of_duplicates += 1
                    self.collected_duplicates[file_path] = [filename, getParentDirectory(file_path)]

    
    def addDateName(self, files_dict):
        for origin_path, info in files_dict.items():
            date = get_image_date(origin_path)
            parent_directory = info[1]

            # Register date for parent directory if not already set
            if parent_directory not in self.date_register and date is not None:
                self.date_register[parent_directory] = date
                
            # Handle files with no date
            if date:
                self.collected_files.setdefault(origin_path, info).append(date)                     
            else:
                parent_date = self.date_register.get(parent_directory)
                if parent_date is None:
                    self.no_date_files.append(origin_path)
                else:
                    self.collected_files.setdefault(origin_path, info).append(parent_date)

    def handleNoDateFiles(self):
        for file_path in self.no_date_files:
            item = self.collected_files.get(file_path)
            date_registered = self.date_register.get(item[1])
            if (date_registered is not None):
                self.collected_files[file_path].append(date_registered)
            else:
                date_now = date.today().year
                self.collected_files[file_path].append(date_now)
        
    def createAndCopyToFolder(self):
        for file_path, info in self.collected_files.items():
            date = str(info[2])
            parent_path = os.path.join(self.to_directory, date, self.root)
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
           
            try:
                file_name = info[0]
                new_file_path = os.path.join(parent_path, file_name)
                shutil.copy2(file_path, new_file_path)
                print(f"Copied {file_name} to {parent_path}")
            except Exception as e:
                print(f"Error copying {file_name}: {e}")
    
    
    def isHEICImage(self, extension):
        return is_HEIC_file(extension[0])
        