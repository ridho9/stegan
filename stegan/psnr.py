from PIL import Image
from math import log10

def mse(img1, img2):
    size1 = img1.size
    size2 = img2.size
    if size1 != size2:
        raise Exception("Size is different")

    data1 = img1.getdata()
    data2 = img2.getdata()

    mode = img1.mode

    w, h = size1
    total = 0
    for x in range(w):
        for y in range(h):
            index = x + w*y
            if mode in ["RGB", "RGBA"]:
                r1, g1, b1 = data1[index][:3]
                r2, g2, b2 = data2[index][:3]
                dr = (r1 - r2)**2
                dg = (g1 - g2)**2
                db = (b1 - b2)**2
                total += dr + dg + db
            elif mode in ["L", "P"]:
                p1 = data1[index]
                p2 = data2[index]
                total += (p1 - p2) ** 2
    
    total /= w * h
    total /= 3
    return total

def psnr(img1, img2):
    mse_res = mse(img1, img2)
    b = 8
    maxi = 2**b - 1

    return 10 * log10(maxi**2 / mse_res)