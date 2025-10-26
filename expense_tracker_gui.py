from expense_tracker_backend import ExpenseTracker
import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker Login")
        self.tracker = ExpenseTracker()
        self.login_screen()

    def login_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=20)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="Username:").grid(row=0, column=0)
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var).grid(row=0, column=1)

        ttk.Label(frame, text="Password:").grid(row=1, column=0)
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="*").grid(row=1, column=1)

        ttk.Button(frame, text="Login", command=self.try_login).grid(row=2, column=0, sticky=tk.W+tk.E)
        ttk.Button(frame, text="Register", command=self.register_screen).grid(row=2, column=1, sticky=tk.W+tk.E)

    def register_screen(self):
        self.clear_root()
        frame = ttk.Frame(self.root, padding=20)
        frame.grid(row=0, column=0)

        ttk.Label(frame, text="New Username:").grid(row=0, column=0)
        self.reg_username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reg_username_var).grid(row=0, column=1)

        ttk.Label(frame, text="Password:").grid(row=1, column=0)
        self.reg_password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reg_password_var, show="*").grid(row=1, column=1)

        ttk.Label(frame, text="Initial Balance:").grid(row=2, column=0)
        self.reg_balance_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.reg_balance_var).grid(row=2, column=1)

        ttk.Button(frame, text="Register", command=self.try_register).grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E)
        ttk.Button(frame, text="Back to Login", command=self.login_screen).grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E)

    def try_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        if self.tracker.login_user(username, password):
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def try_register(self):
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get()
        try:
            init_balance = float(self.reg_balance_var.get())
        except Exception:
            messagebox.showerror("Error", "Enter a valid number for initial balance.")
            return
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return
        if self.tracker.add_user(username, password, init_balance):
            messagebox.showinfo("Success", "User registered! Please login.")
            self.login_screen()
        else:
            messagebox.showerror("Error", "Username already exists.")

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_screen(self):
        self.clear_root()
        self.root.title(f"Expense Tracker - User {self.tracker.user_account.name}")
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Type").grid(row=0, column=0)
        self.type_var = tk.StringVar(value='expense')
        ttk.Radiobutton(frame, text="Expense", variable=self.type_var, value='expense').grid(row=0, column=1)
        ttk.Radiobutton(frame, text="Income", variable=self.type_var, value='income').grid(row=0, column=2)
        ttk.Radiobutton(frame, text="Splitwise", variable=self.type_var, value='splitwise').grid(row=0, column=3)

        ttk.Label(frame, text="Name").grid(row=1, column=0)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var).grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Amount").grid(row=2, column=0)
        self.amount_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.amount_var).grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Category").grid(row=3, column=0)
        self.category_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.category_var).grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=4, column=0)
        self.date_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.date_var).grid(row=4, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Friends Split (name:share,...)").grid(row=5, column=0)
        self.friends_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.friends_var).grid(row=5, column=1, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Add Transaction", command=self.add_transaction).grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Delete Selected", command=self.delete_selected).grid(row=6, column=2, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Button(frame, text="Done", command=self.done_action).grid(row=6, column=4, sticky=(tk.W, tk.E))

        self.tree = ttk.Treeview(frame,
                                 columns=("Type", "Name", "Amount", "Category", "Date", "Split"),
                                 show="headings", height=10)
        for col in ("Type", "Name", "Amount", "Category", "Date", "Split"):
            self.tree.heading(col, text=col)
        self.tree.grid(row=7, column=0, columnspan=5, sticky=(tk.W, tk.E))

        self.balance_label = ttk.Label(frame, text="Available Balance: ₹0.00", font=(None, 12, "bold"))
        self.balance_label.grid(row=8, column=0, columnspan=5)
        self.owed_label = ttk.Label(frame, text="Owed Balance: ₹0.00", font=(None, 12, "bold"), foreground="blue")
        self.owed_label.grid(row=9, column=0, columnspan=5)
        self.receivables_label = ttk.Label(frame, text="", font=(None, 10), foreground="green")
        self.receivables_label.grid(row=10, column=0, columnspan=5)

    def add_transaction(self):
        ttype = self.type_var.get()
        name = self.name_var.get().strip()
        amount = self.amount_var.get()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()
        friends_str = self.friends_var.get().strip()
        if not name or not amount or not category or not date_str:
            messagebox.showerror("Missing Data", "Please fill all required fields")
            return
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            amount = float(amount)
        except Exception:
            messagebox.showerror("Invalid Input", "Please check the amount and date format (YYYY-MM-DD).")
            return
        friends_split = None
        if ttype == 'splitwise':
            if not friends_str:
                messagebox.showerror("Splitwise Required", "Please enter Friends Split for splitwise.")
                return
            friends_split = self.parse_friends(friends_str)
            if friends_split is None or self.tracker.user_account.name.lower() not in [k.lower() for k in friends_split.keys()]:
                messagebox.showerror("Invalid Split", "Enter as 'name:share', must include your name.")
                return
        self.tracker.add_transaction(ttype, name, amount, category, date, friends_split)
        self.tracker.save_user_data()
        self.clear_inputs()
        self.refresh_transactions()

    def delete_selected(self):
        selected = self.tree.selection()
        if selected:
            idx = int(self.tree.item(selected[0], "tags")[0])
            self.tracker.delete_transaction(idx)
            self.tracker.save_user_data()
            self.refresh_transactions()
        else:
            messagebox.showinfo("Delete", "Please select a transaction to delete.")

    def done_action(self):
        self.tracker.save_user_data()
        self.root.destroy()

    def parse_friends(self, friends_str):
        try:
            pairs = friends_str.split(",")
            friends = {}
            for pair in pairs:
                friend, share = pair.split(":")
                friends[friend.strip()] = float(share.strip())
            return friends
        except Exception:
            return None

    def refresh_transactions(self):
        self.tree.delete(*self.tree.get_children())
        for idx, t in enumerate(self.tracker.get_transactions()):
            split_disp = ", ".join([f"{f}:{s}" for f, s in t.friends_split.items()]) if t.ttype == 'splitwise' and t.friends_split else ""
            self.tree.insert("", tk.END, values=(t.ttype, t.name, f"₹{t.amount:.2f}", t.category, t.date, split_disp), tags=(str(idx),))
        available = self.tracker.available_balance
        owed = self.tracker.owed_balance
        self.balance_label.config(text=f"Available Balance for {self.tracker.user_account.name}: ₹{available:.2f}")
        self.owed_label.config(text=f"Owed Balance (Friends owe you): ₹{owed:.2f}")
        if self.tracker.receivables:
            receivables_lines = [f"{friend}: ₹{amount:.2f}" for friend, amount in self.tracker.receivables.items()]
            receivables_text = "Friends owe you ➔ " + ", ".join(receivables_lines)
        else:
            receivables_text = "Friends owe you: None"
        self.receivables_label.config(text=receivables_text)

    def clear_inputs(self):
        self.name_var.set("")
        self.amount_var.set("")
        self.category_var.set("")
        self.date_var.set("")
        self.friends_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()
