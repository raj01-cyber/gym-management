import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

class PaymentsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame; self.db = db; self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()
        tk.Label(self.parent_frame, text="Process Membership Payments", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(self.parent_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief="groove")
        form_frame.pack(fill="x", pady=(0, 20))

        members = self.db.fetch_all("SELECT MemberID, FirstName, LastName FROM Members")
        self.m_map = {f"{m['FirstName']} {m['LastName']} (ID:{m['MemberID']})": m['MemberID'] for m in members}
        self.m_combo = ttk.Combobox(form_frame, values=list(self.m_map.keys()), state="readonly", width=35)
        self.m_combo.grid(row=0, column=1, padx=5, pady=5)
        if members: self.m_combo.current(0)

        self.amt_entry = ttk.Entry(form_frame); self.amt_entry.grid(row=0, column=3, padx=5, pady=5)
        self.method_combo = ttk.Combobox(form_frame, values=["Credit Card", "Cash Network", "Direct Remit"], state="readonly")
        self.method_combo.grid(row=0, column=5, padx=5, pady=5); self.method_combo.current(0)
        
        tk.Button(form_frame, text="Settle Invoice", bg="#28a745", fg="white", command=self.post_pay).grid(row=1, column=0, columnspan=6, pady=10)

        self.tree = ttk.Treeview(self.parent_frame, columns=("TXN", "Name", "Amt", "Date", "Method"), show="headings")
        for col in self.tree["columns"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for row in self.db.fetch_all("SELECT p.PaymentID, CONCAT(m.FirstName, ' ', m.LastName) as Name, p.Amount, p.PaymentDate, p.PaymentMethod FROM Payments p JOIN Members m ON p.MemberID = m.MemberID ORDER BY p.PaymentID DESC"):
            self.tree.insert("", "end", values=(row['PaymentID'], row['Name'], f"${row['Amount']}", row['PaymentDate'], row['PaymentMethod']))

    def post_pay(self):
        t, r, m = self.m_combo.get(), self.amt_entry.get().strip(), self.method_combo.get()
        if not t or not r: return
        if self.db.execute_query("INSERT INTO Payments (MemberID, Amount, PaymentDate, PaymentMethod) VALUES (%s,%s,%s,%s)", (self.m_map[t], float(r), date.today(), m)):
            messagebox.showinfo("Success", "Transaction committed!")
            self.load_data()