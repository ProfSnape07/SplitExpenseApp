import tkinter as tk
from tkinter import messagebox

from database import get_expense, get_profile_involved, get_profile_name, utc_to_local, delete_expense, \
    get_group_id_expense_id, get_group_name


class ExpenseDetails(tk.Frame):
    def __init__(self, parent, controller, expense_id):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.expense_id = expense_id
        self.group_name = self.group_name(expense_id)
        self.expenses_description_textbox = None
        self.group_id = None

        self.create_widgets()
        self.load_expense_details()

    @staticmethod
    def group_name(expense_id):
        group_id = get_group_id_expense_id(expense_id)
        group_name = get_group_name(group_id)
        return group_name

    def create_widgets(self):
        gname_label = tk.Label(self, text=self.group_name, font=("Arial", 20, "bold", "underline", "italic"))
        gname_label.pack(fill="x")
        gname_label.config(bg="white", anchor="center", pady=15)

        log_label = tk.Label(self, text="Expense Details:", font=("Arial", 16, "underline"))
        log_label.pack(fill="x", padx=25, pady=5)
        log_label.config(bg="white", anchor="nw")

        text_frame = tk.Frame(self, highlightthickness=0, bg="#ededed")
        text_frame.pack(fill="both", expand=True, padx=35, pady=5)
        self.expenses_description_textbox = tk.Text(text_frame, padx=5, pady=5, font=("Helvetica", 18), wrap="word",
                                                    borderwidth=2, height=11, width=30, bg="#ededed",
                                                    highlightbackground="blue")
        self.expenses_description_textbox.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        scroller_v = tk.Scrollbar(text_frame, orient="vertical", command=self.expenses_description_textbox.yview)
        scroller_v.config(activebackground="red", highlightthickness=0)
        scroller_v.pack(side="right", fill="y")
        self.expenses_description_textbox.config(yscrollcommand=scroller_v.set)

        buttons_frame = tk.Frame(self, bg="white")
        buttons_frame.pack(fill="both", padx=35, pady=10)
        b1 = tk.Button(buttons_frame, text="Home", command=self.go_home)
        b1.pack(side="left", padx=0)
        b2 = tk.Button(buttons_frame, text="Back", command=self.go_back)
        b2.pack(side="left", padx=15)
        b3 = tk.Button(buttons_frame, text="Edit Expense", command=self.edit_expense)
        b3.pack(side="right", padx=0)
        b4 = tk.Button(buttons_frame, text="Delete Expense", command=self.delete_expense)
        b4.pack(side="right", padx=15)

    def load_expense_details(self):
        expense_id = self.expense_id
        expense = get_expense(expense_id)
        profile_involved_dict = get_profile_involved(expense_id)
        profile_involved_list = list(profile_involved_dict.keys())
        profile_name_list = [(get_profile_name(i), i) for i in profile_involved_list]

        self.group_id = expense[1]
        payee_id = expense[2]
        payee_name = get_profile_name(payee_id)
        amount = expense[3]
        description = expense[4]
        date = expense[5]
        date = utc_to_local(date)

        text_to_display = (f"Description: {description}\n\nDate & Time: {date}\n\nTotal Amount: ${amount}\n\nPaid By: "
                           f"{payee_name}\n\nIndividual Share:\n")
        text_to_display += ''.join(f"   ${profile_involved_dict[i[1]]}:     {i[0]}\n" for i in profile_name_list)
        text_to_display = text_to_display[:-1]

        self.expenses_description_textbox.insert(tk.END, text_to_display)
        self.expenses_description_textbox.config(state="disabled")

    def go_home(self):
        self.focus_set()
        self.controller.show_home_page()

    def go_back(self):
        self.focus_set()
        self.controller.show_group_details(self.group_id)

    def delete_expense(self):
        expense_id = self.expense_id
        delete_expense(expense_id)
        self.controller.on_expense_update(self.group_id)
        messagebox.showinfo("Success", "Expense Deleted")
        self.go_back()

    def edit_expense(self):
        self.controller.show_edit_add_expense_details(expense_id=self.expense_id)
