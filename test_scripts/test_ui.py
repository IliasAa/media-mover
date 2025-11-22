import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"
os.environ["CTK_FORCE_API"] = "SOFTWARE"

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("300x200")

label = ctk.CTkLabel(root, text="If you see this, it's fixed!")
label.pack(pady=20)

btn = ctk.CTkButton(root, text="Test Button")
btn.pack(pady=10)

root.mainloop()
