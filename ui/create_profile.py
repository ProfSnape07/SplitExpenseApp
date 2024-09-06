import sqlite3
import tkinter as tk
from tkinter import messagebox

from database import add_profile


class CreateProfile(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller
        self.name = None
        self.contact = None

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Create Profile", font=("Arial", 18))
        label.pack(fill="x")
        label.config(bg="white", anchor="center", pady=10)

        name_label = tk.Label(self, text="Name:", font=("Arial", 16))
        name_label.pack(fill="x", padx=55, pady=10)
        name_label.config(bg="white", anchor="w")

        self.name = tk.Entry(self, width=50, font=("Arial", 16))
        self.name.pack(pady=0, padx=55)
        self.name.config(bg="white")

        warnings_label = tk.Label(self, text="*name needs to be unique", font=("Arial", 10))
        warnings_label.pack(fill="x", padx=55)
        warnings_label.config(bg="white", fg="#1a1917", anchor="nw")

        contact_label = tk.Label(self, text="Contact (Mobile/E-mail):", font=("Arial", 16))
        contact_label.pack(fill="x", padx=55, pady=10)
        contact_label.config(bg="white", anchor="w")

        self.contact = tk.Entry(self, width=50, font=("Arial", 16))
        self.contact.pack(pady=5, padx=55)
        self.contact.config(bg="white")

        button = tk.Frame(self, width=390, pady=30)
        button.pack(fill="x")
        button.config(bg="white")

        add_button = tk.Button(button, text="Create Profile", command=self.add_profile)
        add_button.pack(padx=55, side="right")
        add_button.config(anchor="ne")

        back_button = tk.Button(button, text="Home", command=self.go_home)
        back_button.pack(padx=55, side="left")
        back_button.config(anchor="nw")

    def go_home(self):
        self.clear_entry()
        self.focus_set()
        self.controller.show_home_page()

    def clear_entry(self):
        self.name.delete(0, tk.END)
        self.contact.delete(0, tk.END)
        self.focus_set()

    def add_profile(self):
        name = self.name.get()
        contact = self.contact.get()
        if name and contact:
            try:
                add_profile(name, contact, self.controller.get_db_key())
                messagebox.showinfo("Success", "Profile added successfully!")
                self.clear_entry()
                self.controller.on_profile_update()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Profile already exists with same name.")
        else:
            messagebox.showerror("Error", "Name and contact are required.")
