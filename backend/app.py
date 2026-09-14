"""
app.py
------
Flask backend for the Blockchain-Based Secure Data Transfer System.

Routes:
  GET  /            -> home page with links to upload / download
  GET  /upload       -> upload form (Organization A)
  POST /upload       -> handles file: encrypt -> hash -> store
  GET  /download      -> download/verify form (Organization B)
  POST /download      -> re-hash stored file, compare to ledger, decrypt if match
"""

import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for

from encryption import encrypt_file, decrypt_file
from hashing import generate_file_hash
from ledger import store_hash, get_hash

BASE_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.join(BASE_DIR, "storage")       # encrypted files "in the cloud"
TEMP_DIR = os.path.join(BASE_DIR, "temp")             # decrypted files ready for download
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# templates/ and static/ live in ../frontend (a sibling folder to backend/,
# matching the repo's backend / frontend / blockchain layout)
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static"),
)
app.secret_key = "dev-secret-key-change-me"  # only for flash messages in dev


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please choose a file to upload.")
        return redirect(url_for("upload"))

    filename = file.filename
    raw_path = os.path.join(STORAGE_DIR, f"raw_{filename}")
    encrypted_path = os.path.join(STORAGE_DIR, f"{filename}.enc")

    # 1. Save the incoming file temporarily so we can hash + encrypt it
    file.save(raw_path)

    # 2. Generate SHA-256 hash of the ORIGINAL file (this is what
    #    Organization B will check integrity against later)
    file_hash = generate_file_hash(raw_path)

    # 3. Encrypt the file with AES and store the encrypted version
    #    ("cloud storage" — currently local disk, see storage/ folder)
    encrypt_file(raw_path, encrypted_path)

    # 4. Store the hash in the ledger (this call becomes a blockchain
    #    smart-contract transaction in Phase 2 — see ledger.py)
    store_hash(filename, file_hash)

    # 5. Remove the plaintext copy — only the encrypted file should
    #    remain in "cloud storage"
    os.remove(raw_path)

    flash(f"'{filename}' uploaded, encrypted, and hash recorded successfully.")
    flash(f"SHA-256: {file_hash}")
    return redirect(url_for("upload"))


@app.route("/download", methods=["GET", "POST"])
def download():
    if request.method == "GET":
        return render_template("download.html")

    filename = request.form.get("filename", "").strip()
    encrypted_path = os.path.join(STORAGE_DIR, f"{filename}.enc")

    if not os.path.exists(encrypted_path):
        flash(f"No file named '{filename}' found in storage.")
        return redirect(url_for("download"))

    # 1. Decrypt to a temp location so we can re-hash the ORIGINAL bytes
    decrypted_path = os.path.join(TEMP_DIR, filename)
    decrypt_file(encrypted_path, decrypted_path)

    # 2. Recompute the hash of the decrypted file
    current_hash = generate_file_hash(decrypted_path)

    # 3. Compare against the hash recorded at upload time
    #    (this read becomes a blockchain smart-contract call in Phase 2)
    recorded_hash = get_hash(filename)

    if recorded_hash is None:
        flash("No hash record found for this file — cannot verify integrity.")
        os.remove(decrypted_path)
        return redirect(url_for("download"))

    if current_hash != recorded_hash:
        flash("INTEGRITY CHECK FAILED — file may have been tampered with!")
        os.remove(decrypted_path)
        return redirect(url_for("download"))

    flash("Integrity verified — hashes match. Downloading file...")
    return send_file(decrypted_path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True)
