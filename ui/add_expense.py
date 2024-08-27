import re
import tkinter as tk
from tkinter import messagebox

from database import add_expense, get_groups, get_members, get_expense, get_group_name, get_profile_involved, \
    get_profile_by_id, get_profile_name, get_profile_id, update_expense, get_group_id, get_admin_id


class AddExpense(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.amount_entry_box = None
        self.expense_description_entry = None
        self.group_options = None
        self.selected_group = tk.StringVar()
        self.payee_options = None
        self.selected_payee = tk.StringVar()
        self.user_listbox = None
        self.add_button = None
        self.label = None
        self.profiles = list()  # helps getting member_ids before inserting in database.
        self.is_edit = False
        self.expense_id = None

        self.create_widgets()

    @staticmethod
    def amount_entry_check(p):
        pattern = r'^\d*(\.\d{0,2})?$'
        if re.match(pattern, p):
            return True
        else:
            return False

    def create_widgets(self):
        self.label = tk.Label(self, text="Add Expense", font=("Arial", 18))
        self.label.pack(fill="x")
        self.label.config(bg="white", anchor="center", pady=10)

        amount_frame = tk.Frame(self, bg="white", padx=25, pady=5)
        amount_frame.pack(fill="x")

        amount_label = tk.Label(amount_frame, text="Amount:", font=("Arial", 16))
        amount_label.pack(side="left")
        amount_label.config(bg="white")

        validate_command = (self.register(self.amount_entry_check), "%P")
        self.amount_entry_box = tk.Entry(amount_frame, font=("Arial", 16), validate="key",
                                         validatecommand=validate_command)
        self.amount_entry_box.pack()
        self.amount_entry_box.config(bg="white", width=25)

        description_frame = tk.Frame(self, bg="white", padx=25, pady=5)
        description_frame.pack(fill="x")
        expense_description_label = tk.Label(description_frame, text="Description:", font=("Arial", 16))
        expense_description_label.config(bg="white", anchor="nw")
        expense_description_label.pack(side="left")
        self.expense_description_entry = tk.Entry(description_frame, font=("Arial", 16))
        self.expense_description_entry.config(bg="white", width=25)
        self.expense_description_entry.pack()

        group_frame = tk.Frame(self, bg="white", width=390)
        group_frame.pack(fill="x")

        group_label = tk.Label(group_frame, text="Group:", font=("Arial", 16))
        group_label.pack(side="left", padx=25)
        group_label.config(bg="white", anchor="nw")

        self.group_options = tk.OptionMenu(group_frame, self.selected_group, "")
        self.group_options.pack(side="left", padx=55, pady=5)
        self.group_options.config(font=("Arial", 14), indicatoron=False)

        payee_clear_button_frame = tk.Frame(self, width=390)
        payee_clear_button_frame.pack(fill="x")
        payee_clear_button_frame.config(bg="white")

        payee_label = tk.Label(payee_clear_button_frame, text="Payee:", font=("Arial", 16))
        payee_label.pack(side="left", padx=25)
        payee_label.config(bg="white", anchor="nw")

        self.payee_options = tk.OptionMenu(payee_clear_button_frame, self.selected_payee, "")
        self.payee_options.pack(side="left", padx=55, pady=5)
        self.payee_options.config(font=("Arial", 14), indicatoron=False)

        refresh_button = tk.Button(payee_clear_button_frame, text="Clear", command=self.clear_entry)
        refresh_button.pack(side="left", padx=25, pady=5)
        refresh_button.config(font=("Ink Free", 16, "bold"))

        user_label = tk.Label(self, text="Users Involved:", font=("Arial", 16))
        user_label.pack(fill="x", padx=25)
        user_label.config(bg="white", anchor="nw")
        self.user_listbox = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.user_listbox.config(bg="white", font=("Arial", 14))
        self.user_listbox.pack(fill='both', expand=1, padx=50)
        s_ = tk.Scrollbar(self.user_listbox, orient=tk.VERTICAL)
        s_.pack(side=tk.RIGHT, fill=tk.Y)
        s_.config(command=self.user_listbox.yview)
        self.user_listbox.config(yscrollcommand=s_.set)

        self.add_button = tk.Button(self, text="Add Expense", command=self.add_update_expense)
        self.add_button.pack(side="right", padx=55, pady=10)

        back_button = tk.Button(self, text="Home", command=self.go_home)
        back_button.pack(side="left", padx=55, pady=10)

        self.load_groups()

    def load_groups(self):
        group_dict = get_groups()
        group_list = list(group_dict.keys())
        self.selected_group.set(group_list[0])
        menu = self.group_options["menu"]
        menu.delete(0, "end")
        for group_name in group_list:
            menu.add_command(label=group_name, command=lambda value=group_name: self.load_profiles(value))
        menu = self.group_options.nametowidget(self.group_options.menuname)
        menu.config(font=("Arial", 14))
        self.load_profiles()

    def load_profiles(self, selection=None):
        # when something is selected from group drop-down menu, its value is passed to this function.
        if selection is None:
            selection = self.selected_group.get()
        else:
            self.selected_group.set(selection)

        self.user_listbox.delete(0, tk.END)
        menu = self.payee_options["menu"]
        menu.delete(0, tk.END)
        group_id = get_group_id(selection)
        self.profiles = get_members(group_id)
        for profile_id, name, contact in self.profiles:
            self.user_listbox.insert(tk.END, f"{name}, {contact}")
            menu.add_command(label=name, command=lambda value=name: self.selected_payee.set(value))
        menu = self.payee_options.nametowidget(self.payee_options.menuname)
        menu.config(font=("Arial", 14))
        self.selected_payee.set(self.profiles[0][1])

    def add_update_expense(self):
        selected_group = self.selected_group.get()
        group_id = get_group_id(selected_group)
        payee_name = self.selected_payee.get()
        payee_id = get_profile_id(payee_name)
        amount = self.amount_entry_box.get()
        admin_id = get_admin_id()
        try:
            amount = float(amount)
        except ValueError:
            pass
        description = self.expense_description_entry.get()
        selected_member_indices = self.user_listbox.curselection()
        member_ids = [self.profiles[i][0] for i in selected_member_indices]
        if amount and description and selected_group and member_ids:
            if self.is_edit:
                update_expense(self.expense_id, payee_id, amount, description, member_ids)
            else:
                add_expense(group_id, payee_id, amount, description, member_ids)
                self.controller.on_group_update()
            messagebox.showinfo("Success", "Expense added successfully!")
            if admin_id == payee_id or admin_id in member_ids:
                self.controller.refresh_homepage()
            self.controller.on_expense_update(group_id)
            self.clear_entry()
        else:
            messagebox.showerror("Error", "Amount, description, group, payee and users involved are required.")

    def clear_entry(self):
        self.amount_entry_box.delete(0, tk.END)
        self.expense_description_entry.delete(0, tk.END)
        self.user_listbox.selection_clear(0, tk.END)
        self.is_edit = False
        self.load_groups()
        self.label.config(text="Add Expense")
        self.add_button.config(text="Add Expense")
        self.focus_set()

    def go_home(self):
        self.clear_entry()
        self.controller.show_home_page()

    def edit_expense_id(self, expense_id):
        self.is_edit = True
        self.expense_id = expense_id
        expense = get_expense(expense_id)
        expense_id = expense[0]
        group_id = expense[1]
        group_name = get_group_name(group_id)
        payee_id = expense[2]
        payee_name = get_profile_name(payee_id)
        amount = expense[3]
        description = expense[4]

        self.amount_entry_box.delete(0, tk.END)
        self.amount_entry_box.insert(tk.END, amount)
        self.expense_description_entry.delete(0, tk.END)
        self.expense_description_entry.insert(tk.END, description)
        menu = self.group_options["menu"]
        menu.delete(0, tk.END)
        self.selected_group.set(group_name)
        self.label.config(text=f"Edit Expense from {group_name}")
        self.add_button.config(text="Save")

        profile_id_involved = get_profile_involved(expense_id)
        profile_id_involved = list(profile_id_involved.keys())
        profile_involved = [get_profile_by_id(i) for i in profile_id_involved]

        self.profiles = profile_involved
        end = len(self.profiles)
        all_members_of_group = get_members(group_id)
        for member in all_members_of_group:
            if member not in self.profiles:
                self.profiles.append(member)
        self.user_listbox.delete(0, tk.END)
        payee_menu = self.payee_options["menu"]
        payee_menu.delete(0, tk.END)

        for index, (profile_id, name, contact) in enumerate(self.profiles):
            self.user_listbox.insert(tk.END, f"{name}, {contact}")
            payee_menu.add_command(label=name, command=lambda value=name: self.selected_payee.set(value))
        menu = self.payee_options.nametowidget(self.payee_options.menuname)
        menu.config(font=("Arial", 14))
        self.user_listbox.selection_set(0, end - 1)
        self.selected_payee.set(payee_name)

    def add_in_gname(self, g_name):
        self.selected_group.set(g_name)
        menu = self.group_options["menu"]
        menu.delete(0, "end")
        self.load_profiles()

    def settle_expense(self, group_id, receiver_id, payee_id, amount):
        group_name = get_group_name(group_id)
        payee_name = get_profile_name(payee_id)
        receiver_name = get_profile_name(receiver_id)

        self.amount_entry_box.delete(0, tk.END)
        self.amount_entry_box.insert(tk.END, amount)
        self.expense_description_entry.delete(0, tk.END)
        self.expense_description_entry.insert(tk.END, f"{payee_name} paid {receiver_name}")
        menu = self.group_options["menu"]
        menu.delete(0, tk.END)
        self.selected_group.set(group_name)
        self.load_profiles()
        self.label.config(text=f"Settle Expense from {group_name}")
        self.add_button.config(text="Settle")

        self.selected_payee.set(payee_name)
        receiver_index = self.profiles.index(get_profile_by_id(receiver_id))
        self.user_listbox.selection_set(receiver_index)
