import tkinter as tk
from tkinter import messagebox

from database import get_group_expenses, get_group_name, delete_expense, utc_to_local


class GroupDetails(tk.Frame):
    def __init__(self, parent, controller, g_id):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.group_id = g_id
        self.group_name = get_group_name(self.group_id, self.controller.get_db_key())
        self.expenses_listbox = None
        self.expenses = []
        self.expenses_id = {}

        self.create_widgets()
        self.load_expense()

    def create_widgets(self):
        gname_label = tk.Label(self, text=self.group_name, font=("Arial", 20, "bold", "underline", "italic"))
        gname_label.pack(fill="x")
        gname_label.config(bg="white", anchor="center", pady=15)

        log_label = tk.Label(self, text="Expense Log:", font=("Arial", 16, "underline"))
        log_label.pack(fill="x", padx=25, pady=5)
        log_label.config(bg="white", anchor="nw")

        self.expenses_listbox = tk.Listbox(self, bg="white", font="Arial 18")
        self.expenses_listbox.pack(fill="both", expand=True, padx=20, pady=0)
        self.expenses_listbox.bind('<<ListboxSelect>>', self.check_selection)

        scroller_v = tk.Scrollbar(self.expenses_listbox, orient=tk.VERTICAL)
        scroller_v.pack(side=tk.RIGHT, fill=tk.Y)
        scroller_v.config(command=self.expenses_listbox.yview)
        self.expenses_listbox.config(yscrollcommand=scroller_v.set)
        scroller_h = tk.Scrollbar(self.expenses_listbox, orient=tk.HORIZONTAL)
        scroller_h.pack(side=tk.BOTTOM, fill=tk.X)
        scroller_h.config(command=self.expenses_listbox.xview)
        self.expenses_listbox.config(xscrollcommand=scroller_h.set)

        buttons_frame = tk.Frame(self, bg="white")
        buttons_frame.pack(fill="x", padx=15, pady=15)
        b1 = tk.Button(buttons_frame, text="Home", command=self.go_home)
        b1.pack(side="left", padx=0)
        b2 = tk.Button(buttons_frame, text="Check Balance", command=self.show_balance)
        b2.pack(side="left", padx=25)
        b3 = tk.Button(buttons_frame, text="View", command=self.expense_details)
        b3.pack(side="left", padx=0)

        b4 = tk.Button(buttons_frame, text="Add", command=self.add_expense)
        b4.pack(side="right", padx=0)
        b5 = tk.Button(buttons_frame, text="Edit", command=self.edit_expense)
        b5.pack(side="right", padx=25)
        b6 = tk.Button(buttons_frame, text="Delete", command=self.delete_expense)
        b6.pack(side="right", padx=0)

    def load_expense(self):
        self.expenses = get_group_expenses(self.group_id, self.controller.get_db_key())
        self.expenses_listbox.delete(0, tk.END)
        for index, i in enumerate(self.expenses):
            expense_id = i[0]
            amount = i[3]
            amount = "$ " + str(amount)
            leading_space = 17 - len(amount)
            amount = " " * leading_space + amount
            description = i[4]
            time = i[5]
            time = utc_to_local(time)
            self.expenses_id[index] = expense_id
            self.expenses_listbox.insert(tk.END, description)
            self.expenses_listbox.insert(tk.END, f"{amount}      {time}")
            self.expenses_listbox.insert(tk.END, "")

    def check_selection(self, _event):
        selected_indices = self.expenses_listbox.curselection()
        if selected_indices:
            selection = selected_indices[0] + 1
            if selection % 3 == 0:
                self.expenses_listbox.selection_clear(selection - 1)
            else:
                if selection % 3 == 1:
                    self.expenses_listbox.selection_set(selection - 1, selection)
                else:
                    self.expenses_listbox.selection_set(selection - 2, selection - 1)

    def add_expense(self):
        self.focus_set()
        self.controller.show_edit_add_expense_details(g_name=self.group_name)

    def edit_expense(self):
        if self.expenses_listbox.curselection():
            t = self.expenses_listbox.curselection()[0]
            t //= 3
            expense_id = self.expenses_id[t]
            self.focus_set()
            self.controller.show_edit_add_expense_details(expense_id=expense_id)
        else:
            messagebox.showerror("Error", "Select any log to edit its details.")

    def delete_expense(self):
        if self.expenses_listbox.curselection():
            t = self.expenses_listbox.curselection()[0]
            t //= 3
            expense_id = self.expenses_id[t]
            delete_expense(expense_id, self.controller.get_db_key())
            self.focus_set()
            self.controller.on_expense_update(self.group_id)
        else:
            messagebox.showerror("Error", "Select any log to delete.")

    def expense_details(self):
        if self.expenses_listbox.curselection():
            t = self.expenses_listbox.curselection()[0]
            t //= 3
            expense_id = self.expenses_id[t]
            self.controller.show_expense_details(expense_id)
        else:
            messagebox.showerror("Error", "Select any log to view its details.")

    def show_balance(self):
        self.focus_set()
        self.controller.show_balance_details(self.group_id)

    def go_home(self):
        self.focus_set()
        self.controller.show_home_page()
