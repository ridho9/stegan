import tkinter as tk
from app import App

root = tk.Tk()
root.geometry("800x600")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
app = App(root)
root.mainloop()
