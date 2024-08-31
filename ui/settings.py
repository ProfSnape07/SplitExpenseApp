import os
import shutil
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox


class Settings(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.config(bg="white")
        self.controller = controller

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self, padx=35, pady=65, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        export_backup = tk.Button(frame, text="Export Backup", height=2, width=15,
                                  font=("Monotype Corsiva", 18, "bold"), command=self.export_backup)
        export_backup.pack()

        delete = tk.Button(frame, text="Delete", height=2, width=15, font=("Monotype Corsiva", 18, "bold"),
                           command=self.delete_db)
        delete.pack(pady=65)

        delete = tk.Button(frame, text="Home", height=2, width=15, font=("Monotype Corsiva", 18, "bold"),
                           command=self.go_home)
        delete.pack(pady=0)

    @staticmethod
    def export_backup():
        data_file = "split_expense.db"
        full_data_file_path = os.path.join(os.getcwd(), data_file)
        initial_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_types = [("Backup file", "*.db"), ("All files", "*.*")]
        current_time = datetime.now()
        backup_file_name = f"backup split expense {current_time.strftime("%Y-%m-%d-%H-%M")}.db"
        filepath = filedialog.asksaveasfilename(title="Select a backup file", initialdir=initial_dir,
                                                filetypes=file_types, initialfile=backup_file_name)
        if filepath:
            try:
                shutil.copyfile(full_data_file_path, filepath)
                messagebox.showinfo("Success", "You have successfully exported backup.")
            except shutil.SameFileError:
                pass
        else:
            messagebox.showerror("Error", "Backup cancelled.")

    def delete_db(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete everything?"):
            data_file = "split_expense.db"
            full_data_file_path = os.path.join(os.getcwd(), data_file)
            os.remove(full_data_file_path)
            messagebox.showinfo("Deletion Success", "The database has been deleted successfully.")
            self.controller.show_initial_setup()

    def go_home(self):
        self.focus_set()
        self.controller.show_home_page()
