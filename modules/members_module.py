import tkinter as tk
from tkinter import ttk


class MembersUI:
   def __init__(self, parent_frame, db):
       self.parent_frame = parent_frame
       self.build_ui()


   def build_ui(self):
       for widget in self.parent_frame.winfo_children(): widget.destroy()
       tk.Label(self.parent_frame, text="Manage Gym Members", font=("Helvetica", 18, "bold"), bg="#f4f4f9").pack(anchor="w", pady=(0, 10))


       form_frame = tk.Frame(self.parent_frame, bg="#ffffff", padx=10, pady=10, bd=1, relief="groove")
       form_frame.pack(fill="x", pady=(0, 20))


       tk.Label(form_frame, text="First Name:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5)
       ttk.Entry(form_frame).grid(row=0, column=1, padx=5, pady=5)
       tk.Label(form_frame, text="Last Name:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5)
       ttk.Entry(form_frame).grid(row=0, column=3, padx=5, pady=5)


       tk.Button(form_frame, text="Add Member (Dummy)", bg="#28a745", fg="white").grid(row=1, column=0, columnspan=4, pady=10)


       self.tree = ttk.Treeview(self.parent_frame, columns=("ID", "Name"), show="headings")
       self.tree.heading("ID", text="ID"); self.tree.heading("Name", text="Name")
       self.tree.pack(fill="both", expand=True)
       self.tree.insert("", "end", values=("1", "Ram Sharma"))
