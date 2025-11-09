import customtkinter as ctk
from settings import *
from tkinter import filedialog, Canvas

class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=DARK_GREY)
        self.pack(fill='x', pady=4, ipady=8)


class SliderPanel(Panel):
    def __init__(self, parent, text, rotation, min_value, max_value):
        super().__init__(parent=parent)

        self.rowconfigure((0,1), weight=1)
        self.columnconfigure((0,1), weight=1)

        self.rotation = rotation
        self.rotation.trace('w', self.update_text)

        ctk.CTkLabel(master=self, text=text).grid(column=0, row=0, sticky='W', padx=5)
        self.num_label = ctk.CTkLabel(master=self, text=rotation.get())
        self.num_label.grid(column=1, row=0, sticky='E', padx=5)
        ctk.CTkSlider(
            master=self, fg_color=SLIDER_BG, variable=rotation, from_= min_value, to=max_value, command= self.update_text
            ).grid(column=0, columnspan=2, row=1, sticky='ew', padx=5, pady=5)

    def update_text(self, *args):
        self.num_label.configure(text = f'{round(self.rotation.get(), 0)}')
        
        
        

class SegmentedPanel(Panel):
    def __init__(self, parent, text, data_var, options):
        super().__init__(parent = parent)

        ctk.CTkLabel(self, text=text).pack()
        ctk.CTkSegmentedButton(self,variable= data_var, values=options).pack(expand =True, fill='both', padx =4, pady=4)
        

class NewFileNameInputPanel(Panel):
    def __init__(self, parent, file_name):
        super().__init__(parent = parent)

        ctk.CTkLabel(self, text="Fill in new file name").pack()
        entry = ctk.CTkEntry(self, placeholder_text=file_name)
        entry.pack(pady=8, padx=8, fill="both", expand=True)
                
class SelectFileButton(Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.rowconfigure((0,1), weight=1)
        self.columnconfigure((0,1), weight=1)
        # Second row of the grid with the source directory label and entry
        ctk.CTkEntry(master=parent, placeholder_text="from").grid(column=0, row=0, sticky='W', padx=5)

        browse_dir_button = ctk.CTkButton(master=parent, text="Browse", command=lambda: filedialog.askdirectory())
        browse_dir_button.grid(column=1, row=0, sticky='E', padx=5)
      
        
class SelectFileButton(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        # Second row of the grid with the source directory label and entry
        entry = ctk.CTkEntry(master=parent, placeholder_text="from")
        entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        browse_dir_button = ctk.CTkButton(master=parent, text="Browse", command=lambda: filedialog.askdirectory())
        browse_dir_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
class RevertButton(ctk.CTkButton):
    def __init__(self, parent, *args):
        super().__init__(master =parent, text = 'Revert', command=self.revert)
        self.pack(side='bottom', pady=10)
        self.args = args
    def revert(self):
        for var, value in self.args:
            var.set(value)
        

