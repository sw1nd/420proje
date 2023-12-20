import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from backend.audio_handler import load_wave_file
from backend.image_handler import load_image_file
from backend.file_handler import handle_file
import os

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Ses için Matplotlib Figure ve Canvas
        self.fig = Figure(figsize=(4, 2))  # Küçük bir figür boyutu seç
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self)  # Matplotlib canvas'ını Tkinter frame'e yerleştir
        self.audio_widget = self.canvas.get_tk_widget()
        self.audio_widget.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.audio_widget.grid_remove()

        # Başlangıçta ses widget'ını gizle
        self.audio_widget.grid_remove()
        
        # Step label

        self.step_label = tk.Label(self, text="Step 1: Select the target file:")
        self.step_label.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        # Image display area
        self.image_label = tk.Label(self, borderwidth=2, relief="groove")
        self.image_label.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        # Image details area
        self.details_text = tk.Label(self, text="Name:\nSize:\nResolution:", justify=tk.LEFT)
        self.details_text.grid(row=1, column=1, sticky='nw', padx=5)

        # Load image button

        self.load_image_button = tk.Button(self, text="Load Target File", command=self.load_audio_or_image)
        self.load_image_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Navigation buttons
        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage",None))
        self.next_button = tk.Button(self, text="Next", state='disabled', command=self.navigate_next)  # Disabled until an image is loaded

        back_button.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        self.next_button.grid(row=3, column=1, sticky='ew', padx=5, pady=5)


        # Grid configuration for resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
    def navigate_next(self):
        process_type = self.controller.shared_data['processType']
        if process_type == 'conceal':
            next_page = "PageTwo"  # Şifreleme sayfası adı
        elif process_type == 'reveal':
            next_page = "RevealPage"  # Şifre çözme sayfası adı
        else:
            next_page = "PageTwo"  # Varsayılan sayfa adı

        self.controller.show_frame(next_page, None)
    
    def show(self):
        # Sayfa her gösterildiğinde çalışacak işlevler
        self.update_ui_according_to_process_type()
        self.tkraise()

    def update_ui_according_to_process_type(self):
        process_type = self.controller.shared_data['processType']
        if process_type == "conceal":
            step_label_text = "Step 1: Select the target file:"
            button_text = "Load Target File"
        else:  # Reveal veya diğer durumlar için
            step_label_text = "Step 1: Select the source file:"
            button_text = "Load Source File"

        self.step_label.config(text=step_label_text)
        self.load_image_button.config(text=button_text)
        
    def load_audio_or_image(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(
                ("All files", "*.wav;*.bmp;*.png;*.aiff;*.tiff"),#*.jpg;*.jpeg;*.mp3;
            )
        )
        if file_path:
            file_type, file_path = handle_file(file_path)
            if file_type == 'image':
                self.controller.shared_data['file_type'] = 'image'
                self.load_image(file_path)
            elif file_type == 'audio':
                self.controller.shared_data['file_type'] = 'audio'
                self.load_audio(file_path)

    def load_image(self, file_path):
        if file_path:
            img, image_details = load_image_file(file_path)
            photo = ImageTk.PhotoImage(img)
            self.controller.shared_data['max_size_kb']  = (img.width * img.height * 3) // 8 // 1024
            self.controller.shared_data['file_path']  = file_path
            # Update the image label
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # type: ignore # Keep a reference so it's not garbage collected
            self.audio_widget.grid_remove()  # Ses widget'ını gizle
            self.image_label.grid()  # Resim widget'ını göster
            self.next_button['state'] = 'normal'
            # Update the details text
            self.details_text.configure(text=image_details)
      
          
    def load_audio(self, file_path):
        if file_path:
            signal, time, details,frames,channels = load_wave_file(file_path)
            
            # Calculate the maximum size of data that can be hidden in the audio (in kilobytes)
            audio_size_kb = (frames * channels) // 8 // 1024
            self.controller.shared_data['max_size_kb'] = audio_size_kb
            self.controller.shared_data['file_path']  = file_path
            self.image_label.grid_remove()  # Resim widget'ını gizle
            self.audio_widget.grid()  # Ses widget'ını göster
            self.next_button['state'] = 'normal'
            self.ax.clear()
            self.ax.plot(time, signal)
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Amplitude')
            self.canvas.draw()
            self.details_text.config(text=details)

