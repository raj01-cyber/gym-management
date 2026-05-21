import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import re

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
        tk.Label(search_frame, text="Global Search (Name, Email, Phone):", bg="#f4f4f9").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=10)
        tk.Button(search_frame, text="Search", command=self.search_members, bg="#17a2b8", fg="white").pack(side="left")
        tk.Button(search_frame, text="Clear", command=self.load_members_data, bg="#6c757d", fg="white").pack(side="left", padx=5)

        form_frame = tk.Frame(self.parent_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief="groove")
        form_frame.pack(fill="x", pady=(0, 20))

        tk.Label(form_frame, text="First Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.fname_entry = ttk.Entry(form_frame); self.fname_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Last Name:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        self.lname_entry = ttk.Entry(form_frame); self.lname_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Email Address:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(form_frame); self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Phone Number:", bg="#ffffff").grid(row=1, column=2, padx=5, pady=5)
        self.phone_entry = ttk.Entry(form_frame); self.phone_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Assigned Plan:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5)
        plans = self.db.fetch_all("SELECT PlanID, PlanName FROM Membership_Plans")
        self.plan_dict = {p['PlanName']: p['PlanID'] for p in plans}
        self.plan_combo = ttk.Combobox(form_frame, values=list(self.plan_dict.keys()), state="readonly")
        self.plan_combo.grid(row=2, column=1, padx=5, pady=5)
        if plans: self.plan_combo.current(0)
        
        tk.Button(form_frame, text="Add Member", bg="#28a745", fg="white", command=self.add_member).grid(row=3, column=0, pady=10)
        tk.Button(form_frame, text="Update", bg="#ffc107", command=self.update_member).grid(row=3, column=1)
        tk.Button(form_frame, text="Remove Member", bg="#dc3545", fg="white", command=self.delete_member).grid(row=3, column=2)

        self.tree = ttk.Treeview(self.parent_frame, columns=("Gym-ID", "First Name", "Last Name", "Email Address", "Phone Number", "Assigned Plan"), show="headings")
        for col in self.tree["columns"]: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.fill_fields)
        self.load_members_data()

    def validate_inputs(self, email, phone):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Format Error", "Invalid Email formatting.")
            return False
        if not re.match(r"^\+?1?\d{9,15}$", phone):
            messagebox.showerror("Format Error", "Phone number entry must be purely numeric (9-15 characters).")
            return False
        return True

    def check_duplicates(self, email, phone, exclude_id=None):
        query = "SELECT Email, Phone FROM Members WHERE (Email = %s OR Phone = %s)"
        params = [email, phone]
        if exclude_id:
            query += " AND MemberID != %s"
            params.append(exclude_id)
            
        conflicts = self.db.fetch_all(query, params)
        if conflicts:
            if conflicts[0]['Email'] == email:
                messagebox.showerror("Constraint Violation", f"Email '{email}' is already registered.")
            else:
                messagebox.showerror("Constraint Violation", f"Phone '{phone}' is already registered to another user.")
            return True
        return False

    def load_members_data(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for row in self.db.fetch_all("SELECT m.MemberID, m.FirstName, m.LastName, m.Email, m.Phone, p.PlanName FROM Members m JOIN Membership_Plans p ON m.PlanID = p.PlanID"):
            self.tree.insert("", "end", values=(row['MemberID'], row['FirstName'], row['LastName'], row['Email'], row['Phone'], row['PlanName']))

    def add_member(self):
        fn, ln, em, ph, pl = self.fname_entry.get().strip(), self.lname_entry.get().strip(), self.email_entry.get().strip(), self.phone_entry.get().strip(), self.plan_combo.get()
        if not all([fn, ln, em, ph, pl]): return messagebox.showwarning("Error", "All parameter values are required.")
        if not self.validate_inputs(em, ph): return
        if self.check_duplicates(em, ph): return

        if self.db.execute_query("INSERT INTO Members (FirstName, LastName, Email, Phone, JoinDate, PlanID) VALUES (%s,%s,%s,%s,%s,%s)", (fn, ln, em, ph, date.today(), self.plan_dict[pl])):
            messagebox.showinfo("Success", "Registered Successfully!")
            self.load_members_data()

    def update_member(self):
        sel = self.tree.focus()
        if not sel: return
        mid = self.tree.item(sel, 'values')[0]
        fn, ln, em, ph, pl = self.fname_entry.get().strip(), self.lname_entry.get().strip(), self.email_entry.get().strip(), self.phone_entry.get().strip(), self.plan_combo.get()
        
        if not self.validate_inputs(em, ph): return
        if self.check_duplicates(em, ph, exclude_id=mid): return
        
        if self.db.execute_query("UPDATE Members SET FirstName=%s, LastName=%s, Email=%s, Phone=%s, PlanID=%s WHERE MemberID=%s", (fn, ln, em, ph, self.plan_dict[pl], mid)):
            messagebox.showinfo("Success", "Parameters Updated.")
            self.load_members_data()

    def delete_member(self):
        sel = self.tree.focus()
        if not sel: return
        mid = self.tree.item(sel, 'values')[0]
        chk = self.db.fetch_all("SELECT COUNT(*) as count FROM Payments WHERE MemberID = %s", (mid,))
        if chk and chk[0]['count'] > 0: return messagebox.showerror("Error", "Linked financial logs exist. Wipe blocked.")
        if messagebox.askyesno("Confirm", "Delete record?"):
            self.db.execute_query("DELETE FROM Members WHERE MemberID = %s", (mid,))
            self.load_members_data()

    def search_members(self):
        t = f"%{self.search_entry.get().strip()}%"
        for row in self.tree.get_children(): self.tree.delete(row)
        query = """SELECT m.MemberID, m.FirstName, m.LastName, m.Email, m.Phone, p.PlanName 
                   FROM Members m JOIN Membership_Plans p ON m.PlanID = p.PlanID 
                   WHERE m.FirstName LIKE %s OR m.LastName LIKE %s OR m.Email LIKE %s OR m.Phone LIKE %s"""
        for row in self.db.fetch_all(query, (t, t, t, t)):
            self.tree.insert("", "end", values=(row['MemberID'], row['FirstName'], row['LastName'], row['Email'], row['Phone'], row['PlanName']))

    def fill_fields(self, e):
        sel = self.tree.focus()
        if not sel: return
        v = self.tree.item(sel, 'values')
        self.fname_entry.delete(0, tk.END); self.fname_entry.insert(0, v[1])
        self.lname_entry.delete(0, tk.END); self.lname_entry.insert(0, v[2])
        self.email_entry.delete(0, tk.END); self.email_entry.insert(0, v[3])
        self.phone_entry.delete(0, tk.END); self.phone_entry.insert(0, v[4])
        self.plan_combo.set(v[5])