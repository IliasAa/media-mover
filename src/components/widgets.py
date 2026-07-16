import tkinter
from PIL import Image
from tkinter import filedialog
import helper.path_helper as ph
import customtkinter as ctk

from helper.file_helper_functions import tree_generator_text


class Panel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent, fg_color='transparent')


class SelectFileButtonExport(Panel):
    def __init__(self,
                 parent,
                 import_func,
                 text_button,
                 entry_text="Select file",
                 **kwargs):

        super().__init__(parent)
        self.selectDirectory = import_func


        if kwargs.get('scan_devices_func'):
            self.scan_devices_func = kwargs.get('scan_devices_func')
            self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform='a')
        else:
            self.grid_columnconfigure((0, 1, 2), weight=1, uniform='a')
        self.grid_rowconfigure(0, weight=1)

        # Second row of the grid with the source directory label and entry
        self.entry = ctk.CTkEntry(master=self, placeholder_text=entry_text)
        self.entry.grid(row=0, column=0,
                        columnspan=2, padx=(5),
                        pady=(5), sticky="nsew")

        browse_dir_button = ctk.CTkButton(master=self,
                                          command=lambda:
                                              self.import_directory())

        browse_dir_button.grid(row=0, column=2,
                               columnspan=1, padx=(5),
                               pady=(5), sticky="ew")

        if kwargs.get('scan_devices_func'):
            scan_devices_button = ctk.CTkButton(
                master=self,
                text="Scan for devices",
                command=lambda: self.scan_devices_func()
            )
            scan_devices_button.grid(
                row=0,
                column=3,
                columnspan=1,
                padx=(5),
                pady=(5),
                sticky="ew"
            )

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


class ScanForDevices(ctk.CTkFrame):
    def __init__(self,
                 parent,
                 text_button,
                 scan_callback, **kwargs):
        super().__init__(parent)
        self.grid_columnconfigure((0), weight=1, uniform='a')
        self.scanButton = ctk.CTkButton(
            master=self,
            text=text_button,
            command=lambda: scan_callback())
        self.scanButton.grid(row=0, column=0, columnspan=1, padx=(5), pady=(5),
                             sticky="ew")


class DeviceLabel(ctk.CTkFrame):
    def __init__(self, parent, device_name, delete_callback, **kwargs):
        # Use a colored frame as background
        super().__init__(parent, corner_radius=5, fg_color='#2FA572',
                         **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=0)

        # Device name label
        self.label = ctk.CTkLabel(
            self, text=f"💾 {device_name}", text_color="white", anchor="w",
            fg_color="transparent", font=("Helvetica", 10)
        )
        self.label.grid(row=0, column=0, padx=5, pady=1, sticky="w")

        # Delete button
        self.delete_button = ctk.CTkButton(
            self,
            text="✕",
            font=("Helvetica", 10),
            width=5,
            height=5,
            fg_color="#FF5C5C",
            hover_color="#FF1F1F",
            command=lambda: delete_callback(device_name)
        )
        self.delete_button.grid(row=0, column=1, padx=5, pady=0)


# Container frame to hold multiple labels tightly
class DeviceLabelRow(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="#1E1E1E", **kwargs)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.refresh_labels()

    def refresh_labels(self):
        # Clear existing labels
        for widget in self.winfo_children():
            widget.destroy()

        devices_names = self.controller.get_all_device_names()
        for i, name in enumerate(devices_names):
            device_label = DeviceLabel(
                self,
                name,
                delete_callback=lambda n=name: print(f"Delete {n}")
            )
            device_label.grid(row=0, column=i, sticky="w", padx=5, pady=5)


class SelectOptions(Panel):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent)
        # Adjusted column weights to balance width
        self.grid_columnconfigure((0, 1), weight=1, uniform='a')
        self.grid_rowconfigure((0, 1), weight=1, uniform='a')
        self.radio_var = tkinter.IntVar(value=0)

        checkbox_1 = ctk.CTkCheckBox(
            master=self,
            text="Filter blurry images",
            command=lambda: controller.toggle_blurry())
        checkbox_1.grid(
            row=0,
            column=0,
            padx=(10, 20),
            pady=(5),
            sticky="nsew")  # Added space between columns

        checkbox_2 = ctk.CTkCheckBox(
            master=self,
            text="Create date folders",
            command=lambda: controller.toggle_date_folders())
        checkbox_2.grid(
            row=0,
            column=1,
            padx=(20, 10),
            pady=(5),
            sticky="nsew")  # Right column aligned to the right

        checkbox_3 = ctk.CTkCheckBox(
            master=self,
            text="Filter lookalikes",
            command=lambda: controller.toggle_lookalikes())
        checkbox_3.grid(
            row=1,
            column=0,
            padx=(10, 20),
            pady=(5),
            sticky="nsew")  # Added space between columns

        checkbox_4 = ctk.CTkCheckBox(
            master=self,
            text="Save hashes",
            command=lambda: controller.toggle_hashes())
        checkbox_4.grid(
            row=1,
            column=1,
            padx=(20, 10),
            pady=(5),
            sticky="nsew")  # Right column aligned to the right


class SelectFilesOverview(Panel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)

        self.grid_columnconfigure((0), weight=1, uniform='a')
        # Adjusted row weights to balance height
        self.grid_rowconfigure((0, 1), weight=1)

        self.selected_file = ctk.CTkEntry(master=self,
                                          placeholder_text="Selected file",
                                          justify="center", height=25)
        self.selected_file.grid(
            row=0,
            column=0,
            padx=(5),
            pady=(5),
            sticky="nsew"
        )
        # Set a fixed height for the scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=200)
        self.scrollable_frame.grid_columnconfigure((0), weight=1, uniform='a')
        self.scrollable_frame.grid(
            row=1,
            column=0,
            padx=(5),
            pady=(5),
            sticky="nsew"
        )


class ActionsButton(Panel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)

        start = kwargs.get("start")
        clear = kwargs.get("clear")
        # scan = kwargs.get("scan")
        save = kwargs.get("save")
        scan = kwargs.get("scan")

        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform='a')
        # Adjusted row weights to balance height
        self.grid_rowconfigure((0), weight=1)
        buttons = [
            ("Scan", scan),
            ("Start", start),
            ("Save", save),
            ("Clear", clear)
        ]
        for i, (text, command) in enumerate(buttons):
            button = ctk.CTkButton(master=self, text=text, command=command)
            button.grid(row=0, column=i, padx=(5), pady=(5), sticky="nsew")


class FolderOverview(ctk.CTkTextbox):
    def __init__(self, master, items, to_directory, total_items, **kwargs):
        super().__init__(master, wrap="none", font=("Courier", 11), **kwargs)

        self.items = items
        self.to_directory = to_directory
        self.total_items = total_items


        display_text = tree_generator_text(self.items, self.to_directory, self.total_items)

        self.insert("1.0", display_text)
        self.configure(state="disabled")  # make it read-only
