import tkinter as tk
from tkinter import ttk, messagebox,filedialog
from backend.stegano_backend import *

class RevealPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Password Entry at the top
        self.password_label = tk.Label(self, text="Enter Password to Unlock Files:")
        self.password_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')

        # File listing Treeview
        self.file_tree = ttk.Treeview(self)
        self.file_tree['columns'] = ('File Type', 'Name', 'Size (K)')
        self.file_tree.column("#0", width=0, stretch=tk.NO)
        self.file_tree.column("File Type", anchor=tk.W, width=120)
        self.file_tree.column("Name", anchor=tk.W, width=200)
        self.file_tree.column("Size (K)", anchor=tk.W, width=80)
        self.file_tree.heading("#0", text="", anchor=tk.W)
        self.file_tree.heading("File Type", text="File Type", anchor=tk.W)
        self.file_tree.heading("Name", text="Name", anchor=tk.W)
        self.file_tree.heading("Size (K)", text="Size (K)", anchor=tk.W)
        self.file_tree.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky='nsew')

        # Extract File button
        self.extract_button = tk.Button(self, text="Extract File", command=self.on_extract_clicked)
        self.extract_button.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky='ew')

        self.download_button = tk.Button(self, text="Download", command=self.on_download_clicked)
        self.download_button.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky='ew')
        
        # Restrict to select only one item at a time in the Treeview
        self.file_tree.configure(selectmode='browse')
        # Configure grid column expansion
        self.grid_columnconfigure(1, weight=1)

    def on_extract_clicked(self):
        password = self.password_entry.get().encode()
        key = derive_aes_key_from_password(password)
        file_type = self.controller.shared_data['file_type']
        if not password:
            messagebox.showwarning("Warning", "Please enter the password.")
            return

        file_path = self.controller.shared_data['file_path']
        if not file_path:
            messagebox.showerror("Error", "Image path is not set.")
            return

        try:
            # Assuming extract_data_from_image returns a dictionary of extracted files
            if file_type == 'image':
                extracted_files = extract_data_from_image(file_path, key)
            else:
                extracted_files = extract_data_from_audio(file_path, key)
            if extracted_files:
                self.populate_file_tree_with_extracted_data(extracted_files)
            else:
                messagebox.showinfo("Info", "No hidden files found in the image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract files: {e}")

    def on_download_clicked(self):
        selected_items = self.file_tree.selection()
        if len(selected_items) != 1:
            messagebox.showwarning("Warning", "Please select one file to download.")
            return
        
        selected_item = selected_items[0]
        file_name = self.file_tree.item(selected_item, "values")[1]
        file_content = self.extracted_files.get(file_name)

        if not file_content:
            messagebox.showerror("Error", "File content is not available.")
            return
        
        # Ask user where to save the file
        file_path = filedialog.asksaveasfilename(
            initialfile=file_name,
            filetypes=[("All files", "*.*")],
            defaultextension="*.*"
        )
        
        if not file_path:
            return  # User cancelled the save operation
        
        # Save the content to the file
        with open(file_path, 'wb') as file:
            file.write(file_content)
        
        messagebox.showinfo("Success", f"File '{file_name}' has been saved successfully.")
        
    def populate_file_tree_with_extracted_data(self, extracted_data):
        for file_name, content in extracted_data.items():
            file_size_kb = len(content) / 1024  # Assuming content is in bytes
            self.file_tree.insert("", "end", values=('txt', file_name, f"{file_size_kb:.2f}"))
            self.extracted_files = extracted_data 
