import os
import tkinter as tk

from database import check_database_structure, check_password_required
from ui.add_expense import AddExpense
from ui.balance_details import BalanceDetails
from ui.create_group import CreateGroup
from ui.create_profile import CreateProfile
from ui.encryption_key import EncryptionKey
from ui.expense_details import ExpenseDetails
from ui.group_details import GroupDetails
from ui.homepage import HomePage
from ui.initial_page import InitialSetup
from ui.settings import Settings


class SplitExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SplitExpense")
        self.geometry("600x600")
        icon_path = "res\\icon.ico"
        full_icon_path = os.path.join(os.getcwd(), icon_path)
        self.iconbitmap(full_icon_path)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = None
        self.frames = {}
        self.db_key = None

        self.create_widgets()

    def create_widgets(self):
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        if check_database_structure():
            if check_password_required():
                self.show_encryption_key()
            else:
                self.show_home_page()
        else:
            try:
                data_file = "split_expense.db"
                full_data_file_path = os.path.join(os.getcwd(), data_file)
                os.remove(full_data_file_path)
            except FileNotFoundError and PermissionError:
                pass
            self.show_initial_setup()

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget()

        frame = self.frames[frame_name]
        frame.pack(fill="both", expand=True)

    def set_db_key(self, key):
        self.db_key = key

    def get_db_key(self):
        return self.db_key

    def show_initial_setup(self):
        self.frames["InitialSetup"] = InitialSetup(self.container, self)
        self.show_frame("InitialSetup")

    def show_encryption_key(self):
        self.frames["EncryptionKey"] = EncryptionKey(self.container, self)
        self.show_frame("EncryptionKey")

    def show_home_page(self):
        if "HomePage" not in self.frames:
            self.frames["HomePage"] = HomePage(self.container, self)
        self.show_frame("HomePage")

    def refresh_homepage(self):
        self.frames["HomePage"] = HomePage(self.container, self)

    def show_create_profile(self):
        if "CreateProfile" not in self.frames:
            self.frames["CreateProfile"] = CreateProfile(self.container, self)
        self.show_frame("CreateProfile")

    def show_create_group(self):
        if "CreateGroup" not in self.frames:
            self.frames["CreateGroup"] = CreateGroup(self.container, self)
        self.show_frame("CreateGroup")

    def show_edit_add_expense_details(self, expense_id: int = None, g_name: str = None,
                                      grpa: list[int, int, int, float] = None):
        if "CreateExpense" not in self.frames:
            self.frames["CreateExpense"] = AddExpense(self.container, self)
        if expense_id:
            self.frames["CreateExpense"].edit_expense_id(expense_id)
        elif g_name:
            self.frames["CreateExpense"].add_in_gname(g_name)
        elif grpa:
            group_id = grpa[0]
            receiver_id = grpa[1]
            payee_id = grpa[2]
            amount = grpa[3]
            self.frames["CreateExpense"].settle_expense(group_id, receiver_id, payee_id, amount)
        else:
            self.frames["CreateExpense"].clear_entry()
        self.show_frame("CreateExpense")

    def show_group_details(self, g_id):
        if g_id not in self.frames:
            self.frames[g_id] = GroupDetails(self.container, self, g_id)
        self.show_frame(g_id)

    def show_expense_details(self, expense_id):
        self.frames["ExpenseDetails"] = ExpenseDetails(self.container, self, expense_id)
        self.show_frame("ExpenseDetails")

    def show_balance_details(self, group_id):
        if f"g_id:{group_id}" not in self.frames:
            self.frames[f"g_id:{group_id}"] = BalanceDetails(self.container, self, group_id)
        self.show_frame(f"g_id:{group_id}")

    def show_settings(self, home_on=True):
        if home_on:
            self.frames["Settings"] = Settings(self.container, self)
        else:
            self.frames["Settings"] = Settings(self.container, self, False)
        self.show_frame("Settings")

    def on_group_update(self):
        self.refresh_homepage()
        if "CreateExpense" in self.frames:
            self.frames["CreateExpense"].load_groups()

    def on_profile_update(self):
        if "CreateGroup" in self.frames:
            self.frames["CreateGroup"].load_all_profiles()

    def on_expense_update(self, group_id):
        self.refresh_homepage()
        if group_id in self.frames:
            self.frames[group_id].load_expense()
        if f"g_id:{group_id}" in self.frames:
            self.frames[f"g_id:{group_id}"].load_balance()


if __name__ == "__main__":
    app = SplitExpenseApp()
    app.mainloop()
