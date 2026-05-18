import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame; self.db = db; self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()
        tk.Label(self.parent_frame, text="True Cash Business Intelligence", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        ctrl_frame = tk.Frame(self.parent_frame, bg="#f4f4f9"); ctrl_frame.pack(fill="x", pady=10)
        self.rep_select = ttk.Combobox(ctrl_frame, values=["Profile Status Distributions", "True Cash Revenue Matrix", "System Ledger Streams"], state="readonly", width=30)
        self.rep_select.current(1); self.rep_select.pack(side="left", padx=5)
        
        tk.Button(ctrl_frame, text="Run Aggregates", bg="#007bff", fg="white", command=self.run_aggregates).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Export CSV", bg="#28a745", fg="white", command=self.export_csv).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Launch Visual Dashboards", bg="#6f42c1", fg="white", command=self.render_charts).pack(side="left", padx=20)

        self.table_container = tk.Frame(self.parent_frame); self.table_container.pack(fill="both", expand=True, pady=10)
        self.tree = ttk.Treeview(self.table_container, show="headings"); self.tree.pack(fill="both", expand=True)

    def run_aggregates(self):
        mode = self.rep_select.get()
        self.tree.delete(*self.tree.get_children())

        if mode == "Profile Status Distributions":
            self.tree["columns"] = ("Status", "Total Profiles")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            for r in self.db.fetch_all("SELECT Status, COUNT(*) as Total FROM Members GROUP BY Status"):
                self.tree.insert("", "end", values=(r['Status'], r['Total']))

        elif mode == "True Cash Revenue Matrix":
            self.tree["columns"] = ("Plan Option", "Active Enrollees", "True Cash Remitted")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            query = """SELECT p.PlanName, COUNT(DISTINCT m.MemberID) as Base, COALESCE(SUM(pay.Amount), 0) as TrueRevenue 
                       FROM Membership_Plans p 
                       LEFT JOIN Members m ON p.PlanID = m.PlanID 
                       LEFT JOIN Payments pay ON m.MemberID = pay.MemberID 
                       GROUP BY p.PlanID"""
            for r in self.db.fetch_all(query):
                self.tree.insert("", "end", values=(r['PlanName'], r['Base'], f"${r['TrueRevenue']}"))

        elif mode == "System Ledger Streams":
            self.tree["columns"] = ("TXN ID", "Remitted Value", "Timestamp", "Route", "Coverage Period")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            for r in self.db.fetch_all("SELECT PaymentID, Amount, PaymentDate, PaymentMethod, CoveredMonth FROM Payments ORDER BY PaymentID DESC"):
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
        win = tk.Toplevel(self.parent_frame); win.title("True Cash Dashboards"); win.geometry("850x450")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
        
        query = """SELECT p.PlanName, COUNT(DISTINCT m.MemberID) as base, COALESCE(SUM(pay.Amount), 0) as rev 
                   FROM Membership_Plans p LEFT JOIN Members m ON p.PlanID = m.PlanID LEFT JOIN Payments pay ON m.MemberID = pay.MemberID GROUP BY p.PlanID"""
        data = self.db.fetch_all(query)
        
        lbls = [d['PlanName'] for d in data if d['base'] > 0]
        vols = [d['base'] for d in data if d['base'] > 0]
        if vols: ax1.pie(vols, labels=lbls, autopct='%1.1f%%', startangle=90)
        ax1.set_title("User Segment Enrollments")

        bar_lbls = [d['PlanName'] for d in data]; bar_yields = [float(d['rev']) for d in data]
        ax2.bar(bar_lbls, bar_yields, color=['#17a2b8', '#28a745', '#ffc107'])
        ax2.set_title("True Cash Collected ($)")
        canvas = FigureCanvasTkAgg(fig, master=win); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)