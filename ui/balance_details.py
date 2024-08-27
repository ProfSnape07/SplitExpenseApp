import tkinter as tk
from tkinter import messagebox

from database import get_group_name, update_member_debts_assets, get_member_debts_assets, get_profile_name, \
    amount_0_member_debts_assets


class BalanceDetails(tk.Frame):
    def __init__(self, parent, controller, group_id):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.group_id = group_id
        self.group_name = get_group_name(self.group_id)
        self.balance_listbox = None
        self.not_available_for_selection = []
        self.selected_value_dict = {}
        self.flag = False

        self.create_widgets()

    def create_widgets(self):
        gname_label = tk.Label(self, text=self.group_name, font=("Arial", 20, "bold", "underline", "italic"))
        gname_label.pack(fill="x")
        gname_label.config(bg="white", anchor="center", pady=15)

        log_label = tk.Label(self, text="Balance:", font=("Arial", 16, "underline"))
        log_label.pack(fill="x", padx=35, pady=0)
        log_label.config(bg="white", anchor="nw")

        self.balance_listbox = tk.Listbox(self, bg="#ededed", font=("Helvetica", 18))
        self.balance_listbox.pack(fill="both", expand=True, padx=35, pady=15)
        self.balance_listbox.bind('<<ListboxSelect>>', self.check_selection)

        scroller_v = tk.Scrollbar(self.balance_listbox, orient=tk.VERTICAL)
        scroller_v.pack(side=tk.RIGHT, fill=tk.Y)
        scroller_v.config(command=self.balance_listbox.yview)
        self.balance_listbox.config(yscrollcommand=scroller_v.set)
        scroller_h = tk.Scrollbar(self.balance_listbox, orient=tk.HORIZONTAL)
        scroller_h.pack(side=tk.BOTTOM, fill=tk.X)
        scroller_h.config(command=self.balance_listbox.xview)
        self.balance_listbox.config(xscrollcommand=scroller_h.set)

        self.load_balance()

        buttons_frame = tk.Frame(self, bg="white")
        buttons_frame.pack(fill="both", padx=35, pady=10)

        b1 = tk.Button(buttons_frame, text="Home", command=self.go_home)
        b1.pack(side="left", padx=0)
        b2 = tk.Button(buttons_frame, text="Back", command=self.go_back)
        b2.pack(side="left", padx=15)
        b3 = tk.Button(buttons_frame, text="Simplify", command=self.simplify_balance)
        b3.pack(side="right", padx=0)
        b4 = tk.Button(buttons_frame, text="Settle", command=self.settle)
        b4.pack(side="right", padx=15)

    def load_balance(self):
        self.balance_listbox.delete(0, tk.END)
        self.not_available_for_selection.clear()
        self.selected_value_dict.clear()
        index = 0
        member_debts_assets = get_member_debts_assets(self.group_id)
        profile_assets = {}
        profile_debts = {}
        for i in member_debts_assets:
            profile_id = i[1]
            if profile_id not in profile_assets:
                profile_assets[profile_id] = []
                profile_assets[profile_id].append((i[2], i[3]))
            else:
                profile_assets[profile_id].append((i[2], i[3]))
        for profile_id in profile_assets.keys():
            transactions = profile_assets[profile_id]
            total_assets = sum(i[1] for i in transactions)
            total_assets = round(total_assets, 2)
            receiver_name = get_profile_name(profile_id)
            self.balance_listbox.insert(tk.END, f"{receiver_name} will get $ {format(total_assets, ".2f")}:")
            self.not_available_for_selection.append(index)
            index += 1
            for transaction in transactions:
                payee_id = transaction[0]
                payee_name = get_profile_name(payee_id)
                amount = transaction[1]
                debt_amount = amount
                amount = format(amount, ".2f")
                amount = "$ " + str(amount)
                leading_space = 17 - len(amount)
                amount = " " * leading_space + amount
                self.balance_listbox.insert(tk.END, f"{amount} from {payee_name}")
                self.selected_value_dict[index] = [profile_id, payee_id, debt_amount]
                index += 1
                if payee_id not in profile_debts:
                    profile_debts[payee_id] = []
                    profile_debts[payee_id].append((profile_id, debt_amount))
                else:
                    profile_debts[payee_id].append((profile_id, debt_amount))
            self.balance_listbox.insert(tk.END, "")
            self.not_available_for_selection.append(index)
            index += 1
        self.balance_listbox.insert(tk.END, "-" * 60)
        self.not_available_for_selection.append(index)
        index += 1
        self.balance_listbox.insert(tk.END, "")
        self.not_available_for_selection.append(index)
        index += 1
        for profile_id in profile_debts.keys():
            transactions = profile_debts[profile_id]
            total_debts = sum(i[1] for i in transactions)
            total_debts = round(total_debts, 2)
            payee_name = get_profile_name(profile_id)
            self.balance_listbox.insert(tk.END, f"{payee_name} will pay $ {format(total_debts, ".2f")}:")
            self.not_available_for_selection.append(index)
            index += 1
            for transaction in transactions:
                receiver_id = transaction[0]
                receiver_name = get_profile_name(receiver_id)
                amount = this_debt = transaction[1]
                amount = format(amount, ".2f")
                amount = "$ " + str(amount)
                leading_space = 17 - len(amount)
                amount = " " * leading_space + amount
                self.balance_listbox.insert(tk.END, f"{amount} to {receiver_name}")
                self.selected_value_dict[index] = [receiver_id, profile_id, this_debt]
                index += 1
            self.balance_listbox.insert(tk.END, "")
            self.not_available_for_selection.append(index)
            index += 1

    def simplify_balance(self):
        self.flag = True
        debt_assets = {}  # debt_assets[member_id] = debt/assets
        debt_dict = {}
        assets_dict = {}
        transactions = get_member_debts_assets(self.group_id)
        amount_0_member_debts_assets(self.group_id)
        for transaction in transactions:
            receiver_id = transaction[1]
            payee_id = transaction[2]
            amount = transaction[3]
            if receiver_id not in debt_assets:
                debt_assets[receiver_id] = 0
            debt_assets[receiver_id] += amount
            if payee_id not in debt_assets:
                debt_assets[payee_id] = 0
            debt_assets[payee_id] -= amount

        for profile_id in debt_assets.keys():
            if debt_assets[profile_id] > 0:
                assets_dict[profile_id] = debt_assets[profile_id]
            elif debt_assets[profile_id] < 0:
                debt_dict[profile_id] = debt_assets[profile_id]
        for receiver_id in assets_dict.keys():
            for payee_id in debt_dict.keys():
                assets = assets_dict[receiver_id]
                debt = debt_dict[payee_id]
                debt = abs(debt)
                if assets > debt:
                    update_member_debts_assets(self.group_id, receiver_id, payee_id, debt)
                    assets_dict[receiver_id] -= debt
                    debt_dict[payee_id] += debt
                # elif assets <= debt:
                else:
                    update_member_debts_assets(self.group_id, receiver_id, payee_id, assets)
                    assets_dict[receiver_id] -= assets
                    debt_dict[payee_id] += assets
                    break
        self.load_balance()

    def go_home(self):
        self.focus_set()
        self.controller.show_home_page()

    def go_back(self):
        self.focus_set()
        self.controller.show_group_details(self.group_id)

    def settle(self):
        self.focus_set()
        if self.balance_listbox.curselection():
            if not self.flag:
                need_simplify = messagebox.askyesno("Careful", "It is advisable to first Simplify debt before "
                                                               "settling it.\nDo you want to go back and Simplify?")
                if need_simplify:
                    return
                else:
                    self.flag = True
            selected_indices = self.balance_listbox.curselection()
            selection = selected_indices[0]
            values = self.selected_value_dict[selection]
            self.controller.show_edit_add_expense_details(grpa=[self.group_id, values[0], values[1], values[2]])
        else:
            messagebox.showerror("Error", "Select any log to settle it.")

    def check_selection(self, _event):
        selected_indices = self.balance_listbox.curselection()
        if selected_indices:
            selection = selected_indices[0]
            if selection in self.not_available_for_selection:
                self.balance_listbox.selection_clear(selection)
