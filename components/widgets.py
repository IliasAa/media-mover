import tkinter
from tkinter import filedialog
import customtkinter as ctk

class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')
        
class SelectFileButtonExport(Panel):
    def __init__(self, parent, import_func, text_button, entry_text="Select file", **kwargs):
        super().__init__(parent)
        self.selectDirectory = import_func
     
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform='a')
        self.grid_rowconfigure(0, weight=1)    
        
        # Second row of the grid with the source directory label and entry
        self.entry = ctk.CTkEntry(master=self, placeholder_text=entry_text)
        self.entry.grid(row=0, column=0,  columnspan=2, padx=(5), pady=(5), sticky="nsew")
        
        browse_dir_button = ctk.CTkButton(master=self, text=text_button, command=lambda: self.import_directory())
        browse_dir_button.grid(row=0, column=2,columnspan=1, padx=(5), pady=(5), sticky="ew")
                
    def import_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selectDirectory(directory)
            self.set_entry(directory)
            self.entry.master.focus_set()
            
    def set_entry(self, text):
        self.entry.delete(0, tkinter.END)
        if (len(text) > 0):
            self.entry.insert(0, text)

class SelectOptions(Panel):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        
        self.grid_columnconfigure((0, 1), weight=1, uniform='a')  # Adjusted column weights to balance width
        self.grid_rowconfigure((0, 1), weight=1, uniform='a')
        self.radio_var = tkinter.IntVar(value=0)
        
        checkbox_1 = ctk.CTkCheckBox(master=self, text="Filter blurry images", command=lambda: controller.toggle_blurry())
        checkbox_1.grid(row=0, column=0, padx=(10, 20), pady=(5), sticky="nsew")  # Added space between columns
        
        checkbox_2 = ctk.CTkCheckBox(master=self, text="Create date folders", command=lambda: controller.toggle_date_folders())
        checkbox_2.grid(row=0, column=1, padx=(20, 10), pady=(5), sticky="nsew")  # Right column aligned to the right
        
        checkbox_3 = ctk.CTkCheckBox(master=self, text="Filter lookalikes", command=lambda: controller.toggle_lookalikes())
        checkbox_3.grid(row=1, column=0, padx=(10, 20), pady=(5), sticky="nsew")  # Added space between columns
        
        checkbox_4 = ctk.CTkCheckBox(master=self, text="Save hashes", command=lambda: controller.toggle_hashes())
        checkbox_4.grid(row=1, column=1, padx=(20, 10), pady=(5), sticky="nsew")  # Right column aligned to the right
        
        
        
class SelectFilesOverview(Panel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
                
        self.grid_columnconfigure((0), weight=1, uniform='a')
        self.grid_rowconfigure((0, 1), weight=1)  # Adjusted row weights to balance height
                
        self.selected_file = ctk.CTkEntry(master=self, placeholder_text="Selected file", justify="center", height=25)
        self.selected_file.grid(row=0, column=0, padx=(5), pady=(5), sticky="nsew")
                
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=200)  # Set a fixed height for the scrollable frame
        self.scrollable_frame.grid_columnconfigure((0), weight=1, uniform='a')
        self.scrollable_frame.grid(row=1, column=0, padx=(5), pady=(5), sticky="nsew")
        
class ActionsButton(Panel):
    def __init__(self, parent, start_progress, clear_progress, **kwargs):
        super().__init__(parent)
    
        
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform='a')
        self.grid_rowconfigure((0), weight=1)  # Adjusted row weights to balance height
        
        self.button = ctk.CTkButton(master=self, text="Save", command=lambda: print("Save clicked"))
        self.button.grid(row=0, column=0, padx=(5), pady=(5), sticky="nsew")
        
        self.button2 = ctk.CTkButton(master=self, text="Start", command=start_progress)
        self.button2.grid(row=0, column=1, padx=(5), pady=(5), sticky="nsew")
        
        self.button3 = ctk.CTkButton(master=self, text="Clear", command=clear_progress)
        self.button3.grid(row=0, column=2, padx=(5), pady=(5), sticky="nsew")
        
        
class FilesMenu(Panel):
    def __init__(self, parent,items, **kwargs):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(self, text="Created files", font=("Roboto", 18))
        self.label.grid(row=0, column=0, padx=5, pady=0, sticky="nsew")

        self.listbox = ctk.CTkScrollableFrame(self, height=50, fg_color="transparent")
        self.listbox.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")

        self.listbox.grid_columnconfigure(0, weight=1)
        
        self.update_items(items)
        
    def update_items(self, items):
        # Clear existing items
        for widget in self.listbox.winfo_children():
            widget.destroy()
        
        # Add all items
        for i, item in enumerate(items):
            RowFrame(self.listbox, i, item)
            
class RowFrame(ctk.CTkFrame):
    def __init__(self, parent, index, item, **kwargs):
        super().__init__(parent)
        self.grid(row=index, column=0, sticky="nsew", padx=5, pady=0)
        self.grid_columnconfigure(0, weight=1)
        label = ctk.CTkLabel(self, text= f" {index+1}. " + item, anchor="w", justify="left", fg_color="transparent", text_color="white")
        label.grid(row=0, column=0, padx=12, pady=0, sticky="nsew")