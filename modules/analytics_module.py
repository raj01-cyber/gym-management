import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class AnalyticsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()
        
        tk.Label(self.parent_frame, text="Time-Series Business Intelligence", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        ctrl_frame = tk.Frame(self.parent_frame, bg="#f4f4f9")
        ctrl_frame.pack(fill="x", pady=5)
        
        filter_frame = tk.Frame(ctrl_frame, bg="#f4f4f9")
        filter_frame.pack(fill="x", pady=5)
        
        tk.Label(filter_frame, text="Filter Year:", bg="#f4f4f9").pack(side="left")
        current_year = datetime.now().year
        self.year_combo = ttk.Combobox(filter_frame, values=["All Time"] + [str(y) for y in range(current_year-1, current_year+4)], state="readonly", width=12)
        self.year_combo.current(0)
        self.year_combo.pack(side="left", padx=5)
        
        tk.Label(filter_frame, text="Filter Month:", bg="#f4f4f9").pack(side="left", padx=(15, 0))
        self.months_map = {"All Months": None, "01 - January": 1, "02 - February": 2, "03 - March": 3, "04 - April": 4, "05 - May": 5, "06 - June": 6, "07 - July": 7, "08 - August": 8, "09 - September": 9, "10 - October": 10, "11 - November": 11, "12 - December": 12}
        self.month_combo = ttk.Combobox(filter_frame, values=list(self.months_map.keys()), state="readonly", width=15)
        self.month_combo.current(0)
        self.month_combo.pack(side="left", padx=5)

        action_frame = tk.Frame(ctrl_frame, bg="#f4f4f9")
        action_frame.pack(fill="x", pady=10)

        self.rep_select = ttk.Combobox(action_frame, values=["True Cash by Plan", "Monthly Revenue Timeline", "System Ledger Streams"], state="readonly", width=30)
        self.rep_select.current(1)
        self.rep_select.pack(side="left", padx=5)
        
        tk.Button(action_frame, text="Run Aggregates", bg="#007bff", fg="white", command=self.run_aggregates).pack(side="left", padx=5)
        tk.Button(action_frame, text="Export CSV", bg="#28a745", fg="white", command=self.export_csv).pack(side="left", padx=5)
        tk.Button(action_frame, text="Launch Visual Dashboards", bg="#6f42c1", fg="white", command=self.render_charts).pack(side="left", padx=20)

        self.table_container = tk.Frame(self.parent_frame)
        self.table_container.pack(fill="both", expand=True, pady=10)
        self.tree = ttk.Treeview(self.table_container, show="headings")
        self.tree.pack(fill="both", expand=True)

    def get_date_filters(self):
        """Constructs safe parameterized SQL filters based on UI dropdowns."""
        year_val = self.year_combo.get()
        month_val = self.months_map[self.month_combo.get()]
        conditions, params = [], []

        if year_val != "All Time":
            conditions.append("YEAR(PaymentDate) = %s")
            params.append(int(year_val))
        if month_val is not None:
            conditions.append("MONTH(PaymentDate) = %s")
            params.append(month_val)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, params

    def run_aggregates(self):
        mode = self.rep_select.get()
        self.tree.delete(*self.tree.get_children())
        where_clause, params = self.get_date_filters()

        if mode == "True Cash by Plan":
            self.tree["columns"] = ("Plan Option", "Unique Payers", "True Cash Remitted")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            query = f"""SELECT p.PlanName, COUNT(DISTINCT pay.MemberID) as Base, COALESCE(SUM(pay.Amount), 0) as TrueRevenue 
                       FROM Payments pay 
                       JOIN Members m ON pay.MemberID = m.MemberID 
                       JOIN Membership_Plans p ON m.PlanID = p.PlanID 
                       WHERE {where_clause} 
                       GROUP BY p.PlanID"""
            for r in self.db.fetch_all(query, tuple(params)):
                self.tree.insert("", "end", values=(r['PlanName'], r['Base'], f"${r['TrueRevenue']}"))

        elif mode == "Monthly Revenue Timeline":
            self.tree["columns"] = ("Year-Month", "Total Revenue", "Transactions Count")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            query = f"""SELECT DATE_FORMAT(PaymentDate, '%Y-%m') as MonthPeriod, COALESCE(SUM(Amount), 0) as TotalRev, COUNT(PaymentID) as TxnCount 
                       FROM Payments 
                       WHERE {where_clause} 
                       GROUP BY MonthPeriod 
                       ORDER BY MonthPeriod DESC"""
            for r in self.db.fetch_all(query, tuple(params)):
                self.tree.insert("", "end", values=(r['MonthPeriod'], f"${r['TotalRev']}", r['TxnCount']))

        elif mode == "System Ledger Streams":
            self.tree["columns"] = ("TXN ID", "Remitted Value", "Timestamp", "Route", "Coverage Label")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            query = f"SELECT PaymentID, Amount, PaymentDate, PaymentMethod, CoveredMonth FROM Payments WHERE {where_clause} ORDER BY PaymentDate DESC"
            for r in self.db.fetch_all(query, tuple(params)):
                self.tree.insert("", "end", values=(r['PaymentID'], f"${r['Amount']}", r['PaymentDate'], r['PaymentMethod'], r['CoveredMonth']))

    def export_csv(self):
        if not self.tree.get_children(): return messagebox.showwarning("Warning", "Run query first.")
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path: return
        with open(path, mode='w', newline='') as f:
            w = csv.writer(f); w.writerow(self.tree["columns"])
            for idx in self.tree.get_children(): w.writerow(self.tree.item(idx)['values'])
        messagebox.showinfo("Exported", "Matrix saved.")

    def render_charts(self):
        where_clause, params = self.get_date_filters()
        win = tk.Toplevel(self.parent_frame)
        win.title("Time-Series Dashboards")
        win.geometry("950x450")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
        
        q1 = f"""SELECT p.PlanName, COALESCE(SUM(pay.Amount), 0) as rev 
                 FROM Payments pay JOIN Members m ON pay.MemberID = m.MemberID 
                 JOIN Membership_Plans p ON m.PlanID = p.PlanID WHERE {where_clause} GROUP BY p.PlanID"""
        d1 = self.db.fetch_all(q1, tuple(params))
        
        lbls1 = [d['PlanName'] for d in d1 if d['rev'] > 0]
        vols1 = [float(d['rev']) for d in d1 if d['rev'] > 0]
        if vols1: 
            ax1.pie(vols1, labels=lbls1, autopct='%1.1f%%', startangle=90, colors=['#5dade2','#48c9b0','#f4d03f'])
        else: 
            ax1.text(0.5, 0.5, 'No Revenue Data for Filter', ha='center')
        ax1.set_title("Cash Distribution by Plan")

        q2 = f"""SELECT DATE_FORMAT(PaymentDate, '%b %Y') as MonthLbl, COALESCE(SUM(Amount), 0) as rev 
                 FROM Payments WHERE {where_clause} GROUP BY MonthLbl ORDER BY MIN(PaymentDate)"""
        d2 = self.db.fetch_all(q2, tuple(params))
        
        lbls2 = [d['MonthLbl'] for d in d2]
        vols2 = [float(d['rev']) for d2 in d2 for k, d2 in d2.items() if k == 'rev'] 
        vols2 = [float(d['rev']) for d in d2]

        if vols2:
            ax2.bar(lbls2, vols2, color=['#ec7063', '#58d68d', '#af7ac5'])
            ax2.tick_params(axis='x', rotation=15)
        else:
            ax2.text(0.5, 0.5, 'No Timeline Data for Filter', ha='center')
        ax2.set_title("Monthly Revenue Timeline ($)")

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)