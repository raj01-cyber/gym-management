import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database_manager import DatabaseManager

class SmartGymApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Management System")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f4f4f9")
        
        self.db = DatabaseManager()
        self.create_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_login_screen(self):
        self.clear_window()
        login_frame = tk.Frame(self.root, bg="#ffffff", padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="Gym Login", font=("Helvetica", 18, "bold"), bg="#ffffff").pack(pady=(0, 20))

        tk.Label(login_frame, text="Username:", font=("Helvetica", 12), bg="#ffffff").pack(anchor="w")
        self.username_entry = ttk.Entry(login_frame, font=("Helvetica", 12))
        self.username_entry.pack(fill="x", pady=(0, 10))

        tk.Label(login_frame, text="Password:", font=("Helvetica", 12), bg="#ffffff").pack(anchor="w")
        self.password_entry = ttk.Entry(login_frame, font=("Helvetica", 12), show="*")
        self.password_entry.pack(fill="x", pady=(0, 20))

        tk.Button(login_frame, text="Login", font=("Helvetica", 12, "bold"), bg="#007bff", fg="white", command=self.authenticate).pack(fill="x")

    def authenticate(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        if user == "admin" and pwd == "admin123":
            self.create_main_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def create_main_dashboard(self):
        self.clear_window()

        sidebar = tk.Frame(self.root, bg="#2c3e50", width=200)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="Menu", font=("Helvetica", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=20)

        buttons = [
            ("Members", self.build_members_ui), 
            ("Payments", self.build_payments_ui), 
            ("Analytics & Reports", self.build_analytics_ui), 
            ("Logout", self.create_login_screen)
        ]
        
        for text, command in buttons:
            tk.Button(sidebar, text=text, font=("Helvetica", 12), bg="#34495e", fg="white", bd=0, command=command).pack(fill="x", pady=5, padx=10)

        self.content_frame = tk.Frame(self.root, bg="#f4f4f9")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.build_members_ui()

    def build_members_ui(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        tk.Label(self.content_frame, text="Manage Members", font=("Helvetica", 20, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        search_frame = tk.Frame(self.content_frame, bg="#f4f4f9")
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="Search Name:", bg="#f4f4f9").pack(side="left")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=10)
        tk.Button(search_frame, text="Search", bg="#17a2b8", fg="white", command=self.search_members).pack(side="left")
        tk.Button(search_frame, text="Show All", bg="#6c757d", fg="white", command=self.load_members_data).pack(side="left", padx=5)

        form_frame = tk.Frame(self.content_frame, bg="#ffffff", padx=10, pady=10)
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="First Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.fname_entry = ttk.Entry(form_frame)
        self.fname_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Last Name:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.lname_entry = ttk.Entry(form_frame)
        self.lname_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Email:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Phone:", bg="#ffffff").grid(row=1, column=2, padx=5, pady=5)
        self.phone_entry = ttk.Entry(form_frame)
        self.phone_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Plan:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        plans = self.db.fetch_all("SELECT PlanID, PlanName FROM Membership_Plans")
        self.plan_dict = {p['PlanName']: p['PlanID'] for p in plans}
        self.plan_combo = ttk.Combobox(form_frame, values=list(self.plan_dict.keys()), state="readonly")
        if plans: self.plan_combo.current(0)
        self.plan_combo.grid(row=2, column=1, padx=5, pady=5)
        
        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(btn_frame, text="Add Member", bg="#28a745", fg="white", command=self.add_member).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Selected", bg="#dc3545", fg="white", command=self.delete_member).pack(side="left", padx=5)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "First", "Last", "Email", "Phone", "Plan"), show="headings")
        for col in self.tree["columns"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.load_members_data()

    def load_members_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        query = """SELECT m.MemberID, m.FirstName, m.LastName, m.Email, m.Phone, p.PlanName 
                   FROM Members m LEFT JOIN Membership_Plans p ON m.PlanID = p.PlanID"""
        for row in self.db.fetch_all(query):
            self.tree.insert("", "end", values=(row['MemberID'], row['FirstName'], row['LastName'], row['Email'], row['Phone'], row['PlanName']))

    def add_member(self):
        fname, lname, email, phone = self.fname_entry.get().strip(), self.lname_entry.get().strip(), self.email_entry.get().strip(), self.phone_entry.get().strip()
        selected_plan_name = self.plan_combo.get()
        
        if not all([fname, lname, email, phone, selected_plan_name]): 
            return messagebox.showwarning("Error", "All fields required!")
        
        plan_id = self.plan_dict[selected_plan_name]
        query = "INSERT INTO Members (FirstName, LastName, Email, Phone, JoinDate, PlanID) VALUES (%s, %s, %s, %s, %s, %s)"
        if self.db.execute_query(query, (fname, lname, email, phone, date.today(), plan_id)):
            messagebox.showinfo("Success", "Member Added!")
            self.load_members_data()
        else:
            messagebox.showerror("Error", "Could not add member. Email might exist.")

    def delete_member(self):
        selected = self.tree.focus()
        if not selected: return messagebox.showwarning("Error", "Select a member.")
        member_id = self.tree.item(selected, 'values')[0]

        payments = self.db.fetch_all("SELECT COUNT(*) as count FROM Payments WHERE MemberID = %s", (member_id,))
        if payments and payments[0]['count'] > 0:
            return messagebox.showerror("Business Rule Violation", "Cannot delete member: Active payment records exist. Delete transactions first.")

        if messagebox.askyesno("Confirm", "Delete member?"):
            self.db.execute_query("DELETE FROM Members WHERE MemberID = %s", (member_id,))
            self.load_members_data()

    def search_members(self):
        term = f"%{self.search_entry.get()}%"
        for row in self.tree.get_children(): self.tree.delete(row)
        query = """SELECT m.MemberID, m.FirstName, m.LastName, m.Email, m.Phone, p.PlanName 
                   FROM Members m LEFT JOIN Membership_Plans p ON m.PlanID = p.PlanID WHERE m.FirstName LIKE %s OR m.LastName LIKE %s"""
        for row in self.db.fetch_all(query, (term, term)):
            self.tree.insert("", "end", values=(row['MemberID'], row['FirstName'], row['LastName'], row['Email'], row['Phone'], row['PlanName']))

    def build_payments_ui(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        tk.Label(self.content_frame, text="Process Payments", font=("Helvetica", 20, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        form_frame = tk.Frame(self.content_frame, bg="#ffffff", padx=10, pady=10)
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="Select Member:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        members = self.db.fetch_all("SELECT MemberID, FirstName, LastName FROM Members")
        self.member_dict = {f"{m['FirstName']} {m['LastName']} (ID: {m['MemberID']})": m['MemberID'] for m in members}
        self.member_combo = ttk.Combobox(form_frame, values=list(self.member_dict.keys()), state="readonly", width=30)
        if members: self.member_combo.current(0)
        self.member_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Amount ($):", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Method:", bg="#ffffff").grid(row=0, column=4, padx=5, pady=5)
        self.method_combo = ttk.Combobox(form_frame, values=["Credit Card", "Cash", "Bank Transfer"], state="readonly")
        self.method_combo.current(0)
        self.method_combo.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(form_frame, text="Record Payment", bg="#28a745", fg="white", command=self.add_payment).grid(row=1, column=0, columnspan=6, pady=10)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True)

        self.pay_tree = ttk.Treeview(tree_frame, columns=("Pay ID", "Member", "Amount", "Date", "Method"), show="headings")
        for col in self.pay_tree["columns"]: self.pay_tree.heading(col, text=col)
        self.pay_tree.pack(fill="both", expand=True)
        self.load_payments_data()

    def load_payments_data(self):
        for row in self.pay_tree.get_children(): self.pay_tree.delete(row)
        query = """SELECT p.PaymentID, CONCAT(m.FirstName, ' ', m.LastName) as MemberName, p.Amount, p.PaymentDate, p.PaymentMethod 
                   FROM Payments p JOIN Members m ON p.MemberID = m.MemberID ORDER BY p.PaymentDate DESC"""
        for row in self.db.fetch_all(query):
            self.pay_tree.insert("", "end", values=(row['PaymentID'], row['MemberName'], f"${row['Amount']}", row['PaymentDate'], row['PaymentMethod']))

    def add_payment(self):
        selected_member = self.member_combo.get()
        amount = self.amount_entry.get().strip()
        method = self.method_combo.get()
        
        if not selected_member or not amount: return messagebox.showwarning("Error", "Provide member and amount.")
        try:
            amount_val = float(amount)
        except ValueError:
            return messagebox.showerror("Error", "Amount must be a number.")

        member_id = self.member_dict[selected_member]
        query = "INSERT INTO Payments (MemberID, Amount, PaymentDate, PaymentMethod) VALUES (%s, %s, %s, %s)"
        if self.db.execute_query(query, (member_id, amount_val, date.today(), method)):
            messagebox.showinfo("Success", "Payment Recorded!")
            self.amount_entry.delete(0, tk.END)
            self.load_payments_data()

    def build_analytics_ui(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        tk.Label(self.content_frame, text="Gym Analytics & Reports", font=("Helvetica", 20, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        ctrl_frame = tk.Frame(self.content_frame, bg="#f4f4f9")
        ctrl_frame.pack(fill="x", pady=10)
        
        self.report_type = ttk.Combobox(ctrl_frame, values=["Member Status Count", "Revenue by Plan", "Recent Payments"], state="readonly")
        self.report_type.current(1)
        self.report_type.pack(side="left", padx=5)
        
        tk.Button(ctrl_frame, text="Generate Report", bg="#007bff", fg="white", command=self.generate_report).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Export to CSV", bg="#28a745", fg="white", command=self.export_csv).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="View Visual Dashboards", bg="#6f42c1", fg="white", command=self.show_charts).pack(side="left", padx=20)

        self.report_tree = ttk.Treeview(self.content_frame, show="headings")
        self.report_tree.pack(fill="both", expand=True, pady=10)

    def generate_report(self):
        report = self.report_type.get()
        for col in self.report_tree["columns"]: self.report_tree.heading(col, text="")
        self.report_tree.delete(*self.report_tree.get_children())

        if report == "Member Status Count":
            self.report_tree["columns"] = ("Status", "Total Members")
            data = self.db.fetch_all("SELECT Status, COUNT(*) as Total FROM Members GROUP BY Status")
            for col in self.report_tree["columns"]: self.report_tree.heading(col, text=col)
            for row in data: self.report_tree.insert("", "end", values=(row['Status'], row['Total']))

        elif report == "Revenue by Plan":
            self.report_tree["columns"] = ("Plan Name", "Total Members Enrolled", "Estimated Revenue")
            query = """SELECT p.PlanName, COUNT(m.MemberID) as Members, (COUNT(m.MemberID) * p.Cost) as Revenue 
                       FROM Membership_Plans p LEFT JOIN Members m ON p.PlanID = m.PlanID GROUP BY p.PlanID"""
            data = self.db.fetch_all(query)
            for col in self.report_tree["columns"]: self.report_tree.heading(col, text=col)
            for row in data: self.report_tree.insert("", "end", values=(row['PlanName'], row['Members'], f"${row['Revenue'] or 0.00}"))

        elif report == "Recent Payments":
            self.report_tree["columns"] = ("Payment ID", "Amount", "Date", "Method")
            data = self.db.fetch_all("SELECT PaymentID, Amount, PaymentDate, PaymentMethod FROM Payments ORDER BY PaymentDate DESC LIMIT 20")
            for col in self.report_tree["columns"]: self.report_tree.heading(col, text=col)
            for row in data: self.report_tree.insert("", "end", values=(row['PaymentID'], f"${row['Amount']}", row['PaymentDate'], row['PaymentMethod']))

    def export_csv(self):
        if not self.report_tree.get_children(): return messagebox.showwarning("Empty", "Generate a report first.")
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path: return

        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.report_tree["columns"])
            for row_id in self.report_tree.get_children():
                writer.writerow(self.report_tree.item(row_id)['values'])
        messagebox.showinfo("Success", f"Report exported to {file_path}")

    def show_charts(self):
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Visual Dashboards")
        chart_window.geometry("800x400")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

        plan_data = self.db.fetch_all("SELECT p.PlanName, COUNT(m.MemberID) as count, (COUNT(m.MemberID) * p.Cost) as rev FROM Membership_Plans p LEFT JOIN Members m ON p.PlanID = m.PlanID GROUP BY p.PlanID")
        
        labels = [d['PlanName'] for d in plan_data if d['count'] > 0]
        sizes = [d['count'] for d in plan_data if d['count'] > 0]
        if sizes:
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
        else:
            ax1.text(0.5, 0.5, 'No Members Found', horizontalalignment='center', verticalalignment='center')
        ax1.set_title("Members Distribution by Plan")

        labels_bar = [d['PlanName'] for d in plan_data]
        revs = [float(d['rev']) for d in plan_data]
        ax2.bar(labels_bar, revs, color=['#17a2b8', '#28a745', '#ffc107'])
        ax2.set_title("Actual Revenue Generated by Plan")
        ax2.tick_params(axis='x', rotation=15)

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartGymApp(root)
    root.mainloop()