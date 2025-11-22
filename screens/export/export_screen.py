from tkinter import filedialog
import customtkinter as ctk
from controllers.export_controller import ExportController
from screens.export.file_transfer import FileTransferManager, FileTransferProps
from widgets import FilesMenu, SelectFileButton, SelectOptions, SelectFilesOverview, ActionsButton
from test_scripts.convert_HEIC_test import convert_single_file

class ExportScreen(ctk.CTkFrame):
    def __init__(self,master, pos_vars, **kwargs):
        super().__init__(master, **kwargs)
        self.pos_vars = pos_vars
        self.progressbar =  ctk.CTkProgressBar(self, orientation="horizontal" )
        self.export_controller = ExportController(self.progressbar)
        ## Set up the grid to contain 8 rows item and filled up.
        self.grid_columnconfigure(0, weight=1, uniform='a')
        self.export_screen()
    
    
    def export_screen(self):
        ## Title on the first row of the grid
        self.export_title = ctk.CTkLabel(self, text="Export media files", font=("Roboto", 24))    
        self.export_title.grid(row=0, column=0, sticky='ew', padx=20, pady=20, columnspan=2)
        
        self.fromDirInput = SelectFileButton(self, lambda fromDir: self.export_controller.set_from_directory(fromDir), entry_text="From directory")
        self.fromDirInput.grid(row=1, column=0, sticky='nsew', padx=20, pady=0)
        
        self.toDirectory = SelectFileButton(self, lambda toDir: self.export_controller.set_to_directory(toDir), entry_text="To directory")
        self.toDirectory.grid(row=2, column=0, sticky='nsew', padx=20, pady=0)
        
        # self.selection_files = SelectFilesOverview(self)
        # self.selection_files.grid(row=3, column=0, sticky='nsew', padx=20, pady=0)
        
        self.file_menu = FilesMenu(self, self.pos_vars, self.export_controller)
        self.file_menu.grid(row=4, column=0, sticky='nsew', padx=20, pady=20)    
        
        self.selectOptions = SelectOptions(self, self.export_controller.file_manager_props)
        self.selectOptions.grid(row=5, column=0, sticky='nsew', padx=20, pady=0)
        
        self.progressbar.grid(row=6, column=0, sticky='ew', padx=20, pady=15)
        self.progressbar.set(0.4)
        
        self.actions_button = ActionsButton(self, self.export_controller.start_progress)
        self.actions_button.grid(row=7, column=0, sticky='nsew', padx=20, pady=10)
    

            
        
    
