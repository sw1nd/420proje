import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from backend.stegano_backend import *

class EncryptionOptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Encryption Algorithms Frame
        encryption_frame = tk.LabelFrame(self, text="Encryption Algorithms", padx=5, pady=5)
        encryption_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nwse")

        # Hashing Algorithms Frame
        hashing_frame = tk.LabelFrame(self, text="Hashing Algorithms", padx=5, pady=5)
        hashing_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nwse")

        # Radio Buttons for Encryption Algorithms
        self.encryption_var = tk.StringVar()
        self.encryption_options = {
            "AES": "AES"
        }
        #for (text, value) in self.encryption_options.items():
        #    tk.Radiobutton(encryption_frame, text=text, variable=self.encryption_var, value=value).pack(anchor="w")

        # Radio Buttons for Hashing Algorithms
        self.hashing_var = tk.StringVar()
        self.hashing_options = {
            "MD5": "MD5"
        }
        #for (text, value) in self.hashing_options.items():
        #    tk.Radiobutton(hashing_frame, text=text, variable=self.hashing_var, value=value).pack(anchor="w")

        for option in self.encryption_options.values():
            self.encryption_var.set(option)  # Varsayılan değeri ayarla
            tk.Radiobutton(encryption_frame, text=option, variable=self.encryption_var, value=option, state='disabled').pack(anchor="w")

        for option in self.hashing_options.values():
            self.hashing_var.set(option)  # Varsayılan değeri ayarla
            tk.Radiobutton(hashing_frame, text=option, variable=self.hashing_var, value=option, state='disabled').pack(anchor="w")
            
        # Password Entry
        tk.Label(self, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = tk.Entry(self)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # Navigation Buttons
        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("PageTwo",self.controller.shared_data['processType']))
        self.next_button = tk.Button(self, text="Next", command=self.next_button_clicked, state='disabled')
        finish_button = tk.Button(self, text="Finish", command=lambda: controller.finish())

        back_button.grid(row=2, column=0, padx=5, pady=5, sticky="we")
        self.next_button.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        finish_button.grid(row=2, column=2, padx=5, pady=5, sticky="we")

        # Grid Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.password_entry.bind("<KeyRelease>", self.on_password_change)
    
    def get_encryption_details(self):
        return {
            'algorithm': self.encryption_var.get(),
            'hashing': self.hashing_var.get(),
            'password': self.password_entry.get()
        }

    def on_password_change(self, event=None):
        password = self.password_entry.get()
        if password:
            self.next_button['state'] = 'normal'
        else:
            self.next_button['state'] = 'disabled'
            
    def next_button_clicked(self):
        encryption_details = self.get_encryption_details()
        password = encryption_details['password'].encode()
        data = self.controller.shared_data
        binary_data = create_data_structure_with_hash(data['txt_paths'],password,)
        file_type, file_extension = get_file_type_and_extension(data['file_path'])
        # Dosya türüne göre uygun filetypes ve defaultextension ayarla
        if file_type == "image":
            filetypes = [("Image files", "*.bmp;*.png;*.tiff")]
            defaultextension = file_extension
        elif file_type == "audio":
            filetypes = [("WAV files", "*.wav;*.aiff;")]
            defaultextension = file_extension
        else:
            # Bilinmeyen dosya türü için genel bir ayar
            filetypes = [("All Files","*.wav;*.bmp;*.png;*.aiff;*.tiff")]
            defaultextension = file_extension
            
        if file_type == "image":
            new_image = hide_data_in_image(data['file_path'],binary_data)
            output_path = filedialog.asksaveasfilename(defaultextension=defaultextension, filetypes=filetypes)
            self.controller.shared_data['output_path']=output_path
            if output_path:
                new_image.save(output_path)
        else:
            params, frames = hide_data_in_audio(data['file_path'],binary_data)
            output_path = filedialog.asksaveasfilename(defaultextension=defaultextension, filetypes=filetypes)
            self.controller.shared_data['output_path']=output_path
            if output_path:
                with wave.open(output_path, 'wb') as output_audio_file:
                    output_audio_file.setparams(params)
                    output_audio_file.writeframes(frames) 
        # İşlem tamamlandıktan sonra sonraki sayfaya geç
        if output_path:
            self.controller.show_frame("FinishPage", self.controller.shared_data['processType'])