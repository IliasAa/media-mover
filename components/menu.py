import customtkinter as ctk
from components.panels import *


class OptionsMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        

        label = ctk.CTkLabel(master=self, text="Options", font=("Roboto", 18), text_color="white")
        label.pack(pady=22, padx=10)

        export_button = ctk.CTkButton(master=self, text="Export", command= lambda: {})
        export_button.pack(pady=5)
    
    