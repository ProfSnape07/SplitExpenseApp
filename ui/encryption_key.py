import hashlib
import tkinter as tk
from tkinter import messagebox

from database import check_password


class EncryptionKey(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.key = None

        self.create_widgets()

    def create_widgets(self):
        frame = tk.LabelFrame(self, text="Welcome!", font=("Freestyle Script", 48), bg="white", borderwidth=0)
        frame.pack(fill="both", padx=65, pady=20)
        key_label = tk.Label(frame, text="Enter your password:", font=("Freestyle Script", 48), bg="white")
        key_label.pack(anchor="w", padx=0, pady=5)
        self.key = tk.Entry(frame, font=("Arial", 48), show="*", relief="solid")
        self.key.pack(anchor="center", fill="x", padx=0, pady=5)
        submit = tk.Button(frame, text="Submit", height=2, width=15, font=("Monotype Corsiva", 18, "bold"),
                           command=self.submit)
        submit.pack(anchor="center", padx=0, pady=5)
        setting = tk.Button(frame, text="Settings", height=2, width=15, font=("Monotype Corsiva", 18, "bold"),
                            command=self.view_settings)
        setting.pack(anchor="center", padx=0, pady=20)

    def submit(self):
        if self.key.get():
            key = hashlib.sha256(self.key.get().encode()).hexdigest()
            if check_password(key):
                self.controller.set_db_key(key)
                self.controller.refresh_homepage()
                self.controller.show_home_page()
            else:
                messagebox.showerror("Wrong password", "Incorrect Password!")
                self.key.delete(0, "end")
        else:
            messagebox.showerror("Error", "Password can't be empty!")

    def view_settings(self):
        self.key.delete(0, "end")
        self.focus_set()
        self.controller.show_settings(False)
