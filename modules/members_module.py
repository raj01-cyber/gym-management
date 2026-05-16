import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

class MembersUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()

        tk.Label(self.parent_frame, text="Manage Gym Members", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        search_frame = tk.Frame(self.parent_frame, bg="#f4f4f9")
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="Search Member Name:", bg="#f4f4f9").pack(side="left")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=10)
        tk.Button(search_frame, text="Search", bg="#17a2b8", fg="white", command=self.search_members).pack(side="left")
        tk.Button(search_frame, text="Clear Filter", bg="#6c757d", fg="white", command=self.load_members_data).pack(side="left", padx=5)

        form_frame = tk.Frame(self.parent_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief="groove")
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="First Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.fname_entry = ttk.Entry(form_frame)
        self.fname_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Last Name:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.lname_entry = ttk.Entry(form_frame)
        self.lname_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Email Address:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Phone String:", bg="#ffffff").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.phone_entry = ttk.Entry(form_frame)
        self.phone_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Assigned Plan:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        plans = self.db.fetch_all("SELECT PlanID, PlanName FROM Membership_Plans")
        self.plan_dict = {p['PlanName']: p['PlanID'] for p in plans}
        self.plan_combo = ttk.Combobox(form_frame, values=list(self.plan_dict.keys()), state="readonly")
        if plans: self.plan_combo.current(0)
        self.plan_combo.grid(row=2, column=1, padx=5, pady=5)
        
        btn_frame = tk.Frame(form_frame, bg="#ffffff")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        tk.Button(btn_frame, text="Add Member", bg="#28a745", fg="white", command=self.add_member).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Apply Updates", bg="#ffc107", fg="black", command=self.update_member).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Member", bg="#dc3545", fg="white", command=self.delete_member).pack(side="left", padx=5)

        tree_frame = tk.Frame(self.parent_frame)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "First Name", "Last Name", "Email", "Phone", "Plan"), show="headings")
        for col in self.tree["columns"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.populate_fields_from_tree)
        self.load_members_data()

    def load_members_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        query = "SELECT m.MemberID, m.FirstName, m.LastName, m.Email, m.Phone, p.PlanName FROM Members m JOIN Membership_Plans p ON m.PlanID = p.PlanID"
        for row in self.db.fetch_all(query):
            self.tree.insert("", "end", values=(row['MemberID'], row['FirstName'], row['LastName'], row['Email'], row['Phone'], row['PlanName']))

    def add_member(self):
        fn, ln, em, ph, pl = self.fname_entry.get().strip(), self.lname_entry.get().strip(), self.email_entry.get().strip(), self.phone_entry.get().strip(), self.plan_combo.get()
        if not all([fn, ln, em, ph, pl]): return messagebox.showwarning("Validation Error", "All registration attributes required.")
        
        query = "INSERT INTO Members (FirstName, LastName, Email, Phone, JoinDate, PlanID) VALUES (%s, %s, %s, %s, %s, %s)"
        if self.db.execute_query(query, (fn, ln, em, ph, date.today(), self.plan_dict[pl])):
            messagebox.showinfo("Success", "Registered new member successfully!")
            self.load_members_data()

    def update_member(self):
        selected = self.tree.focus()
        if not selected: return messagebox.showwarning("Target Error", "Double click an item below to modify it.")
        mid = self.tree.item(selected, 'values')[0]
        fn, ln, em, ph, pl = self.fname_entry.get().strip(), self.lname_entry.get().strip(), self.email_entry.get().strip(), self.phone_entry.get().strip(), self.plan_combo.get()

        if messagebox.askyesno("Confirm Alteration", f"Push updates to system asset ID: {mid}?"):
            query = "UPDATE Members SET FirstName=%s, LastName=%s, Email=%s, Phone=%s, PlanID=%s WHERE MemberID=%s"
            if self.db.execute_query(query, (fn, ln, em, ph, self.plan_dict[pl], mid)):
                messagebox.showinfo("Success", "System parameters patched.")
                self.load_members_data()

    def delete_member(self):
        selected = self.tree.focus()
        if not selected: return messagebox.showwarning("Target Error", "Highlight a record row first.")
        mid = self.tree.item(selected, 'values')[0]

        checks = self.db.fetch_all("SELECT COUNT(*) as count FROM Payments WHERE MemberID = %s", (mid,))
        if checks and checks[0]['count'] > 0:
            return messagebox.showerror("Database Constraint Error", "Cascade blocked: Financial ledgers are linked to this entity profile.")

        if messagebox.askyesno("Confirm Wipe", "Permanently delete profile record?"):
            self.db.execute_query("DELETE FROM Members WHERE MemberID = %s", (mid,))
            self.load_members_data()

    def search_members(self):
        term = f"%{self.search_entry.get().strip()}%"
        for row in self.tree.get_children(): self.tree.delete(row)
        query = "SELECT m.MemberID, m.FirstName, m.LastName, m.Email, m.Phone, p.PlanName FROM Members m JOIN Membership_Plans p ON m.PlanID = p.PlanID WHERE m.FirstName LIKE %s OR m.LastName LIKE %s"
        for row in self.db.fetch_all(query, (term, term)):
            self.tree.insert("", "end", values=(row['MemberID'], row['FirstName'], row['LastName'], row['Email'], row['Phone'], row['PlanName']))

    def populate_fields_from_tree(self, event):
        selected = self.tree.focus()
        if not selected: return
        vals = self.tree.item(selected, 'values')
        self.fname_entry.delete(0, tk.END); self.fname_entry.insert(0, vals[1])
        self.lname_entry.delete(0, tk.END); self.lname_entry.insert(0, vals[2])
        self.email_entry.delete(0, tk.END); self.email_entry.insert(0, vals[3])
        self.phone_entry.delete(0, tk.END); self.phone_entry.insert(0, vals[4])
        self.plan_combo.set(vals[5])