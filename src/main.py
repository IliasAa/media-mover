from tkinter import PhotoImage
import customtkinter as ctk
from controllers.export_controller import ExportController
from components.menu import OptionsMenu
from models.file_transfer.file_transfer import FileTransferManager
from settings import APP_NAME, APP_ICON_PATH, WINDOW_SIZE



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)

        icon = PhotoImage(file=APP_ICON_PATH)
        self.iconphoto(False, icon)
        self.wm_iconbitmap(APP_ICON_PATH)

        # Configure the first row to take up all available vertical space with
        # a weight of 1.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=6, uniform='a')

        # Left half of the screen
        self.menu = OptionsMenu(self)
        self.file_transfer_manager = FileTransferManager()
        self.selected_controller = ExportController(self,
                                                    self.file_transfer_manager)

        # self.mainloop()


if __name__ == "__main__":
    app = App()
    app.eval("tk::PlaceWindow . right")
    app.mainloop()
