import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from database_manager import DatabaseManager

from modules.members_module import MembersUI
from modules.payments_module import PaymentsUI
from modules.analytics_module import AnalyticsUI

class SmartGymApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Gym Engine - Enterprise Platform")
        self.root.geometry("1150完整750")
        self.root.geometry("1150x750")
        self.root.configure(bg="#f4f4f9")
        
        self.db = DatabaseManager()
        self.current_user = None
        self.current_role = None
        self.show_auth_screen(mode="login")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_auth_screen(self, mode="login"):
        self.clear_window()
        
        auth_frame = tk.Frame(self.root, bg="#ffffff", padx=40, pady=40, bd=1, relief="solid")
        auth_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_text = "Secure System Login" if mode == "login" else "New User Registration"
        tk.Label(auth_frame, text=title_text, font=("Helvetica", 16, "bold"), bg="#ffffff").pack(pady=(0, 20))

        tk.Label(auth_frame, text="Username:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
        self.user_entry = ttk.Entry(auth_frame, font=("Helvetica", 11))
        self.user_entry.pack(fill="x", pady=(0, 10))

        tk.Label(auth_frame, text="Password:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
        self.pass_entry = ttk.Entry(auth_frame, font=("Helvetica", 11), show="*")
        self.pass_entry.pack(fill="x", pady=(0, 10))

        # Explicit Role Selection Dropdown (Rubric Section 3.2)
        tk.Label(auth_frame, text="Select Workspace Role:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
        self.role_combo = ttk.Combobox(auth_frame, values=["Admin", "Trainer"], state="readonly", font=("Helvetica", 10))
        self.role_combo.current(0)
        self.role_combo.pack(fill="x", pady=(0, 20))

        if mode == "login":
            tk.Button(auth_frame, text="Authenticate", font=("Helvetica", 11, "bold"), bg="#007bff", fg="white", bd=0, cursor="hand2", command=self.process_login).pack(fill="x")
            tk.Button(auth_frame, text="Create New Account", font=("Helvetica", 10), bg="#ffffff", fg="#007bff", bd=0, cursor="hand2", command=lambda: self.show_auth_screen("register")).pack(fill="x", pady=(10, 0))
        else:
            tk.Button(auth_frame, text="Register System Account", font=("Helvetica", 11, "bold"), bg="#28a745", fg="white", bd=0, cursor="hand2", command=self.process_registration).pack(fill="x")
            tk.Button(auth_frame, text="Back to Login", font=("Helvetica", 10), bg="#ffffff", fg="#6c757d", bd=0, cursor="hand2", command=lambda: self.show_auth_screen("login")).pack(fill="x", pady=(10, 0))

    def process_login(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        selected_role = self.role_combo.get()

        if not user or not pwd:
            return messagebox.showwarning("Validation Warning", "All input fields must be populated.")

        hashed_attempt = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        
        # Enforce exact parameterized lookup matches both identity AND intended role token
        query = "SELECT Username, PasswordHash, Role FROM Users WHERE Username = %s AND Role = %s"
        record = self.db.fetch_all(query, (user, selected_role))

        if record and record[0]['PasswordHash'] == hashed_attempt:
            self.current_user = record[0]['Username']
            self.current_role = record[0]['Role']
            self.create_main_dashboard()
        else:
            messagebox.showerror("Access Denied", "Invalid credential combination or role mismatch.")

    def process_registration(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        role = self.role_combo.get()

        if not user or not pwd:
            return messagebox.showwarning("Validation Warning", "Cannot process blank accounts.")

        hashed_password = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        
        query = "INSERT INTO Users (Username, PasswordHash, Role) VALUES (%s, %s, %s)"
        if self.db.execute_query(query, (user, hashed_password, role)):
            messagebox.showinfo("Success", f"Account created! You can now log in as {role}.")
            self.show_auth_screen("login")
        else:
            messagebox.showerror("Identity Error", "Username is occupied by another system asset.")

    def create_main_dashboard(self):
        self.clear_window()
        sidebar = tk.Frame(self.root, bg="#2c3e50", width=220)
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text="SMART GYM PANEL", font=("Helvetica", 12, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)
        tk.Label(sidebar, text=f"User: {self.current_user}\nRole: {self.current_role}", font=("Helvetica", 9), bg="#34495e", fg="#bdc3c7", padx=10, pady=5).pack(fill="x", padx=10, pady=(0, 20))

        self.content_frame = tk.Frame(self.root, bg="#f4f4f9")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        routes = [("Members Module", lambda: MembersUI(self.content_frame, self.db))]
        
        # Role-based validation gate (Section 3.2 separation rules)
        if self.current_role == "Admin":
            routes.append(("Process Payments", lambda: PaymentsUI(self.content_frame, self.db)))
            routes.append(("Analytics & Reports", lambda: AnalyticsUI(self.content_frame, self.db)))
            
        routes.append(("Disconnect", lambda: self.show_auth_screen("login")))
        
        for text, command in routes:
            bg_color = "#c0392b" if text == "Disconnect" else "#34495e"
            tk.Button(sidebar, text=text, font=("Helvetica", 11), bg=bg_color, fg="white", bd=0, pady=8, cursor="hand2", command=command).pack(fill="x", pady=4, padx=10)

        MembersUI(self.content_frame, self.db)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartGymApp(root)
    root.mainloop()