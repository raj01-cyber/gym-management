import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

class PaymentsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()

        tk.Label(self.parent_frame, text="Process Membership Payments", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(self.parent_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief="groove")
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="Select Profile Target:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        members = self.db.fetch_all("SELECT MemberID, FirstName, LastName FROM Members")
        self.member_map = {f"{m['FirstName']} {m['LastName']} (ID: {m['MemberID']})": m['MemberID'] for m in members}
        self.member_combo = ttk.Combobox(form_frame, values=list(self.member_map.keys()), state="readonly", width=35)
        if members: self.member_combo.current(0)
        self.member_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Amount Received ($):", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.amt_entry = ttk.Entry(form_frame)
        self.amt_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Settlement Method:", bg="#ffffff").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.method_combo = ttk.Combobox(form_frame, values=["Credit Card", "Cash Network", "Direct Remit"], state="readonly")
        self.method_combo.current(0)
        self.method_combo.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(form_frame, text="Authorize Invoice Settlement", bg="#28a745", fg="white", command=self.post_transaction).grid(row=1, column=0, columnspan=6, pady=10)

        tree_frame = tk.Frame(self.parent_frame)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("TXN ID", "Payer Name", "Settle Amount", "Timestamp", "Method"), show="headings")
        for col in self.tree["columns"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.load_transactions()

    def load_transactions(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        query = "SELECT p.PaymentID, CONCAT(m.FirstName, ' ', m.LastName) as Name, p.Amount, p.PaymentDate, p.PaymentMethod FROM Payments p JOIN Members m ON p.MemberID = m.MemberID ORDER BY p.PaymentID DESC"
        for row in self.db.fetch_all(query):
            self.tree.insert("", "end", values=(row['PaymentID'], row['Name'], f"${row['Amount']}", row['PaymentDate'], row['PaymentMethod']))

    def post_transaction(self):
        target = self.member_combo.get()
        raw_amt = self.amt_entry.get().strip()
        method = self.method_combo.get()

        if not target or not raw_amt: return messagebox.showwarning("Validation Error", "All transaction attributes required.")
        try:
            val = float(raw_amt)
        except ValueError:
            return messagebox.showerror("Format Error", "Amount field requires numeric format entries.")

        query = "INSERT INTO Payments (MemberID, Amount, PaymentDate, PaymentMethod) VALUES (%s, %s, %s, %s)"
        if self.db.execute_query(query, (self.member_map[target], val, date.today(), method)):
            messagebox.showinfo("Success", "Transaction committed to system ledger!")
            self.amt_entry.delete(0, tk.END)
            self.load_transactions()