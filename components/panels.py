import customtkinter as ctk
from settings import *
from tkinter import filedialog, Canvas

class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color=DARK_GREY)
        self.pack(fill='x', pady=4, ipady=8)

        

