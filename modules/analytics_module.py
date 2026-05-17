import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()

        tk.Label(self.parent_frame, text="Business Intelligence & Aggregations", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        ctrl_frame = tk.Frame(self.parent_frame, bg="#f4f4f9")
        ctrl_frame.pack(fill="x", pady=10)
        
        self.rep_select = ttk.Combobox(ctrl_frame, values=["Profile Distribution Counts", "Plan Base Yield Metrics", "System Ledger Streams"], state="readonly", width=30)
        self.rep_select.current(1)
        self.rep_select.pack(side="left", padx=5)
        
        tk.Button(ctrl_frame, text="Run Aggregates", bg="#007bff", fg="white", command=self.run_engine_aggregates).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Export CSV Matrix", bg="#28a745", fg="white", command=self.export_matrix_to_csv).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Launch Visual Canvas", bg="#6f42c1", fg="white", command=self.render_canvas_dashboards).pack(side="left", padx=20)

        self.tree = ttk.Treeview(self.content_sub_frame := tk.Frame(self.parent_frame), show="headings")
        self.content_sub_frame.pack(fill="both", expand=True, pady=10)
        self.tree.pack(fill="both", expand=True)

    def run_engine_aggregates(self):
        mode = self.rep_select.get()
        for col in self.tree["columns"]: self.tree.heading(col, text="")
        self.tree.delete(*self.tree.get_children())

        if mode == "Profile Distribution Counts":
            self.tree["columns"] = ("Status Parameter", "Total Tracked Profiles")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            for r in self.db.fetch_all("SELECT Status, COUNT(*) as Total FROM Members GROUP BY Status"):
                self.tree.insert("", "end", values=(r['Status'], r['Total']))

        elif mode == "Plan Base Yield Metrics":
            self.tree["columns"] = ("Plan Index Name", "Enrolled Member Base", "True Derived Yield Metrics")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            query = "SELECT p.PlanName, COUNT(m.MemberID) as Base, (COUNT(m.MemberID) * p.Cost) as Revenue FROM Membership_Plans p LEFT JOIN Members m ON p.PlanID = m.PlanID GROUP BY p.PlanID"
            for r in self.db.fetch_all(query):
                self.tree.insert("", "end", values=(r['PlanName'], r['Base'], f"${r['Revenue'] or 0.00}"))

        elif mode == "System Ledger Streams":
            self.tree["columns"] = ("Payment Pointer ID", "Transaction Face Volume", "Log Timestamp", "Settlement Route")
            for col in self.tree["columns"]: self.tree.heading(col, text=col)
            for r in self.db.fetch_all("SELECT PaymentID, Amount, PaymentDate, PaymentMethod FROM Payments ORDER BY PaymentID DESC"):
                self.tree.insert("", "end", values=(r['PaymentID'], f"${r['Amount']}", r['PaymentDate'], r['PaymentMethod']))

    def export_matrix_to_csv(self):
        if not self.tree.get_children(): return messagebox.showwarning("Execution Warning", "Generate real aggregate tables first.")
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Tables", "*.csv")])
        if not path: return

        with open(path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.tree["columns"])
            for idx in self.tree.get_children(): writer.writerow(self.tree.item(idx)['values'])
        messagebox.showinfo("Export Success", f"Matrix recorded to: {path}")

    def render_canvas_dashboards(self):
        win = tk.Toplevel(self.parent_frame)
        win.title("Dynamic Matplotlib Workspace Canvas")
        win.geometry("850x450")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
        data = self.db.fetch_all("SELECT p.PlanName, COUNT(m.MemberID) as base, (COUNT(m.MemberID) * p.Cost) as rev FROM Membership_Plans p LEFT JOIN Members m ON p.PlanID = m.PlanID GROUP BY p.PlanID")
        
        lbls = [d['PlanName'] for d in data if d['base'] > 0]
        vols = [d['base'] for d in data if d['base'] > 0]
        
        if vols: ax1.pie(vols, labels=lbls, autopct='%1.1f%%', startangle=90, colors=['#5dade2','#48c9b0','#f4d03f'])
        else: ax1.text(0.5, 0.5, 'No Active Yield Profiles Found', ha='center', va='center')
        ax1.set_title("User Segment Ratios per Plan Option")

        bar_lbls = [d['PlanName'] for d in data]
        bar_yields = [float(d['rev']) for d in data]
        ax2.bar(bar_lbls, bar_yields, color=['#ec7063', '#58d68d', '#af7ac5'])
        ax2.set_title("Absolute Cash Yield Matrix ($)")
        ax2.tick_params(axis='x', rotation=12)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)