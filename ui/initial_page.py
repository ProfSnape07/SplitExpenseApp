import hashlib
import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog

from database import add_admin_profile, initialize_db, check_database_structure, add_miscellaneous, \
    check_password_required


class InitialSetup(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.name = None
        self.contact = None
        self.encryption_required = tk.IntVar()
        self.encryption_key = None
        self.show_warning = True

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

        self.encryption_key = tk.Entry(frame, font=("Arial", 20), fg="#424242", highlightthickness=3)
        self.encryption_key.pack(fill="x", padx=5, pady=10)
        self.encryption_key.insert(0, "Password")
        self.encryption_key.config(state="disabled")
        self.encryption_key.bind("<FocusIn>", self.clear_encryption_key)
        self.encryption_key.bind("<FocusOut>", self.encryption_key_placeholder)

        encryption_button = tk.Checkbutton(frame, bg="white", text="Encryption Required", font=("Arial", 16),
                                           variable=self.encryption_required, command=self.encryption_on_off)
        encryption_button.pack(side="left", padx=5, pady=10)

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

    def clear_encryption_key(self, *_event):
        if self.encryption_key.get() == "Password":
            self.encryption_key.config(show="*")
            self.encryption_key.delete(0, tk.END)
            self.encryption_key.config(fg="black")

    def encryption_key_placeholder(self, *_event):
        if not self.encryption_key.get():
            self.encryption_key.config(show="")
            self.encryption_key.insert(0, "Password")
            self.encryption_key.config(fg="#424242")

    def add_admin_profile(self):
        admin_name = self.name.get()
        admin_contact = self.contact.get()
        key = self.encryption_key.get()
        if self.name.get() == "Name":
            admin_name = None
        if self.contact.get() == "Contact (Mobile/E-mail)":
            admin_contact = None
        if self.encryption_key.get() == "Password":
            key = None

        if self.encryption_required.get():
            if admin_name and admin_contact and key:
                key = hashlib.sha256(key.encode()).hexdigest()
                self.controller.set_db_key(key)
            else:
                messagebox.showerror("Error", "Name, contact and password are required.")
        else:
            if admin_name and admin_contact:
                pass
            else:
                messagebox.showerror("Error", "Name and contact are required.")
        initialize_db()
        add_admin_profile(admin_name, admin_contact, key)
        add_miscellaneous("app_name", "SplitExpense", key)
        self.controller.show_home_page()

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
            if check_database_structure():
                messagebox.showinfo("Success", "You have successfully imported from backup.")
                if check_password_required():
                    self.controller.show_encryption_key()
                    return
                self.controller.refresh_homepage()
                self.controller.show_home_page()
            else:
                messagebox.showerror("Error", "Not a valid backup file or corrupted file.")
        else:
            messagebox.showwarning("Error", "No file selected.")

    def encryption_on_off(self):
        if self.encryption_required.get() == 1:
            if self.show_warning:
                self.show_warning = not messagebox.askyesno("Warning",
                                                            "Note: Loosing your password will lock you out of your "
                                                            "data, only your password can decrypt your data, "
                                                            "there is no option to forgot your password.\nClick Yes "
                                                            "if you don't want to see this warning again.")
            self.encryption_key.config(state="normal")
            self.clear_encryption_key()
            self.encryption_key.focus_set()
        else:
            self.encryption_key.delete(0, tk.END)
            self.encryption_key_placeholder()
            self.encryption_key.config(state="disabled")
