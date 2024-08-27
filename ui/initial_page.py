import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import os
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

        name_frame = tk.Frame(self, bg="white", padx=55, pady=10)
        name_frame.pack(fill="x")

        name_label = tk.Label(name_frame, text="Name:", font=("Arial", 16))
        name_label.pack(side="left", padx=0)
        name_label.config(bg="white")

        self.name = tk.Entry(name_frame, font=("Arial", 16))
        self.name.pack(side="left", padx=35)
        self.name.config(bg="white")

        contact_frame = tk.Frame(self, bg="white", padx=55, pady=10)
        contact_frame.pack(fill="x")

        contact_label = tk.Label(contact_frame, text="Contact:", font=("Arial", 16))
        contact_label.pack(side="left", padx=0)
        contact_label.config(bg="white")

        self.contact = tk.Entry(contact_frame, font=("Arial", 16))
        self.contact.pack(side="left", padx=35)
        self.contact.config(bg="white")

        button = tk.Frame(self, bg="white", padx=55, pady=10)
        button.pack(fill="x")
        button.config(bg="white")

        add_button = tk.Button(button, text="Create Profile", command=self.add_admin_profile)
        add_button.pack(padx=55, side="right")
        add_button.config(anchor="ne")

        back_button = tk.Button(button, text="Install Backup", command=self.install_backup)
        back_button.pack(padx=55, side="left")
        back_button.config(anchor="nw")

    def add_admin_profile(self):
        admin_name = self.name.get()
        admin_contact = self.contact.get()
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
            shutil.copy(filepath, destination_path)
            is_correct_file = check_database_structure()
            if is_correct_file:
                messagebox.showinfo("Success", "You have successfully imported from backup.")
                self.controller.show_home_page()
            else:
                messagebox.showerror("Error", "Not a valid backup file or corrupted file.")
        else:
            messagebox.showwarning("Error", "No file selected.")
