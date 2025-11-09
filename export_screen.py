from tkinter import filedialog
import customtkinter as ctk
from file_transfer import FileTransferManager
from widgets import FilesMenu, SelectFileButton, SelectOptions, SelectFilesOverview, ActionsButton
from test_scripts.convert_HEIC_test import convert_single_file



class ExportScreen(ctk.CTkFrame):
    def __init__(self,master, pos_vars, **kwargs):
        super().__init__(master, **kwargs)
        self.pos_vars = pos_vars
        
        ## Set up the grid to contain 8 rows item and filled up.
        self.grid_columnconfigure(0, weight=1, uniform='a')
        
        for key, var in self.pos_vars.items():
            if key in ['from_directory', 'to_directory'] and isinstance(var, ctk.Variable):
                var.trace_add("write", self.set_directories)
        
        self.export_screen()
    
    def set_directories(self, *args):
        print("Setting directories")
        # print(self.pos_vars['from_directory'].get())
        # print(self.pos_vars['to_directory'].get())
        print(self.pos_vars['selected_file'].get())
    
    def export_screen(self):
        ## Title on the first row of the grid
        self.export_title = ctk.CTkLabel(self, text="Export media files", font=("Roboto", 24))    
        self.export_title.grid(row=0, column=0, sticky='ew', padx=20, pady=20, columnspan=2)
        
        self.fromDirInput = SelectFileButton(self, lambda fromDir: self.pos_vars['from_directory'].set(fromDir), entry_text="From directory")
        self.fromDirInput.grid(row=1, column=0, sticky='nsew', padx=20, pady=0)
        
        self.toDirectory = SelectFileButton(self, lambda toDir: self.pos_vars['to_directory'].set(toDir), entry_text="To directory")
        self.toDirectory.grid(row=2, column=0, sticky='nsew', padx=20, pady=0)
        
        # self.selection_files = SelectFilesOverview(self)
        # self.selection_files.grid(row=3, column=0, sticky='nsew', padx=20, pady=0)
        
        self.items = ["No items found"]
        
        self.file_menu = FilesMenu(self, self.pos_vars, self.items, self.set_directories)
        self.file_menu.grid(row=4, column=0, sticky='nsew', padx=20, pady=20)
        
        
        self.selectOptions = SelectOptions(self, )
        self.selectOptions.grid(row=5, column=0, sticky='nsew', padx=20, pady=0)
        
        self.progressbar =  ctk.CTkProgressBar(self, orientation="horizontal" )
        self.progressbar.grid(row=6, column=0, sticky='ew', padx=20, pady=15)
        self.progressbar.set(0.4)
        
        self.actions_button = ActionsButton(self, self.start_progress)
        self.actions_button.grid(row=7, column=0, sticky='nsew', padx=20, pady=10)
    
    
    def start_progress(self):
        self.file_manager = FileTransferManager(self.pos_vars, self.progressbar)
        self.file_manager.start_progress()
        
            
        
    
