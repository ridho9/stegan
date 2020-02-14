import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import N, W, E, S, HORIZONTAL, BOTH, LEFT

from PIL import Image, ImageTk

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(row=0, column=0, sticky=N+E+W+S, padx=5, pady=5)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)

        self.src_filename = tk.StringVar()
        self.show_result = tk.BooleanVar()
        self.message = tk.StringVar()
        self.bitlen = tk.IntVar()
        self.mode = tk.StringVar(value="encode")

        self.original_image = None
        self.processed_image = None

        self.create_widgets()
    
    def create_widgets(self):
        # Button for selecting source image
        file_select_button = tk.Button(self, text="Open File", command=self.select_file)
        file_select_button.grid(row=0, column=0, sticky=W+N)

        # Source image filename label
        src_filename_label = tk.Label(self, textvariable=self.src_filename)
        src_filename_label.grid(row=0, column=1, sticky=E+N)

        # Image widget row 1
        image_label = tk.Label(self, text="Image might be here later", relief="sunken")
        image_label.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)

        # Show Image Result Checkbox
        show_result_checkbox = tk.Checkbutton(
            self, text="Show Result", onvalue=True, offvalue=False, variable=self.show_result)
        show_result_checkbox.grid(row=2, column=0, sticky=W)

        # Message to hide
        message_text = tk.Text(self, height=5)
        message_text.grid(row=3, column=0, columnspan=2, sticky=W+E)

        # Password entry
        tk.Label(self, text="Password: ").grid(row=4, column=0, sticky=W)
        password_entry = tk.Entry(self)
        password_entry.grid(row=4, column=1, sticky=W)
    
        # Bit length to be used
        bitlen_scale = tk.Scale(
            self, from_=1, to=4, orient=HORIZONTAL, label="Bit Used:", variable=self.bitlen)
        bitlen_scale.grid(row=5, column=0, sticky=W)

        stats_label = tk.Label(self, text="Stats about images might be here\nlater")
        stats_label.grid(row=5, column=1, sticky=W)

        # Radio button for selecting encode/decode
        tk.Radiobutton(
            self, text="Encode", variable=self.mode, value="encode"
        ).grid(row=6, column=0, sticky=W)
        tk.Radiobutton(
            self, text="Decode", variable=self.mode, value="decode"
        ).grid(row=6, column=1, sticky=W)

        # Save button
        save_button = tk.Button(self, text="Save")
        save_button.grid(row=7, column=0, columnspan=2, sticky=E)

    def select_file(self):
        print("Select file")
        self.src_filename.set(askopenfilename())
        print(f"{self.src_filename.get()=}")