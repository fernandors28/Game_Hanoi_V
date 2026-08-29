import tkinter as tk

def Window_Game():
    root = tk.Tk()
    root.update_idletasks()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f"{width-1}x{height-1}+0+0")

    label_title = tk.Label(root, text="hola", font=("arial", 20)) 
    label_title.pack(pady=30)  


    root.mainloop()

