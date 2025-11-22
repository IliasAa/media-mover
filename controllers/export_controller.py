from unittest import case
from screens.export.file_transfer import FileTransferManager
from models.file_transfer_props import FileTransferProps

class ExportController:
    def __init__(self, progressbar):
      self.file_manager_props = FileTransferProps(None, None, False, False, False, False)
      self.progressbar = progressbar
      self.on_items_updated = None
        
    def start_progress(self):
        self.file_manager = FileTransferManager(self.file_manager_props, self.progressbar)
        self.file_manager.start_progress(self.add_item)
        
    def add_item(self, item):
        if self.on_items_updated:
            self.file_manager_props.items.append(item)
            self.on_items_updated()
        
    def set_from_directory(self, from_directory):
        self.file_manager_props.from_path = from_directory
    
    def set_to_directory(self, to_directory):
        self.file_manager_props.to_path = to_directory
        
    def switch_screen(self, screen_name):
        match screen_name:
            case "export":
                None
            case "edit":
                None
            case _:
                None
    
    
