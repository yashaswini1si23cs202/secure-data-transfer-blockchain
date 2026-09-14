"""
ledger.py
---------
Real blockchain-backed version. Talks to the Ledger smart contract
(blockchain/Ledger.sol) deployed on your local Ganache chain, instead
of the local-JSON stand-in used in Phase 1.

Before this file works, you must:
  1. Have Ganache running
  2. Have run `python3 backend/deploy_contract.py` once, which creates
     backend/blockchain_config.json (contract address + ABI)

app.py never changes — it only ever calls store_hash()/get_hash(),
exactly as it did with the Phase 1 JSON stub. That's why the
blockchain logic was kept isolated in this one file from the start.
"""

import json
import os

from web3 import Web3

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, "blockchain_config.json")

_w3 = None
_contract = None
_account = None


def _load_contract():
    """Connect to Ganache and load the deployed contract, once."""
    global _w3, _contract, _account

    if _contract is not None:
        return _contract

    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(
            "backend/blockchain_config.json not found. "
            "Start Ganache, then run: python3 backend/deploy_contract.py"
        )

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    _w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
    if not _w3.is_connected():
        raise ConnectionError(
            f"Could not connect to Ganache at {config['rpc_url']}. "
            "Make sure Ganache is open and running."
        )

    _account = _w3.eth.accounts[0]
    _contract = _w3.eth.contract(
        address=config["contract_address"], abi=config["abi"]
    )
    return _contract


def store_hash(filename: str, file_hash: str) -> None:
    """Write a file's hash to the blockchain (a real transaction)."""
    contract = _load_contract()
    tx_hash = contract.functions.storeHash(filename, file_hash).transact(
        {"from": _account}
    )
    _w3.eth.wait_for_transaction_receipt(tx_hash)


def get_hash(filename: str):
    """Read a file's recorded hash from the blockchain."""
    contract = _load_contract()
    result = contract.functions.getHash(filename).call()
    return result if result else None
