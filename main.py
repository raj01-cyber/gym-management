import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from database_manager import DatabaseManager

from modules.members_module import MembersUI
from modules.payments_module import PaymentsUI
from modules.analytics_module import AnalyticsUI
from modules.operations_module import OperationsUI

class SmartGymApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Management System")
        self.root.geometry("1150x750")
        self.root.configure(bg="#f4f4f9")
        
        self.db = DatabaseManager()
        self.current_user = None
        self.current_role = None
        self.show_auth_screen(mode="login")

    def clear_window(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def show_auth_screen(self, mode="login"):
        self.clear_window()
        auth_frame = tk.Frame(self.root, bg="#ffffff", padx=40, pady=40, bd=1, relief="solid")
        auth_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_text = "Login" if mode == "login" else "New User Registration"
        tk.Label(auth_frame, text=title_text, font=("Helvetica", 16, "bold"), bg="#ffffff").pack(pady=(0, 20))

        tk.Label(auth_frame, text="Username:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
        self.user_entry = ttk.Entry(auth_frame, font=("Helvetica", 11))
        self.user_entry.pack(fill="x", pady=(0, 10))

        tk.Label(auth_frame, text="Password:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
        self.pass_entry = ttk.Entry(auth_frame, font=("Helvetica", 11), show="*")
        self.pass_entry.pack(fill="x", pady=(0, 10))

        if mode == "register":
            tk.Label(auth_frame, text="Confirm Password:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
            self.confirm_entry = ttk.Entry(auth_frame, font=("Helvetica", 11), show="*")
            self.confirm_entry.pack(fill="x", pady=(0, 10))
            
            tk.Label(auth_frame, text="Select Workspace Role:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
            self.role_combo = ttk.Combobox(auth_frame, values=["Admin", "Trainer"], state="readonly")
            self.role_combo.current(0)
            self.role_combo.pack(fill="x", pady=(0, 20))

            tk.Button(auth_frame, text="Register Account", font=("Helvetica", 11, "bold"), bg="#28a745", fg="white", bd=0, command=self.process_registration).pack(fill="x")
            tk.Button(auth_frame, text="Back to Login", font=("Helvetica", 10), bg="#ffffff", fg="#6c757d", bd=0, command=lambda: self.show_auth_screen("login")).pack(fill="x", pady=(10, 0))
        else:
            tk.Label(auth_frame, text="Select Login Role:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w", pady=(10, 0))
            self.login_role_var = tk.StringVar(value="Admin") 
            
            radio_frame = tk.Frame(auth_frame, bg="#ffffff")
            radio_frame.pack(fill="x", pady=(0, 15))
            tk.Radiobutton(radio_frame, text="Admin", variable=self.login_role_var, value="Admin", bg="#ffffff", font=("Helvetica", 10)).pack(side="left", padx=(0, 15))
            tk.Radiobutton(radio_frame, text="Trainer", variable=self.login_role_var, value="Trainer", bg="#ffffff", font=("Helvetica", 10)).pack(side="left")
            tk.Button(auth_frame, text="Login", font=("Helvetica", 11, "bold"), bg="#007bff", fg="white", bd=0, command=self.process_login).pack(fill="x", pady=(10, 0))
            tk.Button(auth_frame, text="Create New Account", font=("Helvetica", 10), bg="#ffffff", fg="#007bff", bd=0, command=lambda: self.show_auth_screen("register")).pack(fill="x", pady=(10, 0))

    def process_login(self):
        user, pwd = self.user_entry.get().strip(), self.pass_entry.get().strip()
        selected_role = self.login_role_var.get()
        if not user or not pwd: return messagebox.showwarning("Warning", "Fields cannot be blank.")
        
        hashed_attempt = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        record = self.db.fetch_all("SELECT PasswordHash, Role FROM Users WHERE Username = %s AND Role = %s", (user, selected_role))

        if record and record[0]['PasswordHash'] == hashed_attempt:
            self.current_user = user; self.current_role = record[0]['Role']
            self.create_main_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Credentials or Incorrect Role Selected.")

    def process_registration(self):
        user, pwd = self.user_entry.get().strip(), self.pass_entry.get().strip()
        confirm, r = self.confirm_entry.get().strip(), self.role_combo.get()
        
        if not user or not pwd or not confirm: 
            return messagebox.showwarning("Validation Error", "All input values required.")
        if pwd != confirm:
            return messagebox.showerror("Security Error", "Passwords do not match!")
            
        collision = self.db.fetch_all("SELECT Username FROM Users WHERE Username = %s", (user,))
        if collision:
            return messagebox.showerror("Registration Conflict", f"The identifier '{user}' is already registered.")

        hashed = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        if self.db.execute_query("INSERT INTO Users (Username, PasswordHash, Role) VALUES (%s, %s, %s)", (user, hashed, r)):
            messagebox.showinfo("Success", "Registered! Log in now.")
            self.show_auth_screen("login")

    def create_main_dashboard(self):
        self.clear_window()
        sidebar = tk.Frame(self.root, bg="#2c3e50", width=220)
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text=f"User: {self.current_user}\nRole: {self.current_role}", font=("Helvetica", 9), bg="#34495e", fg="#bdc3c7", pady=5).pack(fill="x", pady=20)
        self.content_frame = tk.Frame(self.root, bg="#f4f4f9")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        routes = [
            ("Members Profile", lambda: MembersUI(self.content_frame, self.db)),
            ("Attendence & Bookings", lambda: OperationsUI(self.content_frame, self.db))
        ]
        if self.current_role == "Admin":
            routes.append(("Process Payments", lambda: PaymentsUI(self.content_frame, self.db)))
            routes.append(("Analytics & Reports", lambda: AnalyticsUI(self.content_frame, self.db)))
        routes.append(("Logout", lambda: self.show_auth_screen("login")))
        
        for text, command in routes:
            tk.Button(sidebar, text=text, font=("Helvetica", 11), bg="#34495e", fg="white", bd=0, pady=8, command=command).pack(fill="x", pady=4, padx=10)

        MembersUI(self.content_frame, self.db)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartGymApp(root)
    root.mainloop()