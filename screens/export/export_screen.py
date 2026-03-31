import asyncio

import customtkinter as ctk
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from controllers.export_controller import ExportController
    from models.file_transfer.file_transfer import FileTransferManager
from screens.observer import Observer
from components.widgets import (
    DeviceLabel,
    FolderOverview,
    SelectFileButtonExport,
    ActionsButton,
    SelectOptions,
)


class ExportScreen(ctk.CTkFrame, Observer):
    items: list[str]

    def __init__(self,
                 master, controller):
        super().__init__(master)
        self.items = []
        self.total_items = 0
        self.collected_files = {}
        self.controller: ExportController = controller
        self.to_directory = ""
        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal")
        # Set up the grid to contain 8 rows item and filled up.
        self.grid_columnconfigure(0, weight=1, uniform='a')
        self.export_screen()

    def update(self, subject: FileTransferManager) -> None:
        self.items = subject.items
        self.collected_files = subject.collected_files
        self.to_directory = subject.to_directory
        self.progress = subject.progress
        print("Export screen received update: "f"progress={subject.progress}")
        total_items = (subject.amount_of_photos_collected +
                       subject.amount_of_videos_collected)
        if (total_items > 0):
            self.progressbar.set(subject.progress / total_items)
        self.total_items = subject.amount_of_files_collected
        self.set_files_created()

    def export_screen(self) -> None:
        # Title on the first row of the grid
        self.export_title = ctk.CTkLabel(
            self,
            text="Export media files",
            font=("Roboto", 24)
        )
        self.export_title.grid(
            row=0,
            column=0,
            sticky='ew',
            padx=20,
            pady=20,
            columnspan=2
        )

        # Buttons for selecting files
        self.set_from_and_to_directories()
        # Files created menu
        self.set_files_created()
        # Selected options
        self.set_selected_options()
        # Progress bar
        self.set_progress()
        # Action buttons
        self.set_actions_buttons()

    def set_found_devices(self):
        devices_names = self.controller.get_all_device_names()
        self.device_row_frame = getattr(self, "device_row_frame", None)
        print(self.device_row_frame)
        if (len(devices_names) == 0):
            if self.device_row_frame is not None and isinstance(self.device_row_frame, ctk.CTkFrame):
                self.device_row_frame.destroy()
                self.device_row_frame = None
            print("No devices found. Device row frame destroyed.")
            return

        self.device_row_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.device_row_frame.grid(row=1, column=0, sticky='w', padx=25, pady=5)

        # Clear previous labels
        for widget in getattr(self, "device_labels", []):
            widget.destroy()
        self.device_labels = []

        # Add new labels inside the container frame
        for i, name in enumerate(devices_names):
            device_label = DeviceLabel(
                self.device_row_frame,
                name,
                delete_callback=lambda n=name: print(f"Delete {n}")
            )
            device_label.grid(
                row=0,           # same row
                column=i,        # next column
                sticky='w',      # no stretching
                padx=(2, 2),     # small gap between labels
                pady=(0, 0)
            )
            self.device_labels.append(device_label)

    def set_from_and_to_directories(self) -> None:
        # From directory input
        def from_callback(fromDir):
            return (self.controller.set_from_directory(fromDir))

        self.fromDirInput = SelectFileButtonExport(
            self,
            from_callback,
            entry_text="From directory",
            text_button="Browse From Directory",
            scan_devices_func=lambda: asyncio.run_coroutine_threadsafe(
                self.controller.check_for_connected_devices(), self.controller.async_loop
            )
        )
        self.fromDirInput.grid(
            row=2,
            column=0,
            sticky='nsew',
            padx=20,
            pady=0
        )

        # To directory input
        def to_callback(toDir):
            return (self.controller.set_to_directory(toDir))

        self.toDirectory = SelectFileButtonExport(
            self,
            to_callback,
            entry_text="To directory",
            text_button="Browse To Directory"
        )
        self.toDirectory.grid(
            row=3,
            column=0,
            sticky='nsew',
            padx=20,
            pady=0
        )

    def set_files_created(self) -> None:
        print("Setting files created in the export screen widget.")
        self.file_menu = FolderOverview(
            self, items=self.collected_files, to_directory=self.to_directory, total_items=self.total_items)
        self.file_menu.grid(
            row=4,
            column=0,
            sticky='nsew',
            padx=20,
            pady=20
        )

    def set_selected_options(self):
        self.selectOptions = SelectOptions(self, self.controller)
        self.selectOptions.grid(
            row=5,
            column=0,
            sticky='nsew',
            padx=20,
            pady=0
        )

    def set_progress(self):
        self.progressbar.grid(
            row=6,
            column=0,
            sticky='ew',
            padx=20,
            pady=15
        )
        self.progressbar.set(0)

    def set_actions_buttons(self):
        self.actions_button = ActionsButton(
            self,
            start=lambda: asyncio.run_coroutine_threadsafe(
                self.controller.start_progress(), self.controller.async_loop
            ),
            clear=self.controller.clear_progress,
            scan=lambda: print("Scan clicked"),
            save=lambda: asyncio.run_coroutine_threadsafe(
                self.controller.save_progress(), self.controller.async_loop
            )
        )
        self.actions_button.grid(
            row=7,
            column=0,
            sticky='nsew',
            padx=20,
            pady=10
        )
