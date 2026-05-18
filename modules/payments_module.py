import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PaymentsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()
        tk.Label(self.parent_frame, text="Process Membership Payments (Pre-Paid Engine)", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(self.parent_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief="groove")
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="Target Profile:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        query = "SELECT m.MemberID, m.FirstName, m.LastName, p.PlanName, p.Cost FROM Members m JOIN Membership_Plans p ON m.PlanID = p.PlanID"
        self.members_data = self.db.fetch_all(query)
        
        self.m_selector_list = [f"{m['FirstName']} {m['LastName']} (Gym-ID: {m['MemberID']} | {m['PlanName']})" for m in self.members_data]
        self.m_combo = ttk.Combobox(form_frame, values=self.m_selector_list, state="readonly", width=55)
        self.m_combo.grid(row=0, column=1, padx=5, pady=5)
        self.m_combo.bind("<<ComboboxSelected>>", self.auto_calculate_billing)

        tk.Label(form_frame, text="Contract Amount ($):", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.amt_entry = ttk.Entry(form_frame, state="disabled") 
        self.amt_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Coverage Period:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.period_combo = ttk.Combobox(form_frame, state="readonly")
        self.period_combo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Settlement Method:", bg="#ffffff").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.method_combo = ttk.Combobox(form_frame, values=["Credit Card", "Cash", "Bank Transfer"], state="readonly")
        self.method_combo.grid(row=1, column=3, padx=5, pady=5); self.method_combo.current(0)
        
        if self.m_selector_list: self.m_combo.current(0); self.auto_calculate_billing(None)
        
        tk.Button(form_frame, text="Authorize Invoice", bg="#28a745", fg="white", command=self.post_pay).grid(row=2, column=0, columnspan=4, pady=10)

        self.tree = ttk.Treeview(self.parent_frame, columns=("TXN ID", "Gym-ID", "Name", "Settled Cost", "Timestamp", "Method", "Coverage Period"), show="headings")
        for col in self.tree["columns"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.load_data()

    def generate_valid_periods(self, is_annual):
        current = datetime.now()
        if is_annual:
            return [f"Year {current.year}", f"Year {current.year + 1}"]
        else:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            periods = []
            for i in range(6): 
                m_idx = (current.month + i - 1) % 12
                y_offset = (current.month + i - 1) // 12
                periods.append(f"{months[m_idx]} {current.year + y_offset}")
            return periods

    def auto_calculate_billing(self, event):
        idx = self.m_combo.current()
        if idx >= 0:
            plan_name = self.members_data[idx]['PlanName']
            target_cost = self.members_data[idx]['Cost']
            
            self.amt_entry.config(state="normal")
            self.amt_entry.delete(0, tk.END)
            self.amt_entry.insert(0, str(target_cost))
            self.amt_entry.config(state="disabled")

            is_annual = "Annual" in plan_name
            valid_periods = self.generate_valid_periods(is_annual)
            self.period_combo.config(values=valid_periods)
            self.period_combo.current(0)

    def load_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        query = "SELECT p.PaymentID, p.MemberID, CONCAT(m.FirstName, ' ', m.LastName) as Name, p.Amount, p.PaymentDate, p.PaymentMethod, p.CoveredMonth FROM Payments p JOIN Members m ON p.MemberID = m.MemberID ORDER BY p.PaymentID DESC"
        for row in self.db.fetch_all(query):
            self.tree.insert("", "end", values=(row['PaymentID'], row['MemberID'], row['Name'], f"${row['Amount']}", row['PaymentDate'], row['PaymentMethod'], row['CoveredMonth']))

    def post_pay(self):
        idx = self.m_combo.current()
        if idx < 0: return
        
        member_id = self.members_data[idx]['MemberID']
        cost = self.members_data[idx]['Cost']
        period = self.period_combo.get()
        method = self.method_combo.get()
        
        double_check = self.db.fetch_all("SELECT PaymentID FROM Payments WHERE MemberID = %s AND CoveredMonth = %s", (member_id, period))
        if double_check:
            return messagebox.showerror("Billing Fraud Prevention", f"This member has already remitted payment for {period}.")
        
        query = "INSERT INTO Payments (MemberID, Amount, PaymentDate, PaymentMethod, CoveredMonth, BillingPeriod) VALUES (%s,%s,%s,%s,%s,%s)"
        if self.db.execute_query(query, (member_id, cost, datetime.now().strftime('%Y-%m-%d'), method, period, "Pre-Paid")):
            messagebox.showinfo("Success", f"Payment for {period} authorized successfully!")
            self.load_data()