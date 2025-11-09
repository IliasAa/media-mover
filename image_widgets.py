import customtkinter as ctk
from tkinter import filedialog, Canvas

from settings import BACKGROUND_COLOR

class ImageImport(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)



class ImageOutput(Canvas):
    def __init__(self, parent, resize_image):
        # Corrected the super() call
        super().__init__(master=parent, background=BACKGROUND_COLOR, bd=0, highlightthickness=0, relief='ridge')
        self.grid(row=0, column=0, sticky="nsew")

        self.bind('<Configure>', resize_image)
        

class OpenOutputButton(ctk.CTkButton):
    def __init__(self, parent, import_func):
        super().__init__(master=parent, text="Open Image", command=self.open_dialog)
        self.image_import = import_func
        self.grid(row=0, column=0, padx=10, pady=10, rowspan = 2)
    
        
    def open_dialog(self):
        path = filedialog.askopenfile().name
        self.image_import(path)

       


class CloseOutput(ctk.CTkButton):
    def __init__(self, parent, close_button):
        super().__init__(
            master=parent,
            text="x",
            text_color='white', fg_color='transparent', width=40, height=40, command=close_button)
        self.place(relx = 0.99, rely=0.01, anchor='ne')




