import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import N, W, E, S, HORIZONTAL, BOTH, LEFT, END, NORMAL, DISABLED

from PIL import Image, ImageTk

from stegan import Steganography
from stegan.psnr import psnr

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
        self.msg_filename = tk.StringVar()
        self.password = tk.StringVar()
        self.password.trace("w", self.on_password_write)
        self.bitlen = tk.IntVar()
        self.bitlen.trace("w", self.on_bitlen_write)
        self.mode = tk.StringVar(value="encode")
        self.mode.trace("w", self.on_mode_write)
        self.psnr = tk.StringVar()

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
        self.show_result_checkbox = tk.Checkbutton(
            self, text="Show Result", onvalue=True, offvalue=False, variable=self.show_result)
        self.show_result_checkbox.grid(row=2, column=0, sticky=W)

        # Message to hide
        # self.message_entry = tk.Text(self, height=5)
        # self.message_entry.grid(row=3, column=0, columnspan=2, sticky=W+E)
        # tk.Label(self, text="Message: ").grid(row=3, column=0, sticky=W)
        # self.message_entry = tk.Entry(self, textvariable=self.message)
        # self.message_entry.grid(row=3, column=1, sticky=W+E)
        self.message_button = tk.Button(self, text="Message file", command=self.select_msg_file)
        self.message_button.grid(row=3, column=0, sticky=W)
        tk.Label(self, textvariable=self.msg_filename).grid(row=3, column=1, sticky=W+E)

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

        tk.Label(self, text="PSNR").grid(row=6, column=0, sticky=W)
        tk.Label(self, textvariable=self.psnr).grid(row=6, column=1, sticky=W)

        # Radio button for selecting encode/decode
        tk.Radiobutton(
            self, text="Encode", variable=self.mode, value="encode"
        ).grid(row=7, column=0, sticky=W)
        tk.Radiobutton(
            self, text="Decode", variable=self.mode, value="decode"
        ).grid(row=7, column=1, sticky=W)

        # Save button
        self.save_button = tk.Button(self, text="Save", command=self.save_file)
        self.save_button.grid(row=8, column=0, columnspan=2, sticky=E)

    def select_file(self):
        filename = askopenfilename(filetypes=[("Image","*.png"), ("Image","*.bmp")])
        self.src_filename.set(filename)
    
    def select_msg_file(self):
        if self.mode.get() == "decode": return
        filename = askopenfilename(filetypes=[("Text","*.txt")])
        self.msg_filename.set(filename)
        if filename == '': return
        with open(filename, "r") as f:
            content = f.read()
            self.message.set(content)
    
    def update_stats_label(self, *args):
        if not self.is_file_set():
            self.stats_label["text"] = "Stats about images might be here later"
            return

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
    
    def update_image_shown(self):
        mode = self.mode.get()
        print(f"update img shown {mode=}")
        if mode == "encode":
            new_image = self.encode_image() or self.original_image
            self.processed_image = new_image
            print(f"update_image {self.original_image=} {self.processed_image=}")
            psnr_res = psnr(self.original_image, self.processed_image)
            self.psnr.set(f"{psnr_res}")
        else:
            message = self.decode_image()
            print(f"decode {message=}")
            if message is not None:
                self.message.set(message.decode())
                self.msg_filename.set(f"{message[:32]}...")
                self.save_button["state"] = NORMAL
            else:
                self.message.set("")
                self.msg_filename.set("NO MESSAGE FOUND")
                self.save_button["state"] = DISABLED
    
    def encode_image(self):
        if not self.is_file_set(): return

        src_filename = self.src_filename.get()
        msg_filename = self.msg_filename.get()
        message = self.message.get().encode()
        password = self.password.get()
        bitlen = self.bitlen.get()
        
        s = Steganography(src_filename)
        s.set_stego_payload(msg_filename, message, password, bitlen)

        print(f"encoding {src_filename=} {msg_filename=} {password=} {bitlen=}")

        result = s.get_stego_image()
        return result
    
    def decode_image(self):
        src_filename = self.src_filename.get()
        password = self.password.get()
        bitlen = self.bitlen.get()

        s = Steganography(src_filename)
        print(f"decode {password=} {bitlen=}")

        msg_filename, result = s.get_stego_payload(password, bitlen)
        # result = result.decode()
        return result

    def show_image_on_label(self, image):
        print(f"show image {image=}")
        self.current_imagetk = ImageTk.PhotoImage(image)
        self.image_label["image"] = self.current_imagetk
    
    def reset_options_state(self):
        self.show_result.set(False)
        self.on_show_result_write()
        self.bitlen.set(1)
        self.mode.set("encode")
    
    def save_file(self):
        if not self.is_file_set(): return

        mode = self.mode.get()
        src_filename = self.src_filename.get().split("/")[-1]
        name, ext = src_filename.split(".")
        if mode == "encode":
            initialfile = f"{name}-stego.{ext}"
        else:
            initialfile = f"{name}.txt"

        dest_filename = asksaveasfilename(initialfile=initialfile)
        print(f"save {dest_filename=}")

        if dest_filename == "": return

        with open(dest_filename, "wb") as f:
            if mode == "encode":
                self.processed_image.save(f)
            else:
                f.write(self.message.get().encode())
    
    def is_file_set(self):
        src_filename = self.src_filename.get()
        msg_filename = self.msg_filename.get()
        if src_filename == "" or msg_filename == "":
            return False
        return True

    def on_src_filename_write(self, *args):
        filename = self.src_filename.get()
        print(f"src_filename change {filename=}")
        if filename == '': return

        self.original_image = Image.open(filename)
        self.processed_image = Image.open(filename)
        
        print(f"src fn w {self.original_image=} {self.processed_image=}")

        self.reset_options_state()
        self.update_stats_label()
    
    def on_show_result_write(self, *args):
        self.image_label["image"] = None
        show_result = self.show_result.get()
        if show_result:
            image = self.processed_image
        else:
            image = self.original_image
        print(f"show result write {show_result=} {image=}")
        self.show_image_on_label(image)
    
    def on_mode_write(self, *args):
        mode = self.mode.get()
        self.save_button["state"] = NORMAL
        self.psnr.set("")
        if mode == "encode":
            # self.message_entry["state"] = "normal"
            self.message_button["state"] = NORMAL
            self.msg_filename.set("")
            self.message.set("")
            self.show_result_checkbox["state"] = NORMAL
            self.show_result.set(False)
        else:
            # self.message_entry["state"] = "disabled"
            self.message_button["state"] = "disabled"
            self.msg_filename.set("Decoding message")
            self.show_result_checkbox["state"] = NORMAL
            self.show_result.set(True)
        self.update_image_shown()
        self.update_stats_label()
    
    def on_bitlen_write(self, *args):
        self.update_stats_label()
        self.update_image_shown()
    
    def on_message_write(self, *args):
        self.update_stats_label()
        if self.mode.get() == "encode":
            self.update_image_shown()
    
    def on_password_write(self, *args):
        self.update_stats_label()
        self.update_image_shown()
