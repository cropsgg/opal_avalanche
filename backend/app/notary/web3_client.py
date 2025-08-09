from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from eth_account import Account
from web3 import Web3

from app.core.config import get_settings


def _load_abi() -> list[dict[str, Any]]:
    # Expect abi.json placed at app/notary/abi.json
    abi_path = Path(__file__).with_name("abi.json")
    with abi_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_contract():
    settings = get_settings()
    if not (settings.AVALANCHE_RPC and settings.NOTARY_CONTRACT_ADDRESS):
        raise RuntimeError("Notary is not configured")
    w3 = Web3(Web3.HTTPProvider(settings.AVALANCHE_RPC))
    return w3, w3.eth.contract(address=settings.NOTARY_CONTRACT_ADDRESS, abi=_load_abi())


def _run_id_to_bytes32(run_id: str) -> bytes:
    # Derive bytes32 from arbitrary run_id (uuid string) using keccak for fixed length
    h = Web3.keccak(text=run_id)
    return h  # 32 bytes


def publish_root(run_id: str, root_hex: str) -> Dict[str, Any]:
    settings = get_settings()
    if not settings.PUBLISHER_PRIVATE_KEY:
        raise RuntimeError("Publisher key not configured")
    w3, contract = get_contract()
    acct = Account.from_key(settings.PUBLISHER_PRIVATE_KEY)
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = contract.functions.publish(_run_id_to_bytes32(run_id), Web3.to_bytes(hexstr=root_hex)).build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "gas": 200000,
        "maxFeePerGas": w3.to_wei("30", "gwei"),
        "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
    })
    signed = acct.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txh)
    return {"transactionHash": receipt.transactionHash.hex(), "blockNumber": receipt.blockNumber}


