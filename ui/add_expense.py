import re
import tkinter as tk
from tkinter import messagebox

from database import add_expense, get_groups, get_members, get_expense, get_group_name, get_profile_involved, \
    get_profile_by_id, get_profile_name, update_expense


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
        self.groups = {}  # groups[name] = group_id
        self.profiles_id = {}  # profiles_id[index] = profile_id
        self.payee_id = {}  # payee_id[name] = profile_id
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
        self.groups = get_groups(self.controller.get_db_key())
        group_list = list(self.groups.keys())
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
        group_id = self.groups[selection]
        profiles = get_members(group_id, self.controller.get_db_key())
        index = 0
        self.profiles_id.clear()
        self.payee_id.clear()
        for profile_id, name, contact in profiles:
            self.user_listbox.insert(index, f"{name}, {contact}")
            menu.add_command(label=name, command=lambda value=name: self.selected_payee.set(value))
            self.profiles_id[index] = profile_id
            self.payee_id[name] = profile_id
            index += 1
        menu = self.payee_options.nametowidget(self.payee_options.menuname)
        menu.config(font=("Arial", 14))
        self.selected_payee.set(profiles[0][1])

    def add_update_expense(self):
        selected_group = self.selected_group.get()
        group_id = self.groups[selected_group]
        payee_name = self.selected_payee.get()
        payee_id = self.payee_id[payee_name]
        amount = self.amount_entry_box.get()
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount can't be empty.")
            return
        description = self.expense_description_entry.get()
        selected_member_indices = self.user_listbox.curselection()
        member_ids = [self.profiles_id[i] for i in selected_member_indices]
        if amount and description and selected_group and member_ids:
            if self.is_edit:
                update_expense(self.expense_id, payee_id, amount, description, member_ids, self.controller.get_db_key())
                messagebox.showinfo("Success", "Expense updated successfully!")
            else:
                add_expense(group_id, payee_id, amount, description, member_ids, self.controller.get_db_key())
                messagebox.showinfo("Success", "Expense added successfully!")
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
        expense = get_expense(expense_id, self.controller.get_db_key())
        expense_id = expense[0]
        group_id = expense[1]
        group_name = get_group_name(group_id, self.controller.get_db_key())
        payee_id = expense[2]
        payee_name = get_profile_name(payee_id, self.controller.get_db_key())
        amount = expense[3]
        description = expense[4]

        self.amount_entry_box.delete(0, tk.END)
        self.amount_entry_box.insert(tk.END, amount)
        self.expense_description_entry.delete(0, tk.END)
        self.expense_description_entry.insert(tk.END, description)
        menu = self.group_options["menu"]
        menu.delete(0, tk.END)
        self.selected_group.set(group_name)
        self.user_listbox.delete(0, tk.END)
        self.label.config(text=f"Edit Expense from {group_name}")
        self.add_button.config(text="Save")

        profile_id_involved_share = get_profile_involved(expense_id, self.controller.get_db_key())
        end = len(profile_id_involved_share)
        profile_involved = [get_profile_by_id(profile_id, self.controller.get_db_key()) for profile_id in
                            profile_id_involved_share.keys()]
        all_members_of_group = get_members(group_id, self.controller.get_db_key())
        for member in all_members_of_group:
            if member not in profile_involved:
                profile_involved.append(member)

        self.profiles_id.clear()
        index = 0
        for profile_id, name, contact in profile_involved:
            self.user_listbox.insert(index, f"{name}, {contact}")
            self.profiles_id[index] = profile_id
            index += 1
        self.user_listbox.selection_set(0, end - 1)
        self.selected_payee.set(payee_name)

    def add_in_gname(self, g_name):
        self.selected_group.set(g_name)
        menu = self.group_options["menu"]
        menu.delete(0, "end")
        self.load_profiles()

    def settle_expense(self, group_id, receiver_id, payee_id, amount):
        group_name = get_group_name(group_id, self.controller.get_db_key())
        payee_name = get_profile_name(payee_id, self.controller.get_db_key())
        receiver_name = get_profile_name(receiver_id, self.controller.get_db_key())

        self.amount_entry_box.delete(0, tk.END)
        self.amount_entry_box.insert(tk.END, amount)
        self.expense_description_entry.delete(0, tk.END)
        self.expense_description_entry.insert(tk.END, f"{payee_name} paid {receiver_name}")
        menu = self.group_options["menu"]
        menu.delete(0, tk.END)
        self.selected_group.set(group_name)
        self.load_profiles()
        menu = self.payee_options["menu"]
        menu.delete(0, tk.END)
        self.selected_payee.set(payee_name)
        for index, profile_id in self.profiles_id.items():
            if profile_id == receiver_id:
                self.user_listbox.selection_set(index)

        self.label.config(text=f"Settle Expense from {group_name}")
        self.add_button.config(text="Settle")
