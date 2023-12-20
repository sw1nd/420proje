import tkinter as tk
from .startPage import StartPage
from .concealPageStep1 import PageOne
from .revealPageStep1 import PageTwo
from .EncryptionOptionsPage import EncryptionOptionsPage
from .FinishPage import FinishPage
from .RevealPage import RevealPage

class MainApp(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("SteganoGraphy UI")
        self.resizable(False, False)
        self.loaded_data = None
        #self.processType = None
        self.shared_data = {'processType': None, 'max_size_kb': None, 'file_path': None,'txt_paths': [],'output_path': None,'file_type':None}
        #self.shared_data = {'max_size_kb': None}
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Tüm sayfaları tutacak sözlük
        self.frames = {}
        
        
        # Sayfaları konteyner içinde oluştur
        for F in (StartPage, PageOne, PageTwo, EncryptionOptionsPage, FinishPage, RevealPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # Tüm sayfalar aynı grid pozisyonunda olacak
            frame.grid(row=0, column=0, sticky="nsew")

        # İlk sayfayı göster
        self.show_frame("StartPage", None)
        
        
    def center_window(self):
            self.update_idletasks()  # Update "requested size" from geometry manager
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            
    def show_frame1(self, page_name, type):
        if(page_name == "PageOne"):
            self.geometry("700x500")
            self.center_window()
            self.processType = type
        if(page_name == "StartPage"):
            self.geometry("400x300")
            self.center_window()
            self.processType = None
        frame = self.frames[page_name]
        if hasattr(frame, "show"):
            frame.show()
        else:
            frame.tkraise()
        
    def show_frame(self, page_name, processType):
        self.shared_data['processType'] = processType

        if page_name == "PageOne":
            self.geometry("700x500")
            self.center_window()

        elif page_name == "StartPage":
            self.geometry("400x300")
            self.center_window()
            self.shared_data['processType'] = None

        frame = self.frames[page_name]

        # Özel gösterim metodu olan sayfalar için
        if hasattr(frame, "show"):
            frame.show()

        # PageTwo'ya geçerken max_size_kb değerini güncelle
        elif page_name == "PageTwo" and 'max_size_kb' in self.shared_data:
            frame.update_max_size_kb(self.shared_data['max_size_kb'])

        frame.tkraise()   
         
    def quit_app(self):
        # This will destroy the main window and terminate the application
        self.destroy()