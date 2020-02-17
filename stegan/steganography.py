from PIL import Image
from bitstring import BitArray
from .vigenere import Vigenere
from struct import (
    pack,
    unpack
)

import random


class SteganographyException(Exception):
    pass


class Steganography:
    __SUPPORTED_MODE = ["RGB", "RGBA", "L", "P"]

    # Inserted payload
    # 2 bytes magic header: 0x1337
    # 2 bytes filename size: n
    # 4 bytes content size: m
    # n bytes filename
    # m bytes content
    def __init__(self, filename: str):
        self._base_image = Image.open(filename)

        if self._base_image.mode not in self.__SUPPORTED_MODE:
            raise SteganographyException("Mode not supported")

        self._payloaded_pixel = None

    @staticmethod
    def _check_lsb(lsb: int):
        if lsb > 4 or lsb < 1:
            raise SteganographyException("Invalid lsb size")

    @staticmethod
    def _put_bits(val: int, bit_mask: int, bits: str):
        if bits == "":
            return val
        return val & (~bit_mask) | int(bits, 2)

    @staticmethod
    def _roundup(val: int, n: int):
        return val if val % n == 0 else val + n - val % n

    def get_payload_size(self, lsb: int) -> int:
        self._check_lsb(lsb)

        pixels_count = self._base_image.width * self._base_image.height

        if type(self._base_image.getdata()[0]) == tuple:
            return (pixels_count * lsb * len(self._base_image.getdata()[0])) // 8

        return (pixels_count * lsb) // 8

    def get_stego_image(self) -> Image:
        if self._payloaded_pixel is None:
            return None

        img = Image.new(self._base_image.mode, self._base_image.size)
        img.putdata(self._payloaded_pixel)

        if img.mode == "P":
            img.putpalette(self._base_image.getpalette())
        return img

    def get_base_image(self) -> Image:
        return self._base_image

    def set_stego_payload(self, filename: str, payload: bytes, key: str, lsb: int):
        max_payload = self.get_payload_size(lsb) - 8 - len(filename.encode("latin-1"))

        if len(payload) > max_payload:
            raise SteganographyException("Payload too big")

        if key != "":
            vigenere = Vigenere(Vigenere.EXTENDED, key=key.encode("utf-8"))
            payload = vigenere.encrypt(payload)
            random.seed(sum([ord(key[i]) for i in range(0, len(key), 2)]))
        else:
            random.seed(key)

        pixels_count = self._base_image.width * self._base_image.height
        seq = [i for i in range(pixels_count)]
        random.shuffle(seq)

        full_payload = pack("HHI", 0x1337, len(filename), len(payload))
        full_payload += filename.encode("latin-1")
        full_payload += payload
        full_payload = BitArray(bytes=full_payload).bin
        len_payload = self._roundup(len(full_payload), lsb)
        full_payload = full_payload.ljust(len_payload, '0')

        i = 0
        bit_mask = (1 << lsb) - 1

        # make copy list pixel
        self._payloaded_pixel = list(self._base_image.getdata()).copy()

        for pos in seq:
            if i >= len(full_payload) / lsb:
                break

            temp_pixel = self._payloaded_pixel[pos]

            if type(temp_pixel) == tuple:
                list_pixel = []
                for j in range(len(temp_pixel)):
                    temp_each_pixel = temp_pixel[j]
                    temp_each_pixel = self._put_bits(temp_each_pixel, bit_mask, full_payload[lsb*i:lsb*(i+1)])
                    list_pixel.append(temp_each_pixel)
                    i += 1
                temp_pixel = tuple(list_pixel)
            else:
                temp_pixel = self._put_bits(temp_pixel, bit_mask, full_payload[lsb*i:lsb*(i+1)])
                i += 1

            self._payloaded_pixel[pos] = temp_pixel

    def get_stego_payload(self, key: str, lsb: int):
        pixel_data = list(self._base_image.getdata())
        bin_payload = ""

        if key != "":
            random.seed(sum([ord(key[i]) for i in range(0, len(key), 2)]))
        else:
            random.seed(key)

        pixels_count = self._base_image.width * self._base_image.height
        seq = [i for i in range(pixels_count)]
        random.shuffle(seq)

        for pos in seq:
            if len(bin_payload) >= 64:
                break
            temp_pixel = pixel_data[pos]

            if type(temp_pixel) == tuple:
                for j in range(len(temp_pixel)):
                    bin_payload += BitArray(int=temp_pixel[j], length=9).bin[-lsb:]
            else:
                bin_payload += BitArray(int=temp_pixel, length=9).bin[-lsb:]

        bin_payload = bin_payload[:64]

        payload = BitArray(bin=bin_payload).bytes
        header, len_filename, len_content = unpack("HHI", payload[:8])

        if header != 0x1337:
            return None, None

        bin_payload = ""
        for pos in seq:
            if len(bin_payload) >= (len_content + len_filename + 8) * 8:
                break
            temp_pixel = pixel_data[pos]

            if type(temp_pixel) == tuple:
                for j in range(len(temp_pixel)):
                    bin_payload += BitArray(int=temp_pixel[j], length=9).bin[-lsb:]
            else:
                bin_payload += BitArray(int=temp_pixel, length=9).bin[-lsb:]

        bin_payload = bin_payload[:len(bin_payload) // 8 * 8]
        payload = BitArray(bin=bin_payload).bytes
        filename = payload[8:8+len_filename]
        content = payload[8+len_filename:8+len_filename+len_content]

        if key != "":
            vigenere = Vigenere(Vigenere.EXTENDED, key=key.encode("utf-8"))
            content = vigenere.decrypt(content)

        return filename, content
