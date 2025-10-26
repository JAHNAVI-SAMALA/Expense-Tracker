import re
import json
import datetime
import bcrypt
import os

class Transaction:
    def __init__(self, ttype, name, amount, category, date, friends_split=None):
        self.ttype = ttype
        self.name = name
        self.amount = amount
        self.category = category
        self.date = date
        self.friends_split = friends_split if friends_split else {}

class Account:
    def __init__(self, name, initial_balance=0):
        self.name = name
        self.init_balance = initial_balance
        self.transactions = []
        self.receivables = {}
        self.balance = initial_balance

    def recompute(self):
        self.balance = self.init_balance
        self.receivables = {}
        for t in self.transactions:
            if t.ttype == 'splitwise':
                self.balance -= t.amount
                total_share = sum(t.friends_split.values())
                for friend, share in t.friends_split.items():
                    if friend.lower() != self.name.lower():
                        owed_amount = t.amount * share / total_share
                        self.receivables[friend] = self.receivables.get(friend, 0) + owed_amount
                continue
            if t.ttype == 'income':
                match = re.match(r"paid by (.+)", t.name.lower())
                friend = None
                if match:
                    friend = match.group(1).strip()
                if friend and friend in self.receivables:
                    self.receivables[friend] -= t.amount
                    if self.receivables[friend] <= 0:
                        del self.receivables[friend]
                self.balance += t.amount
            elif t.ttype == 'expense':
                self.balance -= t.amount

    def owed_balance(self):
        return sum(self.receivables.values())

class ExpenseTracker:
    def __init__(self):
        self.user_account = None
        self.user_file = ""
        self.users_file = "users.json"
        self.users = self.load_users()

    # User management

    def load_users(self):
        if not os.path.exists(self.users_file):
            return {}
        with open(self.users_file, "r") as f:
            return json.load(f)

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f)

    def password_check(self, username, password):
        hashed = self.users.get(username)
        if not hashed:
            return False
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def add_user(self, username, password, initial_balance):
        if username in self.users:
            return False
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode(), salt).decode()
        self.users[username] = hashed_pw
        self.save_users()

        self.user_account = Account(username, initial_balance)
        self.user_file = f"user_{username}.json"
        self.save_user_data()
        return True

    def login_user(self, username, password):
        if not self.password_check(username, password):
            return False
        self.user_file = f"user_{username}.json"
        self.load_user_data()
        return True

    # Transaction management

    def add_transaction(self, ttype, name, amount, category, date, friends_split=None):
        if not self.user_account:
            return
        if friends_split and ttype == 'splitwise':
            t = Transaction('splitwise', name, amount, category, date, friends_split)
            self.user_account.transactions.append(t)
        else:
            t = Transaction(ttype, name, amount, category, date)
            self.user_account.transactions.append(t)
        if friends_split:
            # Optionally track known friends
            pass
        self.user_account.recompute()

    def delete_transaction(self, idx):
        if self.user_account and 0 <= idx < len(self.user_account.transactions):
            del self.user_account.transactions[idx]
            self.user_account.recompute()

    def save_user_data(self):
        if not self.user_account:
            return
        data = {
            "user_name": self.user_account.name,
            "initial_balance": self.user_account.init_balance,
            "transactions": [
                {
                    "ttype": t.ttype,
                    "name": t.name,
                    "amount": t.amount,
                    "category": t.category,
                    "date": t.date.strftime("%Y-%m-%d") if isinstance(t.date, datetime.date) else str(t.date),
                    "friends_split": t.friends_split
                } for t in self.user_account.transactions
            ]
        }
        with open(self.user_file, "w") as f:
            json.dump(data, f)

    def load_user_data(self):
        if not os.path.exists(self.user_file):
            # No data file, means new user with initial balance
            return
        with open(self.user_file, "r") as f:
            data = json.load(f)
        self.user_account = Account(data["user_name"], data["initial_balance"])
        for t in data["transactions"]:
            date = datetime.datetime.strptime(t["date"], "%Y-%m-%d").date()
            self.add_transaction(
                t["ttype"], t["name"], t["amount"], t["category"], date, t.get("friends_split", None)
            )

    def get_transactions(self):
        if not self.user_account:
            return []
        return self.user_account.transactions

    @property
    def available_balance(self):
        if not self.user_account:
            return 0
        return self.user_account.balance

    @property
    def owed_balance(self):
        if not self.user_account:
            return 0
        return self.user_account.owed_balance()

    @property
    def receivables(self):
        if not self.user_account:
            return {}
        return {f: a for f, a in self.user_account.receivables.items() if a > 0}
