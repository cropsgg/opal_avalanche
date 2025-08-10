from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from eth_account import Account
from web3 import Web3
from web3.exceptions import TransactionNotFound
import structlog

from ..config.settings import get_settings

log = structlog.get_logger()


class SubnetClient:
    """
    Web3 client for OPAL private Avalanche Subnet
    Handles contract interactions with proper nonce management and error handling
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._w3: Optional[Web3] = None
        self._contracts: Dict[str, Any] = {}
        self._account: Optional[Account] = None
        self._nonce_cache: Optional[int] = None
        
    def _get_web3(self) -> Web3:
        """Get Web3 instance with subnet connection"""
        if self._w3 is None:
            if not self.settings.SUBNET_RPC:
                raise RuntimeError("SUBNET_RPC not configured")
            
            self._w3 = Web3(Web3.HTTPProvider(self.settings.SUBNET_RPC))
            
            # Verify connection and chain ID
            if not self._w3.is_connected():
                raise RuntimeError(f"Cannot connect to subnet RPC: {self.settings.SUBNET_RPC}")
            
            chain_id = self._w3.eth.chain_id
            expected_chain_id = getattr(self.settings, 'SUBNET_CHAIN_ID', 43210)
            if chain_id != expected_chain_id:
                raise RuntimeError(f"Chain ID mismatch: got {chain_id}, expected {expected_chain_id}")
            
            log.info("subnet.connected", chain_id=chain_id, rpc=self.settings.SUBNET_RPC)
        
        return self._w3
    
    def _get_account(self) -> Account:
        """Get account from private key"""
        if self._account is None:
            if not self.settings.SUBNET_SENDER_PK:
                raise RuntimeError("SUBNET_SENDER_PK not configured")
            
            self._account = Account.from_key(self.settings.SUBNET_SENDER_PK)
            log.info("subnet.account_loaded", address=self._account.address)
        
        return self._account
    
    def _load_contract_abi(self, contract_name: str) -> list[dict[str, Any]]:
        """Load contract ABI from deployment files"""
        abi_path = Path(__file__).parent / f"{contract_name.lower()}_abi.json"
        
        if not abi_path.exists():
            raise RuntimeError(f"ABI file not found: {abi_path}")
        
        with abi_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def _get_contract(self, name: str) -> Any:
        """Get contract instance with caching"""
        if name not in self._contracts:
            w3 = self._get_web3()
            
            # Get contract address from settings
            address_attr = f"SUBNET_{name.upper()}_ADDR"
            address = getattr(self.settings, address_attr, None)
            
            if not address:
                raise RuntimeError(f"Contract address not configured: {address_attr}")
            
            abi = self._load_contract_abi(name)
            self._contracts[name] = w3.eth.contract(address=address, abi=abi)
            
            log.info("subnet.contract_loaded", name=name, address=address)
        
        return self._contracts[name]
    
    def _get_nonce(self, force_refresh: bool = False) -> int:
        """Get nonce with caching to avoid RPC calls"""
        if self._nonce_cache is None or force_refresh:
            w3 = self._get_web3()
            account = self._get_account()
            self._nonce_cache = w3.eth.get_transaction_count(account.address)
        
        return self._nonce_cache
    
    def _increment_nonce(self):
        """Increment cached nonce after successful transaction"""
        if self._nonce_cache is not None:
            self._nonce_cache += 1
    
    def _build_transaction(self, contract_function, gas_limit: int = 200000) -> dict[str, Any]:
        """Build transaction with proper gas and nonce"""
        w3 = self._get_web3()
        account = self._get_account()
        
        base_fee = w3.eth.get_block('latest').get('baseFeePerGas', 25_000_000)  # 25 gwei fallback
        max_fee = int(base_fee * 1.5)  # 50% buffer
        max_priority_fee = min(2_000_000, max_fee // 10)  # 2 gwei or 10% of max fee
        
        return contract_function.build_transaction({
            "from": account.address,
            "nonce": self._get_nonce(),
            "gas": gas_limit,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": max_priority_fee,
        })
    
    def _send_transaction(self, tx: dict[str, Any], retry_count: int = 3) -> dict[str, Any]:
        """Send transaction with retry logic"""
        w3 = self._get_web3()
        account = self._get_account()
        
        for attempt in range(retry_count):
            try:
                # Sign and send
                signed_tx = account.sign_transaction(tx)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                # Wait for receipt
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                if receipt.status == 1:
                    self._increment_nonce()
                    return {
                        "transactionHash": receipt.transactionHash.hex(),
                        "blockNumber": receipt.blockNumber,
                        "gasUsed": receipt.gasUsed,
                        "status": "success"
                    }
                else:
                    raise RuntimeError(f"Transaction failed: {receipt.transactionHash.hex()}")
                    
            except Exception as e:
                log.warning("subnet.tx_failed", attempt=attempt + 1, error=str(e))
                
                if attempt < retry_count - 1:
                    # Refresh nonce and try again
                    tx["nonce"] = self._get_nonce(force_refresh=True)
                    time.sleep(1)
                else:
                    raise
        
        raise RuntimeError("Transaction failed after all retries")
    
    # Contract interaction methods
    
    def publish_notary(self, run_id: str, root_hash: str) -> dict[str, Any]:
        """Publish notarization to Notary contract"""
        log.info("subnet.notary.publish", run_id=run_id, root_hash=root_hash)
        
        contract = self._get_contract("notary")
        
        # Convert run_id to bytes32
        run_id_bytes32 = Web3.keccak(text=run_id)
        root_hash_bytes32 = Web3.to_bytes(hexstr=root_hash)
        
        # Build transaction
        tx = self._build_transaction(
            contract.functions.publish(run_id_bytes32, root_hash_bytes32),
            gas_limit=100000
        )
        
        # Send transaction
        result = self._send_transaction(tx)
        
        log.info("subnet.notary.published", 
                run_id=run_id, 
                tx_hash=result["transactionHash"],
                block_number=result["blockNumber"])
        
        return result
    
    def get_notary(self, run_id: str) -> Optional[str]:
        """Get notarized root hash for a run"""
        contract = self._get_contract("notary")
        run_id_bytes32 = Web3.keccak(text=run_id)
        
        root_hash = contract.functions.get(run_id_bytes32).call()
        
        if root_hash == b'\x00' * 32:
            return None
        
        return root_hash.hex()
    
    def commit_blob(
        self, 
        commit_id: str, 
        label_hash: bytes, 
        ciphertext: bytes, 
        data_hash: bytes
    ) -> dict[str, Any]:
        """Commit encrypted data to CommitStore"""
        log.info("subnet.commit.store", 
                commit_id=commit_id, 
                label_hash=label_hash.hex(),
                data_hash=data_hash.hex(),
                ciphertext_size=len(ciphertext))
        
        contract = self._get_contract("commit")
        
        # Convert ID to bytes32
        id_bytes32 = Web3.keccak(text=commit_id)
        
        # Build transaction
        tx = self._build_transaction(
            contract.functions.commit(id_bytes32, label_hash, ciphertext, data_hash),
            gas_limit=min(500000, 21000 + len(ciphertext) * 16)  # Dynamic gas based on data size
        )
        
        # Send transaction
        result = self._send_transaction(tx)
        
        log.info("subnet.commit.stored",
                commit_id=commit_id,
                tx_hash=result["transactionHash"],
                block_number=result["blockNumber"])
        
        return result
    
    def get_commit(self, commit_id: str) -> Optional[bytes]:
        """Get encrypted data from CommitStore"""
        contract = self._get_contract("commit")
        id_bytes32 = Web3.keccak(text=commit_id)
        
        ciphertext = contract.functions.get(id_bytes32).call()
        
        if len(ciphertext) == 0:
            return None
        
        return ciphertext
    
    def register_release(
        self, 
        version: str, 
        source_hash: str, 
        artifact_hash: str
    ) -> dict[str, Any]:
        """Register a project release in ProjectRegistry"""
        log.info("subnet.registry.register", 
                version=version,
                source_hash=source_hash,
                artifact_hash=artifact_hash)
        
        contract = self._get_contract("project_registry")
        
        # Convert to bytes32
        version_id = Web3.keccak(text=version)
        source_hash_bytes32 = Web3.to_bytes(hexstr=source_hash) if source_hash.startswith('0x') else Web3.keccak(text=source_hash)
        artifact_hash_bytes32 = Web3.to_bytes(hexstr=artifact_hash) if artifact_hash.startswith('0x') else Web3.keccak(text=artifact_hash)
        
        # Build transaction
        tx = self._build_transaction(
            contract.functions.register(version_id, source_hash_bytes32, artifact_hash_bytes32, version),
            gas_limit=150000
        )
        
        # Send transaction
        result = self._send_transaction(tx)
        
        log.info("subnet.registry.registered",
                version=version,
                tx_hash=result["transactionHash"],
                block_number=result["blockNumber"])
        
        return result


# Global instance
_subnet_client: Optional[SubnetClient] = None


def get_subnet_client() -> SubnetClient:
    """Get global subnet client instance"""
    global _subnet_client
    if _subnet_client is None:
        _subnet_client = SubnetClient()
    return _subnet_client
