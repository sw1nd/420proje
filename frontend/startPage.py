import tkinter as tk

class StartPage(tk.Frame):
  
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        #tk.Label(self, text="This is the start page").pack(side="top", fill="x", pady=10)
        outline_frame = tk.Frame(self,background="black")
        outline_frame.pack(padx=25, pady=55)
        main_frame = tk.Frame(outline_frame,background="white")
        main_frame.pack(padx=1, pady=1)
        encryption_button_frame = tk.Frame(main_frame, background='black') 
        encryption_button_frame.pack(padx=20, pady=8) 
        decryption_button_frame = tk.Frame(main_frame, background='black') 
        decryption_button_frame.pack(padx=20, pady=8)
        exit_button_frame = tk.Frame(main_frame, background='black') 
        exit_button_frame.pack(padx=20, pady=8)

        encryption_button = tk.Button(encryption_button_frame, text="Conceal Information", bg="white", fg="black",
                                    command=lambda: controller.show_frame("PageOne","conceal"),
                                    width=20, height=1, font=('Helvetica', '16'))
        encryption_button.pack(padx=1, pady=1)
        decryption_button = tk.Button(decryption_button_frame, text="Reveal Information", bg="white", fg="black",
                                    command=lambda: controller.show_frame("PageOne","reveal"),
                                    width=20, height=1, font=('Helvetica', '16'))
        decryption_button.pack(padx=1, pady=1)
        exit_button = tk.Button(exit_button_frame, text="Exit", bg="red", fg="white", command=controller.quit_app,
                                width=10, height=1, font=('Helvetica', '12'))
        exit_button.pack(padx=1, pady=1)
    
