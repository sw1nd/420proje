import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from backend.stegano_backend import *

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.max_size_kb = 0
        self.current_size_kb = 0
        self.files = []
        self.step_label = tk.Label(self, text="Step 2: Select the file must be add into the target file:")
        self.step_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        # Remaining size label
        self.remaining_size_label = tk.Label(self, text=f"Remaining KB: {self.max_size_kb}")
        self.remaining_size_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        style = ttk.Style()
        style.theme_use("default")

        # 'Treeview' widget'ı için stil ayarları
        style.configure("Treeview", background="white", foreground="black", rowheight=25)
        style.configure("Treeview.Heading", font=('Calibri', 10, 'bold'))
        style.map('Treeview', background=[('selected', 'blue')])

        # 'Treeview' ve 'Heading' için siyah çizgiler eklemek
        style.layout("Treeview", [('Treeview.field', {'sticky': 'nswe'})])
        style.layout("Treeview.Heading", [('Treeview.Heading.cell', {'sticky': 'nswe'}), 
                                        ('Treeview.Heading.border', {'sticky': 'nswe', 'children': 
                                            [('Treeview.Heading.padding', {'sticky': 'nswe', 'children': 
                                                [('Treeview.Heading.image', {'side': 'right', 'sticky': ''}), 
                                                    ('Treeview.Heading.text', {'sticky': 'we'})]})]})])

        style.configure("Treeview.Heading", background="lightgrey", foreground="black", relief="flat")
        style.map("Treeview.Heading", relief=[('active', 'groove'),('pressed', 'sunken')])

        # 'Treeview' sütunlarını oluştur
        self.tree = ttk.Treeview(self, style="Treeview")
        self.tree['columns'] = ('File Type', 'Name', 'Size (KB)')

        # Sütun başlıklarını yapılandır
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("File Type", anchor=tk.W, width=120)
        self.tree.column("Name", anchor=tk.W, width=240)
        self.tree.column("Size (KB)", anchor=tk.W, width=120)

        # Sütun başlıklarını tanımla
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("File Type", text="File Type", anchor=tk.W)
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Size (KB)", text="Size (KB)", anchor=tk.W)
        # Treeview widget'ını yerleştir
        self.tree.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')
        # Treeview for listing files
        # Add and remove buttons
        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("PageOne",self.controller.shared_data['processType']))
        self.next_button = tk.Button(self, text="Next", state='disabled', command=lambda: controller.show_frame("EncryptionOptionsPage",self.controller.shared_data['processType']))  # Disabled until a file is added
        add_button = tk.Button(self, text="Add File", command=self.add_file)
        remove_button = tk.Button(self, text="Remove File", command=self.remove_file)

        # Butonların yerleştirilmesi
        back_button.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        self.next_button.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        add_button.grid(row=3, column=2, sticky='ew', padx=5, pady=5)
        remove_button.grid(row=3, column=3, sticky='ew', padx=5, pady=5)

        # Butonların boyutlarını sabitlemek için
        back_button.config(width=10, height=1)
        self.next_button.config(width=10, height=1)
        add_button.config(width=10, height=1)
        remove_button.config(width=10, height=1)

        # Grid konfigürasyonu
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def update_max_size_kb(self, new_max_size_kb):
        self.max_size_kb = round(new_max_size_kb, 2)

        self.remaining_size_label.config(text=f"Remaining KB: {self.max_size_kb}")    

    def add_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            file_size_kb = calculate_file_structure_size(file_path) /8 / 1024
            if self.current_size_kb + file_size_kb <= self.max_size_kb:
                self.current_size_kb += file_size_kb
                file_name = os.path.basename(file_path)
                file_info = ('txt', file_name, round(file_size_kb, 2))
                self.files.append(file_info)
                self.tree.insert("", "end", values=file_info)
                self.remaining_size_label.config(text=f"Remaining KB: {self.max_size_kb - self.current_size_kb:.2f}")
                self.next_button['state'] = 'normal'
                self.controller.shared_data['txt_paths'].append(file_path)
            else:
                messagebox.showerror("Error", "The file can't be added. Too long to be attached!")

    def remove_file(self):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            values = self.tree.item(selected_item, "values")
            file_name = values[1]
            file_size_kb = float(values[2])

            self.current_size_kb -= file_size_kb

            self.tree.delete(selected_item)
            self.files = [file for file in self.files if file[1] != file_name]

            self.remaining_size_label.config(text=f"Remaining KB: {self.max_size_kb - self.current_size_kb:.2f}")
            if not self.files:  
                self.next_button['state'] = 'disabled'
            if 'txt_paths' in self.controller.shared_data:
                self.controller.shared_data['txt_paths'] = [path for path in self.controller.shared_data['txt_paths'] if os.path.basename(path) != file_name]
        else:
            messagebox.showwarning("Warning", "Please select a file to remove.")


