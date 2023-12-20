import tkinter as tk
from tkinter import messagebox 
import os
import subprocess

class FinishPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        tk.Label(self, text="Dosya başarıyla kaydedildi!").pack(pady=10)

        # Finish butonu
        finish_button = tk.Button(self, text="Finish", command=self.finish)
        finish_button.pack(pady=5)

        # Dosyayı Göster butonu
        show_file_button = tk.Button(self, text="Dosyayı Göster", command=self.show_file)
        show_file_button.pack(pady=5)

    def finish(self):
        # Uygulamadan çıkış veya başka bir işlem
        self.controller.quit()

    def show_file(self):
        # Kaydedilen dosyayı aç
        output_path = self.controller.shared_data['output_path']
        if output_path and os.path.exists(output_path):
            try:
                if os.name == 'nt':  # Windows için
                    os.startfile(output_path)
                elif os.name == 'posix':  # macOS ve Linux için
                    if os.name == 'darwin':  # macOS için
                        subprocess.call(('open', output_path))
                    else:  # Linux için
                        subprocess.call(('xdg-open', output_path))
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya açılırken bir hata oluştu: {e}")
        else:
            messagebox.showerror("Hata", "Dosya bulunamadı veya henüz kaydedilmedi.")
