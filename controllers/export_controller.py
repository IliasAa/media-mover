from screens.export.export_screen import ExportScreen
from models.file_transfer.file_transfer import FileTransferManager

class ExportController:
    
    def __init__(self, master):
        self.subject = FileTransferManager()
        self.show_export_screen(master)
        ## Register the ExportScreen as an observer to the FileTransferManager
        self.subject.attach(self.my_frame)
      
    def show_export_screen(self, master):
        '''Display the export screen on the main application window'''
        self.my_frame = ExportScreen(master=master, controller=self)
        self.my_frame.grid(row=0, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=10, pady=10)
    
    def start_progress(self):
        self.subject.start_progress()
        
    def clear_progress(self):
        self.subject.clear_progress()
        
    def set_from_directory(self, from_directory):
        '''Set the source directory for file transfer'''
        self.subject.from_directory = from_directory
    
    def set_to_directory(self, to_directory):
        '''Set the destination directory for file transfer'''
        self.subject.to_directory = to_directory
    
    def toggle_blurry(self):
        self.subject.filter_blurry = not self.subject.filter_blurry
    
    def toggle_date_folders(self):
        self.subject.create_date_folders = not self.subject.create_date_folders
    
    def toggle_lookalikes(self):
        self.subject.filter_lookalikes = not self.subject.filter_lookalikes
        
    def toggle_hashes(self):
        self.subject.save_hashes = not self.subject.save_hashes
    
