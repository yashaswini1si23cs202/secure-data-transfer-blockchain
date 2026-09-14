# blockchain/

`Ledger.sol` — the smart contract that records each file's SHA-256
hash on-chain, with `storeHash()`, `getHash()`, and `getUploader()`.

## How it fits together

1. Install and open **Ganache** (free, local blockchain — see main
   SETUP.md for install steps).
2. Run `python3 backend/deploy_contract.py` — this compiles
   `Ledger.sol` and deploys it to your running Ganache instance,
   saving the deployed address + ABI to `backend/blockchain_config.json`.
3. `backend/ledger.py` reads that config and calls the deployed
   contract via Web3.py — `store_hash()` and `get_hash()` are now
   real blockchain transactions/reads instead of a local JSON file.
4. `app.py` didn't need to change at all, because it only ever calls
   `store_hash()` / `get_hash()` — the blockchain details were kept
   isolated in `ledger.py` from the start.

## Important: redeploy after restarting Ganache

A fresh Ganache chain (unless you save its workspace) has no
contracts on it. If you restart Ganache and get "contract not found"
errors, just re-run `python3 backend/deploy_contract.py` — it deploys
a fresh copy and updates the config automatically.
