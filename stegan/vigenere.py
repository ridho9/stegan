import random


class CryptoException(Exception):
    pass


class Vigenere:
    STANDARD = 1
    FULL = 2
    AUTO_KEY = 3
    RUNNING_KEY = 4
    EXTENDED = 5
    _DEFAULT_CHARSET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _DEFAULT_N = 26

    # https://stackoverflow.com/questions/43656104/creation-of-nxn-matrix-sudoku-like
    @staticmethod
    def bitcount(n):
        i = 0
        while n:
            i += 1
            n &= n - 1
        return i

    def complete(self, rowset, colset, entries):
        random.seed(self._key)
        n_size = self._DEFAULT_N
        if entries == n_size * n_size:
            return True
        i, j = max(
            ((i, j) for i in range(n_size) for j in range(n_size) if self._s_box[i][j] == 0),
            key=lambda item: (
                self.bitcount(rowset[item[0]] | colset[item[1]])
            )
        )

        bits = rowset[i] | colset[j]
        p = [n for n in range(1, n_size + 1) if not (bits >> (n - 1)) & 1]
        random.shuffle(p)

        for n in p:
            self._s_box[i][j] = n
            rowset[i] |= 1 << (n - 1)
            colset[j] |= 1 << (n - 1)
            if self.complete(rowset, colset, entries + 1):
                return True
            rowset[i] &= ~(1 << (n - 1))
            colset[j] &= ~(1 << (n - 1))

        self._s_box[i][j] = 0
        return False

    def _load_key(self):
        key = open(self._filename, "r").read()
        return ''.join(filter(str.isalpha, key.upper()))

    def __init__(self, variant, key=None, filename=None):
        if (variant < 1) and (variant > 5):
            raise CryptoException("Invalid Vigenere variant")
        self._type = variant

        if self._type == Vigenere.RUNNING_KEY:
            if filename is None:
                raise CryptoException("Need filename parameter")
            self._filename = filename

        else:
            if key is None:
                raise CryptoException("Need key parameter")

            if self._type == Vigenere.EXTENDED:
                if isinstance(key, bytes):
                    self._key = key
                else:
                    raise CryptoException("Invalid key type")
            else:
                self._key = ''.join(filter(str.isalpha, key.upper()))

            if self._type == Vigenere.FULL:
                self._s_box = [[0] * self._DEFAULT_N for _ in range(self._DEFAULT_N)]
                assert self.complete([0] * self._DEFAULT_N, [0] * self._DEFAULT_N, 0)

    def _encrypt_standard(self, plaintext: str):
        ct = ""
        idx_key = 0

        for c in plaintext:
            if c not in Vigenere._DEFAULT_CHARSET:
                ct += c
                continue

            k = Vigenere._DEFAULT_CHARSET.index(self._key[idx_key])
            c = Vigenere._DEFAULT_CHARSET.index(c)
            ct += Vigenere._DEFAULT_CHARSET[(c + k) % 26]
            idx_key += 1
            idx_key %= len(self._key)

        return ct

    def _encrypt_full_key(self, plaintext: str):
        ct = ""
        idx_key = 0

        for c in plaintext:
            if c not in Vigenere._DEFAULT_CHARSET:
                ct += c
                continue

            k = Vigenere._DEFAULT_CHARSET.index(self._key[idx_key])
            plain_pos = Vigenere._DEFAULT_CHARSET.index(c)
            cipher_pos = self._s_box[k][plain_pos] - 1
            ct += Vigenere._DEFAULT_CHARSET[cipher_pos]
            idx_key += 1
            idx_key %= len(self._key)

        return ct

    def _encrypt_auto_key(self, plaintext: str):
        ct = ""
        idx_key = 0
        extend = False

        for c in plaintext:
            if c not in Vigenere._DEFAULT_CHARSET:
                ct += c
                continue

            if not extend:
                k = Vigenere._DEFAULT_CHARSET.index(self._key[idx_key])
            else:
                while plaintext[idx_key] not in Vigenere._DEFAULT_CHARSET:
                    idx_key += 1
                k = Vigenere._DEFAULT_CHARSET.index(plaintext[idx_key])

            c = Vigenere._DEFAULT_CHARSET.index(c)
            ct += Vigenere._DEFAULT_CHARSET[(c + k) % 26]

            idx_key += 1
            if not extend:
                if idx_key == len(self._key):
                    extend = True
                    idx_key = 0

        return ct

    def _encrypt_running_key(self, plaintext: str):
        ct = ""
        idx_key = 0
        key = self._load_key()

        for c in plaintext:
            if c not in Vigenere._DEFAULT_CHARSET:
                ct += c
                continue

            k = Vigenere._DEFAULT_CHARSET.index(key[idx_key])
            c = Vigenere._DEFAULT_CHARSET.index(c)
            ct += Vigenere._DEFAULT_CHARSET[(c + k) % 26]
            idx_key += 1
            idx_key %= len(key)

        return ct

    def _encrypt_extended(self, plaintext: bytes):
        ct = b""
        idx_key = 0

        assert isinstance(self._key, bytes)

        for c in plaintext:
            k = self._key[idx_key]
            ct += bytes([(c + k) % 256])
            idx_key += 1
            idx_key %= len(self._key)

        return ct

    def encrypt(self, plaintext):
        if type(plaintext) == str:
            plaintext = plaintext.upper()

        if self._type == Vigenere.STANDARD:
            return self._encrypt_standard(plaintext)
        elif self._type == Vigenere.FULL:
            return self._encrypt_full_key(plaintext)
        elif self._type == Vigenere.AUTO_KEY:
            return self._encrypt_auto_key(plaintext)
        elif self._type == Vigenere.RUNNING_KEY:
            return self._encrypt_running_key(plaintext)
        elif self._type == Vigenere.EXTENDED:
            return self._encrypt_extended(plaintext)

    def _decrypt_standard(self, ciphertext: str):
        pt = ""
        idx_key = 0

        for c in ciphertext:
            if c not in Vigenere._DEFAULT_CHARSET:
                pt += c
                continue

            k = Vigenere._DEFAULT_CHARSET.index(self._key[idx_key])
            c = Vigenere._DEFAULT_CHARSET.index(c)
            pt += Vigenere._DEFAULT_CHARSET[(c - k) % 26]
            idx_key += 1
            idx_key %= len(self._key)

        return pt

    def _decrypt_full_key(self, ciphertext: str):
        pt = ""
        idx_key = 0

        for c in ciphertext:
            if c not in Vigenere._DEFAULT_CHARSET:
                pt += c
                continue

            k = Vigenere._DEFAULT_CHARSET.index(self._key[idx_key])
            cipher_pos = Vigenere._DEFAULT_CHARSET.index(c)
            plain_pos = self._s_box[k].index(cipher_pos + 1)
            pt += Vigenere._DEFAULT_CHARSET[plain_pos]
            idx_key += 1
            idx_key %= len(self._key)

        return pt

    def _decrypt_auto_key(self, ciphertext: str):
        pt = ""
        idx_key = 0
        extend = False

        for c in ciphertext:
            if c not in Vigenere._DEFAULT_CHARSET:
                pt += c
                continue

            if not extend:
                k = Vigenere._DEFAULT_CHARSET.index(self._key[idx_key])
            else:
                while pt[idx_key] not in Vigenere._DEFAULT_CHARSET:
                    idx_key += 1
                k = Vigenere._DEFAULT_CHARSET.index(pt[idx_key])

            c = Vigenere._DEFAULT_CHARSET.index(c)
            pt += Vigenere._DEFAULT_CHARSET[(c - k) % 26]

            idx_key += 1
            if not extend:
                if idx_key == len(self._key):
                    extend = True
                    idx_key = 0

        return pt

    def _decrypt_running_key(self, ciphertext: str):
        pt = ""
        idx_key = 0
        key = self._load_key()

        for c in ciphertext:
            if c not in Vigenere._DEFAULT_CHARSET:
                pt += c
                continue

            k = Vigenere._DEFAULT_CHARSET.index(key[idx_key])
            c = Vigenere._DEFAULT_CHARSET.index(c)
            pt += Vigenere._DEFAULT_CHARSET[(c - k) % 26]
            idx_key += 1
            idx_key %= len(key)

        return pt

    def _decrypt_extended(self, ciphertext: bytes):
        pt = b""
        idx_key = 0

        assert isinstance(self._key, bytes)

        for c in ciphertext:
            k = self._key[idx_key]
            pt += bytes([(c - k) % 256])
            idx_key += 1
            idx_key %= len(self._key)

        return pt

    def decrypt(self, ciphertext):
        if self._type == Vigenere.STANDARD:
            return self._decrypt_standard(ciphertext)
        elif self._type == Vigenere.FULL:
            return self._decrypt_full_key(ciphertext)
        elif self._type == Vigenere.AUTO_KEY:
            return self._decrypt_auto_key(ciphertext)
        elif self._type == Vigenere.RUNNING_KEY:
            return self._decrypt_running_key(ciphertext)
        elif self._type == Vigenere.EXTENDED:
            return self._decrypt_extended(ciphertext)
