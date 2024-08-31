import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog

from database import add_admin_profile, initialize_db, check_database_structure


class InitialSetup(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.name = None
        self.contact = None

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Welcome!", font=('Freestyle Script', 48))
        label.pack(fill="x")
        label.config(bg="white", anchor="center", pady=0)
        label = tk.Label(self, text="Create your profile:", font=('Freestyle Script', 38))
        label.pack(fill="x")
        label.config(bg="white", anchor="center", pady=0)

        frame = tk.LabelFrame(self, text="Sign Up", bg="white", font=("Arial", 16), fg="#292929")
        frame.pack(fill="x", padx=55, pady=10)

        self.name = tk.Entry(frame, font=("Arial", 20), fg="#424242", highlightthickness=3)
        self.name.pack(fill="x", padx=5, pady=10)
        self.name.insert(0, "Name")
        self.name.bind("<FocusIn>", self.clear_name)
        self.name.bind("<FocusOut>", self.name_placeholder)

        self.contact = tk.Entry(frame, font=("Arial", 20), fg="#424242", highlightthickness=3)
        self.contact.pack(fill="x", padx=5, pady=10)
        self.contact.insert(0, "Contact (Mobile/E-mail)")
        self.contact.bind("<FocusIn>", self.clear_contact)
        self.contact.bind("<FocusOut>", self.contact_placeholder)

        button = tk.Frame(self, bg="white", pady=10)
        button.pack(fill="x")
        button.config(bg="white")

        add_button = tk.Button(button, text="Create Profile", font=("Monotype Corsiva", 18, "bold"), width=15,
                               command=self.add_admin_profile)
        add_button.pack(padx=55, side="right")

        back_button = tk.Button(button, text="Install Backup", font=("Monotype Corsiva", 18, "bold"), width=15,
                                command=self.install_backup)
        back_button.pack(padx=55, side="left")

    def clear_name(self, _event):
        if self.name.get() == "Name":
            self.name.delete(0, tk.END)
            self.name.config(fg="black")

    def name_placeholder(self, _event):
        if not self.name.get():
            self.name.insert(0, "Name")
            self.name.config(fg="#424242")

    def clear_contact(self, _event):
        if self.contact.get() == "Contact (Mobile/E-mail)":
            self.contact.delete(0, tk.END)
            self.contact.config(fg="black")

    def contact_placeholder(self, _event):
        if not self.contact.get():
            self.contact.insert(0, "Contact (Mobile/E-mail)")
            self.contact.config(fg="#424242")

    def add_admin_profile(self):
        admin_name = self.name.get()
        admin_contact = self.contact.get()
        if self.name.get() == "Name":
            admin_name = None
        if self.contact.get() == "Contact (Mobile/E-mail)":
            admin_contact = None
        if admin_name and admin_contact:
            initialize_db()
            add_admin_profile(admin_name, admin_contact)
            self.controller.show_home_page()
        else:
            messagebox.showerror("Error", "Name and contact are required.")

    def install_backup(self):
        initial_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_types = [("Backup file", "*.db"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(title="Select a backup file", initialdir=initial_dir,
                                              filetypes=file_types)
        if filepath:
            destination_path = os.path.join(os.getcwd(), "split_expense.db")
            try:
                shutil.copy(filepath, destination_path)
            except shutil.SameFileError:
                pass
            is_correct_file = check_database_structure()
            if is_correct_file:
                messagebox.showinfo("Success", "You have successfully imported from backup.")
                self.controller.refresh_homepage()
                self.controller.show_home_page()
            else:
                messagebox.showerror("Error", "Not a valid backup file or corrupted file.")
        else:
            messagebox.showwarning("Error", "No file selected.")
