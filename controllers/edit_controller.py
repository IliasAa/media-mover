import customtkinter as ctk
from screens.edit.image_widgets import ImageImport, ImageOutput, CloseOutput, OpenOutputButton
from PIL import Image, ImageTk, ImageOps
import os
from settings import FILE_NAME_DEFAULT, FLIP_OPTIONS, ROTATE_DEFAULT

class CanvasWithImage(ImageTk.PhotoImage):
    def __init__(self, image=None, **kw) -> None:
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
    
    def setImage(self, image: ImageTk.PhotoImage):
        self.image = image
        
    def image_importing(self, path):
        self.original = Image.open(path)
        self.pos_vars['has_image_selected'].set(True)
        # Set the file name to the last part of the path
        self.pos_vars["file_name"].set(os.path.basename(path))
        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)            
        self.image_output = ImageOutput(self, self.resize_image)
        self.close_button = CloseOutput(self, self.close_edit)

        self.image_output._tk_image = self.image_tk
        self._call_resize_now()
        
    def resize_image(self, event):
        canvas_ratio = event.width / event.height
        self.canvas_width = event.width
        self.canvas_height = event.height

        if canvas_ratio > self.image_ratio:
            self.image_height = int(event.height)
            self.image_width = int(self.image_height * self.image_ratio)
        else:
            self.image_width = int(event.width)
            self.image_height = int(self.image_width / self.image_ratio)

        self.canvas_width = event.width
        self.canvas_height = event.height

        self.place_image()
    
    def manipulate_image(self, *args):
        self.image = self.original
        self.image = self.image.rotate(self.pos_vars['rotate'].get())
        if self.pos_vars['flip'].get() == 'X':
            self.image = ImageOps.mirror(self.image)
        elif self.pos_vars['flip'].get() == 'Y':
            self.image = ImageOps.flip(self.image)
        elif self.pos_vars['flip'].get() == 'Both':
            self.image = ImageOps.mirror(self.image)
            self.image = ImageOps.flip(self.image)

        self.place_image()
    

class EditController:
    def __init__(self, pos_vars):
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
        self.set_pos_vars(pos_vars)
        
    def set_pos_vars(self, pos_vars: dict):
        self.pos_vars = pos_vars
        for key, var in self.pos_vars.items():
            if key not in ['file_name', 'show_edit_menu', 'has_image_selected'] and isinstance(var, ctk.Variable):
                var.trace_add("write", self.manipulate_image)
    
    def switch_screen(self, screen_name: str):
        # Logic to switch screens
        pass
    
    
    
        
    def close_edit(self):
        self.reset_pos_vars()
        self.image_output.grid_forget()
        self.close_button.place_forget()
    
    def resize_image(self, event):
        canvas_ratio = event.width / event.height
        self.canvas_width = event.width
        self.canvas_height = event.height

        if canvas_ratio > self.image_ratio:
            self.image_height = int(event.height)
            self.image_width = int(self.image_height * self.image_ratio)
        else:
            self.image_width = int(event.width)
            self.image_height = int(self.image_width / self.image_ratio)

        self.canvas_width = event.width
        self.canvas_height = event.height

        self.place_image()
    
    def reset_pos_vars(self):
        self.pos_vars['has_image_selected'].set(False)
        self.pos_vars['show_edit_menu'].set(False)
        self.pos_vars['rotate'].set(ROTATE_DEFAULT)
        self.pos_vars['flip'].set(FLIP_OPTIONS[0])
        self.pos_vars['file_name'].set(FILE_NAME_DEFAULT)  