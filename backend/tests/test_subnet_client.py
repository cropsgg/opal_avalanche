"""
Unit tests for subnet client
Tests Web3 interactions, transaction building, and error handling
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from web3 import Web3

from app.subnet.client import SubnetClient, get_subnet_client


class TestSubnetClient:
    """Test subnet client functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock settings
        self.mock_settings = Mock()
        self.mock_settings.SUBNET_RPC = "http://test-subnet:8545"
        self.mock_settings.SUBNET_CHAIN_ID = 43210
        self.mock_settings.SUBNET_SENDER_PK = "0x" + "a" * 64
        self.mock_settings.SUBNET_NOTARY_ADDR = "0x" + "1" * 40
        self.mock_settings.SUBNET_COMMIT_ADDR = "0x" + "2" * 40
        self.mock_settings.SUBNET_REGISTRY_ADDR = "0x" + "3" * 40
        
        with patch('app.subnet.client.get_settings', return_value=self.mock_settings):
            self.client = SubnetClient()
    
    def test_initialization(self):
        """Test client initialization"""
        assert self.client._w3 is None
        assert self.client._contracts == {}
        assert self.client._account is None
        assert self.client._nonce_cache is None
    
    @patch('app.subnet.client.Web3')
    def test_get_web3_connection(self, mock_web3_class):
        """Test Web3 connection setup"""
        # Mock Web3 instance
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.chain_id = 43210
        mock_web3_class.return_value = mock_w3
        
        # Get Web3 instance
        w3 = self.client._get_web3()
        
        assert w3 is mock_w3
        assert self.client._w3 is mock_w3
        mock_web3_class.assert_called_once()
        mock_w3.is_connected.assert_called_once()
    
    @patch('app.subnet.client.Web3')
    def test_get_web3_connection_failure(self, mock_web3_class):
        """Test Web3 connection failure"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = False
        mock_web3_class.return_value = mock_w3
        
        with pytest.raises(RuntimeError, match="Cannot connect to subnet RPC"):
            self.client._get_web3()
    
    @patch('app.subnet.client.Web3')
    def test_get_web3_wrong_chain_id(self, mock_web3_class):
        """Test wrong chain ID detection"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.chain_id = 99999  # Wrong chain ID
        mock_web3_class.return_value = mock_w3
        
        with pytest.raises(RuntimeError, match="Chain ID mismatch"):
            self.client._get_web3()
    
    def test_get_account(self):
        """Test account loading from private key"""
        with patch('app.subnet.client.Account') as mock_account:
            mock_acc = Mock()
            mock_acc.address = "0x742d35Cc6640C966f9f9c78c7D7bf88F9c900DAE"
            mock_account.from_key.return_value = mock_acc
            
            account = self.client._get_account()
            
            assert account is mock_acc
            assert self.client._account is mock_acc
            mock_account.from_key.assert_called_once_with(self.mock_settings.SUBNET_SENDER_PK)
    
    def test_get_account_no_private_key(self):
        """Test error when private key not configured"""
        self.mock_settings.SUBNET_SENDER_PK = None
        
        with pytest.raises(RuntimeError, match="SUBNET_SENDER_PK not configured"):
            self.client._get_account()
    
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_load_contract_abi(self, mock_exists, mock_open):
        """Test contract ABI loading"""
        mock_exists.return_value = True
        mock_abi = [{"type": "function", "name": "test"}]
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_abi)
        
        abi = self.client._load_contract_abi("notary")
        
        assert abi == mock_abi
        mock_open.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_load_contract_abi_not_found(self, mock_exists):
        """Test error when ABI file not found"""
        mock_exists.return_value = False
        
        with pytest.raises(RuntimeError, match="ABI file not found"):
            self.client._load_contract_abi("nonexistent")
    
    def test_get_nonce_caching(self):
        """Test nonce caching mechanism"""
        with patch.object(self.client, '_get_web3') as mock_get_w3:
            with patch.object(self.client, '_get_account') as mock_get_acc:
                mock_w3 = Mock()
                mock_w3.eth.get_transaction_count.return_value = 42
                mock_get_w3.return_value = mock_w3
                
                mock_account = Mock()
                mock_account.address = "0x123"
                mock_get_acc.return_value = mock_account
                
                # First call should fetch from network
                nonce1 = self.client._get_nonce()
                assert nonce1 == 42
                assert self.client._nonce_cache == 42
                
                # Second call should use cache
                nonce2 = self.client._get_nonce()
                assert nonce2 == 42
                
                # Should only call RPC once
                mock_w3.eth.get_transaction_count.assert_called_once()
    
    def test_increment_nonce(self):
        """Test nonce increment after successful transaction"""
        self.client._nonce_cache = 10
        
        self.client._increment_nonce()
        
        assert self.client._nonce_cache == 11
    
    def test_increment_nonce_no_cache(self):
        """Test nonce increment when no cache exists"""
        self.client._nonce_cache = None
        
        self.client._increment_nonce()  # Should not raise error
        
        assert self.client._nonce_cache is None
    
    @patch.object(SubnetClient, '_get_web3')
    @patch.object(SubnetClient, '_get_account')
    @patch.object(SubnetClient, '_get_nonce')
    def test_build_transaction(self, mock_get_nonce, mock_get_account, mock_get_w3):
        """Test transaction building"""
        # Setup mocks
        mock_w3 = Mock()
        mock_block = {'baseFeePerGas': 1000000000}  # 1 gwei
        mock_w3.eth.get_block.return_value = mock_block
        mock_get_w3.return_value = mock_w3
        
        mock_account = Mock()
        mock_account.address = "0x123"
        mock_get_account.return_value = mock_account
        
        mock_get_nonce.return_value = 5
        
        # Mock contract function
        mock_function = Mock()
        mock_function.build_transaction.return_value = {
            "to": "0x456",
            "data": "0xdeadbeef"
        }
        
        # Build transaction
        tx = self.client._build_transaction(mock_function, gas_limit=100000)
        
        # Verify transaction structure
        expected_max_fee = int(1000000000 * 1.5)  # 1.5x base fee
        expected_priority_fee = min(2000000, expected_max_fee // 10)
        
        mock_function.build_transaction.assert_called_once_with({
            "from": "0x123",
            "nonce": 5,
            "gas": 100000,
            "maxFeePerGas": expected_max_fee,
            "maxPriorityFeePerGas": expected_priority_fee,
        })
    
    @patch.object(SubnetClient, '_get_web3')
    @patch.object(SubnetClient, '_get_account')
    @patch.object(SubnetClient, '_increment_nonce')
    def test_send_transaction_success(self, mock_increment, mock_get_account, mock_get_w3):
        """Test successful transaction sending"""
        # Setup mocks
        mock_w3 = Mock()
        mock_get_w3.return_value = mock_w3
        
        mock_account = Mock()
        mock_signed_tx = Mock()
        mock_signed_tx.rawTransaction = b"signed_tx_bytes"
        mock_account.sign_transaction.return_value = mock_signed_tx
        mock_get_account.return_value = mock_account
        
        # Mock transaction receipt
        mock_receipt = Mock()
        mock_receipt.status = 1
        mock_receipt.transactionHash.hex.return_value = "0xabcd1234"
        mock_receipt.blockNumber = 12345
        mock_receipt.gasUsed = 85000
        
        mock_w3.eth.send_raw_transaction.return_value = b"tx_hash"
        mock_w3.eth.wait_for_transaction_receipt.return_value = mock_receipt
        
        # Send transaction
        tx = {"from": "0x123", "to": "0x456", "data": "0x"}
        result = self.client._send_transaction(tx)
        
        # Verify result
        assert result["transactionHash"] == "0xabcd1234"
        assert result["blockNumber"] == 12345
        assert result["gasUsed"] == 85000
        assert result["status"] == "success"
        
        # Verify nonce was incremented
        mock_increment.assert_called_once()
    
    @patch.object(SubnetClient, '_get_web3')
    @patch.object(SubnetClient, '_get_account')
    def test_send_transaction_failure(self, mock_get_account, mock_get_w3):
        """Test transaction failure handling"""
        mock_w3 = Mock()
        mock_get_w3.return_value = mock_w3
        
        mock_account = Mock()
        mock_account.sign_transaction.side_effect = Exception("Signing failed")
        mock_get_account.return_value = mock_account
        
        tx = {"from": "0x123", "to": "0x456", "data": "0x"}
        
        with pytest.raises(RuntimeError, match="Transaction failed after all retries"):
            self.client._send_transaction(tx, retry_count=2)
    
    @patch.object(SubnetClient, '_get_contract')
    @patch.object(SubnetClient, '_build_transaction')
    @patch.object(SubnetClient, '_send_transaction')
    def test_publish_notary(self, mock_send_tx, mock_build_tx, mock_get_contract):
        """Test notary publishing"""
        # Setup mocks
        mock_contract = Mock()
        mock_function = Mock()
        mock_contract.functions.publish.return_value = mock_function
        mock_get_contract.return_value = mock_contract
        
        mock_tx = {"to": "0x123", "data": "0xdeadbeef"}
        mock_build_tx.return_value = mock_tx
        
        mock_result = {
            "transactionHash": "0xabcd1234",
            "blockNumber": 12345,
            "status": "success"
        }
        mock_send_tx.return_value = mock_result
        
        # Publish notary
        result = self.client.publish_notary("test-run-123", "0x" + "f" * 64)
        
        # Verify calls
        mock_get_contract.assert_called_once_with("notary")
        mock_build_tx.assert_called_once_with(mock_function, gas_limit=100000)
        mock_send_tx.assert_called_once_with(mock_tx)
        
        assert result == mock_result
    
    @patch.object(SubnetClient, '_get_contract')
    def test_get_notary(self, mock_get_contract):
        """Test notary reading"""
        # Setup mock
        mock_contract = Mock()
        mock_root = b'\xaa' * 32  # Non-zero root
        mock_contract.functions.get.return_value.call.return_value = mock_root
        mock_get_contract.return_value = mock_contract
        
        # Get notary
        result = self.client.get_notary("test-run-123")
        
        assert result == mock_root.hex()
    
    @patch.object(SubnetClient, '_get_contract')
    def test_get_notary_not_found(self, mock_get_contract):
        """Test notary reading when not found"""
        # Setup mock - zero hash means not found
        mock_contract = Mock()
        mock_contract.functions.get.return_value.call.return_value = b'\x00' * 32
        mock_get_contract.return_value = mock_contract
        
        # Get notary
        result = self.client.get_notary("nonexistent-run")
        
        assert result is None
    
    @patch.object(SubnetClient, '_get_contract')
    @patch.object(SubnetClient, '_build_transaction')
    @patch.object(SubnetClient, '_send_transaction')
    def test_commit_blob(self, mock_send_tx, mock_build_tx, mock_get_contract):
        """Test blob committing"""
        # Setup mocks
        mock_contract = Mock()
        mock_function = Mock()
        mock_contract.functions.commit.return_value = mock_function
        mock_get_contract.return_value = mock_contract
        
        mock_tx = {"to": "0x123", "data": "0xdeadbeef"}
        mock_build_tx.return_value = mock_tx
        
        mock_result = {
            "transactionHash": "0xabcd1234",
            "blockNumber": 12345,
            "status": "success"
        }
        mock_send_tx.return_value = mock_result
        
        # Commit blob
        test_data = b"encrypted test data"
        label_hash = b'\xaa' * 32
        data_hash = b'\xbb' * 32
        
        result = self.client.commit_blob("test-commit", label_hash, test_data, data_hash)
        
        # Verify calls
        mock_get_contract.assert_called_once_with("commit")
        # Gas limit should be dynamic based on data size
        expected_gas = min(500000, 21000 + len(test_data) * 16)
        mock_build_tx.assert_called_once_with(mock_function, gas_limit=expected_gas)
        mock_send_tx.assert_called_once_with(mock_tx)
        
        assert result == mock_result


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_get_subnet_client_singleton(self):
        """Test that get_subnet_client returns same instance"""
        with patch('app.subnet.client.SubnetClient') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            client1 = get_subnet_client()
            client2 = get_subnet_client()
            
            assert client1 is client2
            mock_class.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_missing_rpc_config(self):
        """Test error when RPC not configured"""
        mock_settings = Mock()
        mock_settings.SUBNET_RPC = None
        
        with patch('app.subnet.client.get_settings', return_value=mock_settings):
            client = SubnetClient()
            
            with pytest.raises(RuntimeError, match="SUBNET_RPC not configured"):
                client._get_web3()
    
    def test_missing_contract_address(self):
        """Test error when contract address not configured"""
        mock_settings = Mock()
        mock_settings.SUBNET_RPC = "http://test:8545"
        mock_settings.SUBNET_NOTARY_ADDR = None
        
        with patch('app.subnet.client.get_settings', return_value=mock_settings):
            client = SubnetClient()
            
            with patch.object(client, '_get_web3'):
                with pytest.raises(RuntimeError, match="Contract address not configured"):
                    client._get_contract("notary")


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    @patch.object(SubnetClient, '_get_web3')
    @patch.object(SubnetClient, '_get_account')  
    @patch.object(SubnetClient, '_get_contract')
    @patch.object(SubnetClient, '_send_transaction')
    def test_full_notarization_flow(self, mock_send_tx, mock_get_contract, mock_get_account, mock_get_w3):
        """Test complete notarization workflow"""
        # Setup client
        mock_settings = Mock()
        mock_settings.SUBNET_RPC = "http://test-subnet:8545"
        mock_settings.SUBNET_CHAIN_ID = 43210
        mock_settings.SUBNET_SENDER_PK = "0x" + "a" * 64
        mock_settings.SUBNET_NOTARY_ADDR = "0x" + "1" * 40
        mock_settings.SUBNET_COMMIT_ADDR = "0x" + "2" * 40
        
        with patch('app.subnet.client.get_settings', return_value=mock_settings):
            client = SubnetClient()
        
        # Mock dependencies
        mock_w3 = Mock()
        mock_w3.eth.get_block.return_value = {'baseFeePerGas': 1000000000}
        mock_get_w3.return_value = mock_w3
        
        mock_account = Mock()
        mock_account.address = "0x742d35Cc6640C966f9f9c78c7D7bf88F9c900DAE"
        mock_get_account.return_value = mock_account
        
        # Mock notary contract
        mock_notary_contract = Mock()
        mock_notary_function = Mock()
        mock_notary_function.build_transaction.return_value = {"to": "0x1", "data": "0x"}
        mock_notary_contract.functions.publish.return_value = mock_notary_function
        
        # Mock commit contract  
        mock_commit_contract = Mock()
        mock_commit_function = Mock()
        mock_commit_function.build_transaction.return_value = {"to": "0x2", "data": "0x"}
        mock_commit_contract.functions.commit.return_value = mock_commit_function
        
        # Return different contracts based on name
        def get_contract_side_effect(name):
            if name == "notary":
                return mock_notary_contract
            elif name == "commit":
                return mock_commit_contract
            else:
                raise ValueError(f"Unknown contract: {name}")
        
        mock_get_contract.side_effect = get_contract_side_effect
        
        # Mock successful transactions
        mock_send_tx.side_effect = [
            {"transactionHash": "0xnotary123", "blockNumber": 100},
            {"transactionHash": "0xcommit456", "blockNumber": 101}
        ]
        
        # Execute full flow
        run_id = "test-run-789"
        merkle_root = "0x" + "f" * 64
        
        # 1. Publish notary
        notary_result = client.publish_notary(run_id, merkle_root)
        assert notary_result["transactionHash"] == "0xnotary123"
        
        # 2. Commit audit data
        audit_data = b"encrypted audit data"
        label_hash = b'\xaa' * 32
        data_hash = b'\xbb' * 32
        
        commit_result = client.commit_blob(run_id, label_hash, audit_data, data_hash)
        assert commit_result["transactionHash"] == "0xcommit456"
        
        # Verify both transactions were sent
        assert mock_send_tx.call_count == 2
