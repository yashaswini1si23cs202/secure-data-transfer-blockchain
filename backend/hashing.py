"""
hashing.py
----------
Generates the SHA-256 hash of a file. This hash is the "fingerprint"
that will later be stored on the blockchain (Phase 2) so that any
change to the stored file can be detected — even a single changed
byte produces a completely different hash.
"""

import hashlib


def generate_file_hash(file_path: str) -> str:
    """Return the SHA-256 hash (hex string) of a file's contents."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks so large files don't blow up memory
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
