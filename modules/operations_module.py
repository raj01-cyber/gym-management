import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class OperationsUI:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.build_ui()

    def build_ui(self):
        for widget in self.parent_frame.winfo_children(): widget.destroy()
        tk.Label(self.parent_frame, text="Floor Operations (Classes & Attendance)", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))

        notebook = ttk.Notebook(self.parent_frame)
        notebook.pack(fill="both", expand=True)

        tab_attendance = tk.Frame(notebook, bg="#ffffff")
        tab_bookings = tk.Frame(notebook, bg="#ffffff")
        notebook.add(tab_attendance, text="Log Attendance")
        notebook.add(tab_bookings, text="Class Bookings")

        self.build_attendance_tab(tab_attendance)
        self.build_bookings_tab(tab_bookings)

    def build_attendance_tab(self, frame):
        ctrl_frame = tk.Frame(frame, bg="#ffffff", pady=15, padx=15)
        ctrl_frame.pack(fill="x")

        tk.Label(ctrl_frame, text="Select Member for Check-in:", bg="#ffffff").pack(side="left", padx=5)
        
        members = self.db.fetch_all("SELECT MemberID, FirstName, LastName FROM Members")
        self.att_member_map = {f"{m['FirstName']} {m['LastName']} (Gym-ID: {m['MemberID']})": m['MemberID'] for m in members}
        
        self.att_combo = ttk.Combobox(ctrl_frame, values=list(self.att_member_map.keys()), state="readonly", width=40)
        self.att_combo.pack(side="left", padx=5)
        if members: self.att_combo.current(0)

        tk.Button(ctrl_frame, text="Log Facility Entry", bg="#28a745", fg="white", command=self.log_attendance).pack(side="left", padx=15)

        self.att_tree = ttk.Treeview(frame, columns=("Log ID", "Gym-ID", "Name", "Check-in Timestamp"), show="headings")
        for col in self.att_tree["columns"]: self.att_tree.heading(col, text=col)
        self.att_tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.load_attendance()

    def log_attendance(self):
        selection = self.att_combo.get()
        if not selection: return
        member_id = self.att_member_map[selection]
        
        if self.db.execute_query("INSERT INTO Attendance (MemberID) VALUES (%s)", (member_id,)):
            messagebox.showinfo("Access Granted", "Member check-in logged successfully.")
            self.load_attendance()

    def load_attendance(self):
        for row in self.att_tree.get_children(): self.att_tree.delete(row)
        query = """SELECT a.LogID, a.MemberID, CONCAT(m.FirstName, ' ', m.LastName) as Name, a.CheckInTime 
                   FROM Attendance a JOIN Members m ON a.MemberID = m.MemberID ORDER BY a.CheckInTime DESC"""
        for r in self.db.fetch_all(query):
            self.att_tree.insert("", "end", values=(r['LogID'], r['MemberID'], r['Name'], r['CheckInTime']))

    def build_bookings_tab(self, frame):
        ctrl_frame = tk.Frame(frame, bg="#ffffff", pady=15, padx=15)
        ctrl_frame.pack(fill="x")

        tk.Label(ctrl_frame, text="Member:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
        self.book_combo = ttk.Combobox(ctrl_frame, values=list(self.att_member_map.keys()), state="readonly", width=35)
        self.book_combo.grid(row=0, column=1, padx=5, pady=5)
        if self.att_member_map: self.book_combo.current(0)

        tk.Label(ctrl_frame, text="Select Class:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
        classes = self.db.fetch_all("SELECT ClassID, ClassName, ScheduleTime FROM Classes")
        self.class_map = {f"{c['ClassName']} ({c['ScheduleTime']})": c['ClassID'] for c in classes}
        
        self.class_combo = ttk.Combobox(ctrl_frame, values=list(self.class_map.keys()), state="readonly", width=35)
        self.class_combo.grid(row=0, column=3, padx=5, pady=5)
        if classes: self.class_combo.current(0)

        tk.Button(ctrl_frame, text="Confirm Booking", bg="#007bff", fg="white", command=self.book_class).grid(row=0, column=4, padx=15)

        self.book_tree = ttk.Treeview(frame, columns=("Booking ID", "Name", "Class", "Schedule"), show="headings")
        for col in self.book_tree["columns"]: self.book_tree.heading(col, text=col)
        self.book_tree.pack(fill="both", expand=True, padx=15, pady=10)
        self.load_bookings()

    def book_class(self):
        m_sel, c_sel = self.book_combo.get(), self.class_combo.get()
        if not m_sel or not c_sel: return
        
        member_id = self.att_member_map[m_sel]
        class_id = self.class_map[c_sel]

        if self.db.fetch_all("SELECT BookingID FROM Class_Bookings WHERE MemberID = %s AND ClassID = %s", (member_id, class_id)):
            return messagebox.showerror("Booking Failed", "This member is already registered for this specific class.")

        if self.db.execute_query("INSERT INTO Class_Bookings (ClassID, MemberID) VALUES (%s, %s)", (class_id, member_id)):
            messagebox.showinfo("Success", "Class booked successfully.")
            self.load_bookings()

    def load_bookings(self):
        for row in self.book_tree.get_children(): self.book_tree.delete(row)
        query = """SELECT cb.BookingID, CONCAT(m.FirstName, ' ', m.LastName) as Name, c.ClassName, c.ScheduleTime 
                   FROM Class_Bookings cb JOIN Members m ON cb.MemberID = m.MemberID JOIN Classes c ON cb.ClassID = c.ClassID ORDER BY cb.BookingID DESC"""
        for r in self.db.fetch_all(query):
            self.book_tree.insert("", "end", values=(r['BookingID'], r['Name'], r['ClassName'], r['ScheduleTime']))