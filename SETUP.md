# Blockchain-Based Secure Data Transfer System — Phase 1 scaffold

This is a **working Phase 1** of the project described in the report:
Organization A can upload a file, which gets AES-encrypted, SHA-256
hashed, and stored; Organization B can download it, and the system
re-hashes the file and checks it against the recorded hash before
handing it over.

The blockchain part (Ganache + Solidity smart contract) is stubbed out
in `ledger.py` using a local JSON file, so the whole pipeline already
runs end-to-end. Swapping that stub for real Ganache calls is Phase 2 —
see the comments at the top of `ledger.py`.

## Run it locally

```bash
python3 -m venv backend/venv
source backend/venv/bin/activate        # Windows: backend\venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/app.py
```

Open http://127.0.0.1:5000 in your browser.

- Go to **Upload (Org A)**, choose a file, submit. You'll see a flash
  message with the SHA-256 hash that was recorded.
- Go to **Download (Org B)**, type the exact filename you uploaded,
  submit. It re-hashes the stored file, compares it to the recorded
  hash, and downloads it only if they match.

## Project layout

```
backend/
  app.py              Flask routes (upload / download)
  encryption.py        AES-256 encrypt/decrypt
  hashing.py            SHA-256 file hashing
  ledger.py             Phase-1 stand-in for the blockchain (JSON file)
  requirements.txt
  storage/               "cloud storage" — encrypted files land here
  temp/                  Decrypted files, created just before download
  ledger/ledger.json    filename -> hash records (git-ignored)
frontend/
  templates/            HTML pages (Jinja2)
  static/style.css      Styling
blockchain/
  README.md             Phase 2 plan — Solidity contract goes here
```

## Phase 2 (after Sept 30): adding the real blockchain

1. Install Ganache (GUI or `npm i -g ganache`) and start a local chain.
2. Write `Ledger.sol` — a Solidity contract with `storeHash(string,string)`
   and `getHash(string) returns (string)`.
3. Compile + deploy it to Ganache (Remix IDE is the easiest way to start).
4. `pip install web3`, then replace `store_hash`/`get_hash` in
   `ledger.py` with Web3.py calls to the deployed contract (a full
   sketch is already in the comments of that file).
5. Install MetaMask, connect it to your Ganache RPC (usually
   `http://127.0.0.1:7545`), import a Ganache test account, and use it
   to sign the `storeHash` transactions from the frontend if you want
   that step to be user-facing rather than server-side.

Nothing else in the app needs to change, because `app.py` only ever
calls `store_hash()` / `get_hash()` — that's the whole point of
isolating the blockchain logic in its own module.
