"""
encryption.py
--------------
Handles AES-256 encryption and decryption of files for the
Blockchain-Based Secure Data Transfer System.

Why AES-CBC?
- AES is a symmetric cipher: the SAME key encrypts and decrypts.
  Both Organization A (uploader) and Organization B (downloader)
  must share this key out-of-band (in a real deployment this key
  exchange would itself be secured, e.g. with RSA — that is a good
  "future work" extension to mention in your viva).
- CBC mode needs a random IV (Initialization Vector) per file so
  that encrypting the same file twice never produces the same
  ciphertext.
- We pad the plaintext to a multiple of 16 bytes (AES block size)
  using PKCS7 padding.
"""

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# In a real system this key would come from a secure key-management
# service or be exchanged via RSA. For the project demo we load it
# from a local file so both upload and download use the same key.
KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")


def get_or_create_key():
    """Load the AES-256 key, creating one on first run."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = get_random_bytes(32)  # 32 bytes = AES-256
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def encrypt_file(input_path: str, output_path: str) -> None:
    """Encrypt input_path and write IV + ciphertext to output_path."""
    key = get_or_create_key()
    iv = get_random_bytes(16)  # AES block size = 16 bytes
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(input_path, "rb") as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    # Store IV alongside the ciphertext (IV is not secret, just unique)
    with open(output_path, "wb") as f:
        f.write(iv + ciphertext)


def decrypt_file(input_path: str, output_path: str) -> None:
    """Decrypt a file produced by encrypt_file()."""
    key = get_or_create_key()

    with open(input_path, "rb") as f:
        raw = f.read()

    iv, ciphertext = raw[:16], raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    with open(output_path, "wb") as f:
        f.write(plaintext)
