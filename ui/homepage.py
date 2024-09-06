import tkinter as tk
from tkinter import messagebox

from database import get_groups, get_admin_assets, get_admin_name


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.admin_name = get_admin_name(self.controller.get_db_key()).split()[-1]
        self.a_debt_amount = get_admin_assets(self.controller.get_db_key())
        if self.a_debt_amount >= 0:
            self.a_debt = "assets"
            self.a_debt_color = "green"
            self.a_debt_amount = "$ " + format(self.a_debt_amount, ".2f")
        else:
            self.a_debt = "debts"
            self.a_debt_color = "red"
            self.a_debt_amount = "$ " + format(abs(self.a_debt_amount), ".2f")

        self.groups = {}  # groups[self.groups_listbox] = group_id
        self.groups_listbox = None

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text=f"{self.admin_name}! Your total {self.a_debt} are:", font=("Arial", 22))
        label.pack(fill="x")
        label.config(bg="white", anchor="center", pady=5)
        total_label = tk.Label(self, text=self.a_debt_amount, font=("Arial", 20))
        total_label.pack(fill="x")
        total_label.config(bg=self.a_debt_color, anchor="center", pady=5)

        groups_label = tk.Label(self, text="Groups:", font=("Arial", 16))
        groups_label.pack(fill="x")
        groups_label.config(bg="white", anchor="nw", padx=35, pady=5)

        self.groups_listbox = tk.Listbox(self, font=("Harrington", 20, "bold"))
        groups = get_groups(self.controller.get_db_key())
        index = 0
        for name, group_id in groups.items():
            self.groups_listbox.insert(index, name)
            self.groups[index] = group_id
            index += 1
        self.groups_listbox.pack(fill='both', expand=1, padx=35, pady=0)

        s = tk.Scrollbar(self.groups_listbox, orient=tk.VERTICAL)
        s.pack(side=tk.RIGHT, fill=tk.Y)
        s.config(command=self.groups_listbox.yview)
        self.groups_listbox.config(yscrollcommand=s.set)

        buttons_frame = tk.Frame(self, bg="white")
        buttons_frame.pack(fill="both", padx=35, pady=10)

        add_profile_button = tk.Button(buttons_frame, text="Add Profile", command=self.add_profile)
        add_profile_button.pack(side='left', padx=0, pady=10)

        add_group_button = tk.Button(buttons_frame, text="Add Group", command=self.add_group)
        add_group_button.pack(side='left', padx=20, pady=10)

        add_group_button = tk.Button(buttons_frame, text="Add Expense", command=self.add_expense)
        add_group_button.pack(side='left', padx=0, pady=10)

        view_expense_button = tk.Button(buttons_frame, text="View Group", command=self.view_group)
        view_expense_button.pack(side="right", padx=0, pady=10)

        setting_button = tk.Button(buttons_frame, text="Settings", command=self.view_settings)
        setting_button.pack(side="right", padx=20, pady=10)

    def add_profile(self):
        self.groups_listbox.selection_clear(0, tk.END)
        self.focus_set()
        self.controller.show_create_profile()

    def add_group(self):
        self.groups_listbox.selection_clear(0, tk.END)
        self.focus_set()
        self.controller.show_create_group()

    def add_expense(self):
        if not self.groups:
            messagebox.showerror("Warning", "You must create a group first.")
            return
        self.groups_listbox.selection_clear(0, tk.END)
        self.focus_set()
        self.controller.show_edit_add_expense_details()

    def view_group(self):
        if not self.groups:
            messagebox.showerror("Warning", "You must create a group first.")
            return
        if not self.groups_listbox.curselection():
            messagebox.showerror("Error", "No groups selected")
            return
        group_id = self.groups[self.groups_listbox.curselection()[0]]
        self.groups_listbox.selection_clear(0, tk.END)
        self.focus_set()
        self.controller.show_group_details(group_id)

    def view_settings(self):
        self.groups_listbox.selection_clear(0, tk.END)
        self.focus_set()
        self.controller.show_settings()
