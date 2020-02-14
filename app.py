import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import N, W, E, S, HORIZONTAL, BOTH, LEFT, END

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
        self.src_filename.trace("w", self.on_src_filename_write)
        self.show_result = tk.BooleanVar()
        self.show_result.trace("w", self.on_show_result_write)
        self.message = tk.StringVar()
        self.message.trace("w", self.on_message_write)
        self.password = tk.StringVar()
        self.password.trace("w", self.on_password_write)
        self.bitlen = tk.IntVar()
        self.bitlen.trace("w", self.on_bitlen_write)
        self.mode = tk.StringVar(value="encode")

        self.original_image = None
        self.processed_image = None
        self.current_imagetk = None

        self.create_widgets()
    
    def create_widgets(self):
        # Button for selecting source image
        file_select_button = tk.Button(self, text="Open File", command=self.select_file)
        file_select_button.grid(row=0, column=0, sticky=W+N)

        # Source image filename label
        src_filename_label = tk.Label(self, textvariable=self.src_filename)
        src_filename_label.grid(row=0, column=1, sticky=E+N)

        # Image widget row 1
        self.image_label = tk.Label(
            self, text="Image might be here later", relief="sunken")
        self.image_label.grid(row=1, column=0, columnspan=2, sticky=N+E+W+S)

        # Show Image Result Checkbox
        show_result_checkbox = tk.Checkbutton(
            self, text="Show Result", onvalue=True, offvalue=False, variable=self.show_result)
        show_result_checkbox.grid(row=2, column=0, sticky=W)

        # Message to hide
        # self.message_entry = tk.Text(self, height=5)
        # self.message_entry.grid(row=3, column=0, columnspan=2, sticky=W+E)
        tk.Label(self, text="Message: ").grid(row=3, column=0, sticky=W)
        self.message_entry = tk.Entry(self, textvariable=self.message)
        self.message_entry.grid(row=3, column=1, sticky=W+E)

        # Password entry
        tk.Label(self, text="Password: ").grid(row=4, column=0, sticky=W)
        password_entry = tk.Entry(self, textvariable=self.password)
        password_entry.grid(row=4, column=1, sticky=W+E)
    
        # Bit length to be used
        bitlen_scale = tk.Scale(
            self, from_=1, to=4, orient=HORIZONTAL, label="Bit Used:", variable=self.bitlen)
        bitlen_scale.grid(row=5, column=0, sticky=W)

        self.stats_label = tk.Label(self, text="Stats about images might be here later", justify=LEFT)
        self.stats_label.grid(row=5, column=1, sticky=W)

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
        filename = askopenfilename(filetypes=[("Image","*.png"), ("Image","*.bmp")])
        self.src_filename.set(filename)
    
    def on_src_filename_write(self, *args):
        filename = self.src_filename.get()
        print(f"src_filename change {filename=}")

        self.original_image = Image.open(filename)
        self.processed_image = self.original_image.copy()

        self.reset_options_state()
        self.update_stats_label()
    
    def update_stats_label(self, *args):
        img_w, img_h = self.original_image.size
        avl_bit = img_w * img_h * self.bitlen.get()
        avl_byte = avl_bit // 8

        message = self.message.get()
        message_bytes = message.encode("utf-8")
        msg_len = len(message)
        msg_byte = len(message_bytes)
        byte_left = avl_byte - msg_byte

        password = self.password.get()
        enc = "encrypted" if password != "" else "not encrypted"

        result_text = f"size={img_w}x{img_h} {avl_bit=}bits {avl_byte=}bytes"
        result_text += f"\n{msg_len=} {msg_byte=} {byte_left=}bytes"
        result_text += f"\n{password=} {enc}"

        self.stats_label["text"] = result_text
    
    def reset_options_state(self):
        self.show_result.set(False)
        self.on_show_result_write()
        self.bitlen.set(1)
        self.mode.set("encode")
    
    def on_show_result_write(self, *args):
        self.image_label["image"] = None
        if self.show_result.get():
            image = self.original_image
        else:
            image = self.processed_image
        self.show_image_on_label(image)
    
    def on_bitlen_write(self, *args):
        self.update_stats_label()

    def show_image_on_label(self, image):
        self.current_imagetk = ImageTk.PhotoImage(image)
        self.image_label["image"] = self.current_imagetk
    
    def on_message_write(self, *args):
        self.update_stats_label()
    
    def on_password_write(self, *args):
        self.update_stats_label()
