import customtkinter as ctk
from image_widgets import ImageImport, ImageOutput, CloseOutput, OpenOutputButton
from PIL import Image, ImageTk, ImageOps
from settings import *
import test as tst
import os


class EditScreen(ctk.CTkFrame):
    def __init__(self, master, pos_vars, **kwargs):
        super().__init__(master, **kwargs)
        self.image_width = 0
        self.image_height = 0
        self.canvas_width = 0
        self.canvas_height = 0
        self.pos_vars = pos_vars
        
        for key, var in self.pos_vars.items():
            if key not in ['file_name', 'show_edit_menu', 'has_image_selected'] and isinstance(var, ctk.Variable):
                var.trace_add("write", self.manipulate_image)

        
        ## Set up the grid to only contain 1 item and filled up.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.edit_images()
         
    def edit_images(self):
        self.open_output = OpenOutputButton(self, self.image_importing)
    
    
    def manipulate_image(self, *args):
        self.image = self.original

        self.image = self.image.rotate(self.pos_vars['rotate'].get())
        if self.pos_vars['flip'].get() == 'X':
            self.image =  ImageOps.mirror(self.image)
        elif self.pos_vars['flip'].get() == 'Y':
            self.image =  ImageOps.flip(self.image)
        elif self.pos_vars['flip'].get() == 'Both':
            self.image =  ImageOps.mirror(self.image)
            self.image =  ImageOps.flip(self.image)

        self.place_image()


    def image_importing(self, path):
        self.original = Image.open(path)
        self.pos_vars['has_image_selected'].set(True)
        # Set the file name to the last part of the path
        self.pos_vars["file_name"] = (os.path.basename(path))
        self.image = self.original
        self.image_ratio = self.image.size[0] / self.image.size[1]
        self.image_tk = ImageTk.PhotoImage(self.image)            
        self.image_output = ImageOutput(self, self.resize_image)
        self.close_button = CloseOutput(self, self.close_edit)

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

    def place_image(self):
        self.image_output.delete("all")
        resized_image = self.image.resize((self.image_width, self.image_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)
        self.image_output.create_image(self.canvas_width / 2, self.canvas_height / 2, image=self.image_tk)
        
    
    def reset_pos_vars(self):
        self.pos_vars['has_image_selected'].set(False)
        self.pos_vars['show_edit_menu'].set(False)
        self.pos_vars['rotate'].set(ROTATE_DEFAULT)
        self.pos_vars['flip'].set(FLIP_OPTIONS[0])
        self.pos_vars['file_name'] = (FILE_NAME_DEFAULT)    
  
         
         