import customtkinter as ctk
from edit_screen import EditScreen
from export_screen import ExportScreen
from image_widgets import ImageImport, ImageOutput, CloseOutput, OpenOutputButton
from edit_screen import EditScreen
from PIL import Image, ImageTk, ImageOps
from menu import OptionsMenu, EditMenu
from settings import *
import test as tst
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.init_parameters()
        self.iconbitmap(APP_ICON_PATH)
        
        # Configure the first row to take up all available vertical space with a weight of 1.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')

        print("name_variable: ", __name__)


        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
        
        
        # Left half of the screen
        self.menu = OptionsMenu(self, self.pos_vars)
        
        # Right half of the screen
        self.show_export_screen()
        
        self.mainloop()
        
    def show_export_screen(self):
        self.my_frame = ExportScreen(master=self, pos_vars = self.pos_vars)
        self.my_frame.grid(row=0, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=10, pady=10)
    

    def show_edit_screen(self):
        # Only show the edit menu if a file is selected
        is_file_selected = self.pos_vars['has_image_selected'].get()
        
        print("Is file selected: ", is_file_selected)
        if self.pos_vars['has_image_selected'].get():
            self.setup_edit_menu()
        
        # Right half of the screen
        self.my_frame = EditScreen(master=self, pos_vars = self.pos_vars)
        self.my_frame.grid(row=0, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=10, pady=10)
    
    def setup_edit_menu(self, *args):
        # If the edit menu is already shown, remove it            
        if hasattr(self, 'edit_menu'):
                self.edit_menu.grid_forget()
        
        # Only show the edit menu if a file is selected
        if (self.pos_vars['has_image_selected'].get() == True):
            self.edit_menu = EditMenu(self, self.pos_vars)
            if self.pos_vars['show_edit_menu'].get():
                self.edit_menu.grid(row=1, column=0, rowspan=1, sticky="ns", padx=10, pady=10)    
    
    def init_parameters(self):        
        self.pos_vars = {
            'rotate': ctk.DoubleVar(value=ROTATE_DEFAULT),
            'flip': ctk.StringVar(value=FLIP_OPTIONS[0]),
            'file_name': ctk.StringVar(value=FILE_NAME_DEFAULT),
            'show_edit_menu': ctk.BooleanVar(value=False),
            'has_image_selected': ctk.BooleanVar(value=False),
            'selected_screen': ctk.StringVar(value=SCREEN_OPTIONS[0]),
            'from_directory': ctk.StringVar(value=""),
            'to_directory': ctk.StringVar(value=""),
            'selected_file': ctk.StringVar(value=""),
        }
        
        for key, var in self.pos_vars.items():
            if key in ['file_name'] and isinstance(var, ctk.Variable):
                var.trace_add("write", self.reinitialize_menu)
            elif key in ['show_edit_menu'] and isinstance(var, ctk.Variable):
                var.trace_add("write", self.setup_edit_menu)
            elif key in ['selected_screen'] and isinstance(var, ctk.Variable):
                var.trace_add("write", self.selectOtherScreen)
    

    
    def reinitialize_menu(self):
        self.menu = OptionsMenu(self, self.pos_vars)
    
    def selectOtherScreen(self, *args):
        current_screen = self.pos_vars['selected_screen'].get()
        self.my_frame.grid_forget()
        if (current_screen == SCREEN_OPTIONS[0]):
            self.show_export_screen()
        elif (current_screen == SCREEN_OPTIONS[1]):
            self.show_edit_screen()
            
            
if __name__ == "__main__":
    App()
               