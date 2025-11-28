from tkinter import filedialog
import customtkinter as ctk
from typing import TYPE_CHECKING
from models.file_transfer.file_transfer import FileTransferManager
from screens.observer import Observer
from models.subject import Subject
from components.widgets import FilesMenu, SelectFileButtonExport, ActionsButton
from test_scripts.convert_HEIC_test import convert_single_file


class ExportScreen(ctk.CTkFrame, Observer):
    items: list[str]
    
    def __init__(self,master, controller):
        super().__init__(master)
        self.items = []
        self.controller = controller
        self.progressbar =  ctk.CTkProgressBar(self, orientation="horizontal" )
        ## Set up the grid to contain 8 rows item and filled up.
        self.grid_columnconfigure(0, weight=1, uniform='a')
        self.export_screen()
    
    def update(self, subject: Subject) -> None:
        if isinstance(subject, FileTransferManager):
            self.items = subject.items
            self.set_files_created(self.items)
            self.progressbar.set(subject.progress / 100)
            self.fromDirInput.set_entry(subject.from_directory)
            self.toDirectory.set_entry(subject.to_directory)
    
    def export_screen(self) -> None:
        ## Title on the first row of the grid
        self.export_title = ctk.CTkLabel(self, text="Export media files", font=("Roboto", 24))    
        self.export_title.grid(row=0, column=0, sticky='ew', padx=20, pady=20, columnspan=2)
        
        self.fromDirInput = SelectFileButtonExport(self, lambda fromDir: self.controller.set_from_directory(fromDir), entry_text="From directory", text_button="Browse")
        self.fromDirInput.grid(row=1, column=0, sticky='nsew', padx=20, pady=0)
        self.toDirectory = SelectFileButtonExport(self, lambda toDir: self.controller.set_to_directory(toDir), entry_text="To directory", text_button="Browse")
        self.toDirectory.grid(row=2, column=0, sticky='nsew', padx=20, pady=0)
        
        self.set_files_created(self.items)
        
        # self.selection_files = SelectFilesOverview(self)
        # self.selection_files.grid(row=3, column=0, sticky='nsew', padx=20, pady=0)  
        
        # self.selectOptions = SelectOptions(self, self.export_controller.file_manager_props)
        # self.selectOptions.grid(row=5, column=0, sticky='nsew', padx=20, pady=0)
        
        self.progressbar.grid(row=6, column=0, sticky='ew', padx=20, pady=15)
        self.progressbar.set(0.4)
        
        self.actions_button = ActionsButton(self, self.controller.start_progress, self.controller.clear_progress)
        self.actions_button.grid(row=7, column=0, sticky='nsew', padx=20, pady=10)
    
    def set_files_created(self, items: list[str]) -> None:
        print("Setting files created in the export screen widget.")
        self.file_menu = FilesMenu(self, items)
        self.file_menu.grid(row=4, column=0, sticky='nsew', padx=20, pady=20)  
            
        
    
