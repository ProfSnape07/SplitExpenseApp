import sqlite3
import tkinter as tk
from tkinter import messagebox

from database import add_group, get_profiles


class CreateGroup(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.members_listbox = None
        self.name_entry = None
        self.profile_ids = {}

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="Create Group", font=("Arial", 18))
        label.pack(fill="x")
        label.config(bg="white", anchor="center", pady=10)

        name_label = tk.Label(self, text="Group Name:", font=("Arial", 16))
        name_label.pack(fill="x", padx=25)
        name_label.config(bg="white", anchor="nw")

        self.name_entry = tk.Entry(self, width=50, font=("Arial", 16))
        self.name_entry.pack(padx=55)
        self.name_entry.config(bg="white")

        warnings_label = tk.Label(self, text="*group name needs to be unique", font=("Arial", 10))
        warnings_label.pack(fill="x", padx=55)
        warnings_label.config(bg="white", fg="#1a1917", anchor="nw")

        members_label = tk.Label(self, text="Select Members:", font=("Arial", 16))
        members_label.pack(fill="x", padx=25)
        members_label.config(bg="white", anchor="nw")

        self.members_listbox = tk.Listbox(self, selectmode=tk.EXTENDED, font=("Arial", 12))
        self.members_listbox.config(bg="white")
        self.members_listbox.pack(fill='both', expand=1, padx=50)

        s = tk.Scrollbar(self.members_listbox, orient=tk.VERTICAL)
        s.pack(side=tk.RIGHT, fill=tk.Y)
        s.config(command=self.members_listbox.yview)
        self.members_listbox.config(yscrollcommand=s.set)

        add_button = tk.Button(self, text="Create Group", command=self.create_group)
        add_button.pack(side="right", padx=55, pady=10)

        back_button = tk.Button(self, text="Home", command=self.go_home)
        back_button.pack(side="left", padx=55, pady=10)

        self.load_all_profiles()

    def load_all_profiles(self):
        profiles = get_profiles(self.controller.get_db_key())
        self.members_listbox.delete(0, tk.END)
        self.profile_ids.clear()
        for index, (profile_id, name, contact) in enumerate(profiles):
            self.members_listbox.insert(tk.END, f"Name: {name}, Contact: {contact}")
            self.profile_ids[index] = profile_id

    def create_group(self):
        name = self.name_entry.get()
        profile_ids = []
        selected_indices = self.members_listbox.curselection()
        if selected_indices:
            for i in selected_indices:
                profile_ids.append(self.profile_ids[i])

        if name and profile_ids:
            try:
                add_group(name, profile_ids, self.controller.get_db_key())
                messagebox.showinfo("Success", "Group created successfully!")
                self.clear_entry()
                self.controller.on_group_update()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Group already exists with same name.")
        else:
            messagebox.showerror("Error", "Group name and members are required.")

    def clear_entry(self):
        self.name_entry.delete(0, tk.END)
        self.members_listbox.selection_clear(0, tk.END)
        self.focus_set()

    def go_home(self):
        self.clear_entry()
        self.controller.show_home_page()
