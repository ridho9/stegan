from stegan import Steganography
from stegan.psnr import mse, psnr
from PIL import Image


def test1():
    s = Steganography("images/ocean.png")

    s.set_stego_payload("content.txt", b"secret message here", "test", 1)

    img_stego = s.get_stego_image()
    with open("images/ocean-stego.png", "wb") as f:
        img_stego.save(f)

    s = Steganography("images/ocean-stego.png")
    d = s.get_stego_payload("test", 1)
    print(d)


def test2():
    s = Steganography("images/rose.bmp")

    s.set_stego_payload("content.txt", b"secret message here", "test", 2)

    img_stego = s.get_stego_image()
    with open("images/rose-stego.bmp", "wb") as f:
        img_stego.save(f)

    s = Steganography("images/rose-stego.bmp")
    d = s.get_stego_payload("test", 2)
    print(d)


def test3():
    s = Steganography("images/rose24.bmp")

    content = open("images/python-logo.png", "rb").read()

    s.set_stego_payload("python-logo-stego.png", content, "super_secret_key", 4)

    img_stego = s.get_stego_image()
    with open("images/rose24-stego.bmp", "wb") as f:
        img_stego.save(f)

    s = Steganography("images/rose24-stego.bmp")
    d = s.get_stego_payload("super_secret_key", 4)

    with open(f"images/{d[0].decode()}", "wb") as f:
        f.write(d[1])

def psnrtest():
    img1 = Image.open("images/arch.png")
    img2 = Image.open("arch-stego.png")
    mse_res = mse(img1, img2)
    psnr_res = psnr(img1, img2)
    print(f"{mse_res=} {psnr_res=}")

if __name__ == '__main__':
    # test1()
    # test2()
    # test3()
    psnrtest()
