"""
deploy_contract.py
-------------------
Compiles blockchain/Ledger.sol and deploys it to your locally running
Ganache instance. Run this ONCE after starting Ganache (and again any
time you restart Ganache without a saved workspace, since a fresh
Ganache chain has no contracts on it yet).

This version calls the `solc` command directly (installed via
`brew install solidity`) instead of using py-solc-x's compile
function — py-solc-x only recognizes compilers it downloaded itself,
so it doesn't see a Homebrew-installed solc. Calling solc directly
sidesteps that, and also avoids networks that block py-solc-x's
download source (solc-bin.ethereum.org).

It also compiles with --evm-version london: solc 0.8.20+ defaults to
emitting the PUSH0 instruction, which Ganache's local EVM doesn't yet
support and causes an "invalid opcode" crash on deploy. Targeting the
London EVM version avoids PUSH0 entirely and is fully compatible with
Ganache.

What this does, step by step:
  1. Runs `solc` on blockchain/Ledger.sol to get its ABI + bytecode
  2. Connects to Ganache over its RPC URL
  3. Deploys the compiled contract using one of Ganache's test accounts
  4. Saves the deployed contract's address + ABI to
     backend/blockchain_config.json, which backend/ledger.py reads

Usage:
    python3 backend/deploy_contract.py
"""

import json
import os
import subprocess

from web3 import Web3

BASE_DIR = os.path.dirname(__file__)
CONTRACT_PATH = os.path.join(BASE_DIR, "..", "blockchain", "Ledger.sol")
CONFIG_PATH = os.path.join(BASE_DIR, "blockchain_config.json")

# Ganache's default RPC URL (GUI app). If you're using ganache-cli instead,
# it also defaults to this, but double check the "RPC SERVER" address shown
# in your Ganache window.
GANACHE_RPC_URL = "http://127.0.0.1:7545"


def compile_contract():
    print("Compiling Ledger.sol with your installed solc...")
    result = subprocess.run(
        [
            "solc",
            "--combined-json", "abi,bin",
            "--evm-version", "london",  # avoids PUSH0, which Ganache can't run
            CONTRACT_PATH,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"solc failed to compile:\n{result.stderr}")

    output = json.loads(result.stdout)
    contracts = output["contracts"]

    # The key looks like "<path>:Ledger" — find whichever entry ends
    # with our contract's name, regardless of the exact path solc echoes.
    key = next(k for k in contracts if k.endswith(":Ledger"))
    contract_data = contracts[key]

    abi = contract_data["abi"]
    if isinstance(abi, str):  # some solc versions return abi as a JSON string
        abi = json.loads(abi)

    bytecode = contract_data["bin"]
    return abi, bytecode


def deploy(abi, bytecode):
    w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(
            f"Could not connect to Ganache at {GANACHE_RPC_URL}. "
            "Make sure Ganache is open and running first."
        )

    deployer_account = w3.eth.accounts[0]
    print(f"Deploying from account: {deployer_account}")

    Ledger = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = Ledger.constructor().transact({"from": deployer_account})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress
    print(f"Contract deployed at: {contract_address}")
    return contract_address


def save_config(address, abi):
    config = {"contract_address": address, "abi": abi, "rpc_url": GANACHE_RPC_URL}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved deployment info to {CONFIG_PATH}")


if __name__ == "__main__":
    abi, bytecode = compile_contract()
    address = deploy(abi, bytecode)
    save_config(address, abi)
    print("\nDone. backend/ledger.py will automatically pick this up.")
