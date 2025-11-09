import customtkinter as ctk
from panels import *

class EditMenu(ctk.CTkTabview):
    def __init__(self, parent, pos_vars):
        super().__init__(master=parent)

        self.add('Position')
        self.add('Export')

        PositionFrame(self.tab("Position"), pos_vars)
        ExportFrame(self.tab("Export"), pos_vars)


class OptionsMenu(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
        super().__init__(master=parent)
        self.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        

        label = ctk.CTkLabel(master=self, text="Options", font=("Roboto", 18))
        label.pack(pady=22, padx=10)

        export_button = ctk.CTkButton(master=self, text="Export", command= lambda: self.set_export(pos_vars))
        export_button.pack(pady=5)
        
        self.show_menu = pos_vars['show_edit_menu']

        # edit_button = ctk.CTkButton(master=self, text="Edit", command= lambda:  pos_vars['show_edit_menu'].set( not self.show_menu.get()))
        edit_button = ctk.CTkButton(master=self, text="Edit", command= lambda:  self.set_edit(pos_vars))
       
        # edit_button = ctk.CTkButton(master=self, text="Edit", command= lambda: self.set_edit_boolean( not self.show_menu.get()))
        edit_button.pack(pady=5)
    
    def set_export(self, pos_vars):
        if isinstance(pos_vars["selected_screen"], ctk.StringVar) and pos_vars["selected_screen"].get() == SCREEN_OPTIONS[1]:
            pos_vars['selected_screen'].set(SCREEN_OPTIONS[0])
            return
    
    
    def set_edit(self, pos_vars):
        if isinstance(pos_vars["selected_screen"], ctk.StringVar) and pos_vars["selected_screen"].get() == SCREEN_OPTIONS[0]:
            print("Export screen is selected. Cannot edit.")
            pos_vars['selected_screen'].set(SCREEN_OPTIONS[1])
            print(pos_vars["selected_screen"].get(), "instance of ctk.StringVar")
            return
        
        if pos_vars["has_image_selected"].get() == False:
            print("No file selected.")
            return
   
        pos_vars['show_edit_menu'].set( not self.show_menu.get())
           
        
class OptionsFrame(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
         super().__init__(master=parent, fg_color='transparent')
         self.pack(expand=True, fill='both')


class PositionFrame(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
    
        SliderPanel(self, "Rotation", pos_vars["rotate"], 0, 360)
        SegmentedPanel(self, 'Invert', pos_vars["flip"], options=FLIP_OPTIONS)
        RevertButton(self, 
                     (pos_vars['rotate'], ROTATE_DEFAULT),
                     (pos_vars['flip'], FLIP_OPTIONS[0]))
    
        

class ExportFrame(ctk.CTkFrame):
    def __init__(self, parent, pos_vars):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        NewFileNameInputPanel(self, pos_vars["file_name"])

        

    