import tkinter as tk
from tkinter import ttk, messagebox


class SmartGymApp:
   def __init__(self, root):
       self.root = root
       self.root.title("Gym Management System")
       self.root.geometry("1150x750")
       self.root.configure(bg="#f4f4f9")
       self.create_login_screen()


   def clear_window(self):
       for widget in self.root.winfo_children(): widget.destroy()


   def create_login_screen(self):
       self.clear_window()
       auth_frame = tk.Frame(self.root, bg="#ffffff", padx=40, pady=40, bd=1, relief="solid")
       auth_frame.place(relx=0.5, rely=0.5, anchor="center")


       tk.Label(auth_frame, text="System Login", font=("Helvetica", 16, "bold"), bg="#ffffff").pack(pady=(0, 20))
       tk.Label(auth_frame, text="Username:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
       ttk.Entry(auth_frame, font=("Helvetica", 11)).pack(fill="x", pady=(0, 10))
       tk.Label(auth_frame, text="Password:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
       ttk.Entry(auth_frame, font=("Helvetica", 11), show="*").pack(fill="x", pady=(0, 10))


       tk.Label(auth_frame, text="Select Workspace Role:", font=("Helvetica", 11), bg="#ffffff").pack(anchor="w")
       ttk.Combobox(auth_frame, values=["Admin", "Trainer"], state="readonly").pack(fill="x", pady=(0, 20))


       tk.Button(auth_frame, text="Authenticate", font=("Helvetica", 11, "bold"), bg="#007bff", fg="white", bd=0, command=self.create_main_dashboard).pack(fill="x")


   def create_main_dashboard(self):
       self.clear_window()
       sidebar = tk.Frame(self.root, bg="#2c3e50", width=220)
       sidebar.pack(side="left", fill="y")
      
       tk.Label(sidebar, text="GYM PANEL", font=("Helvetica", 12, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)
       self.content_frame = tk.Frame(self.root, bg="#f4f4f9")
       self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)


       for text in ["Members Module", "Process Payments", "Analytics & Reports", "Logout"]:
           tk.Button(sidebar, text=text, font=("Helvetica", 11), bg="#34495e", fg="white", bd=0, pady=8).pack(fill="x", pady=4, padx=10)


       tk.Label(self.content_frame, text="Members UI", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w")
