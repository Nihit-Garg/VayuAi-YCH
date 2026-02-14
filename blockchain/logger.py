"""
Blockchain Logger
Logs critical events to Ethereum blockchain (Sepolia testnet) or simulated ledger
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging
import json
import asyncio

from models.schemas import (
    BlockchainLog,
    ControlDecision,
    SmokePrediction,
    FaultDetectionResult,
    SelfHealingAction
)
from config.settings import settings

logger = logging.getLogger(__name__)


class BlockchainLogger:
    """
    Logs critical events to blockchain or simulated ledger.
    
    For hackathon:
    - If BLOCKCHAIN_ENABLED=False: Use in-memory simulated ledger
    - If BLOCKCHAIN_ENABLED=True: Use Ethereum Sepolia testnet
    
    Events logged:
    - Control decisions (when fan turns ON/OFF)
    - Fault detections
    - Self-healing actions
    """
    
    def __init__(self):
        """Initialize blockchain logger."""
        self.enabled = settings.BLOCKCHAIN_ENABLED
        
        # In-memory simulated ledger (always maintained as backup)
        self.ledger: List[BlockchainLog] = []
        
        # Web3 connection
        self.web3 = None
        self.contract = None
        self.account = None
        
        if self.enabled:
            try:
                self._initialize_web3()
                logger.info(f"✅ Blockchain logger initialized with Sepolia testnet")
                logger.info(f"   Contract: {settings.BLOCKCHAIN_CONTRACT_ADDRESS}")
                logger.info(f"   Account: {self.account.address if self.account else 'Not configured'}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize blockchain: {str(e)}")
                logger.warning("   Falling back to simulated ledger")
                self.enabled = False
        else:
            logger.info("Blockchain logger initialized with simulated ledger")
    
    def _initialize_web3(self):
        """Initialize Web3 connection to Ethereum."""
        from web3 import Web3
        from web3.middleware import geth_poa_middleware
        from blockchain.contract_abi import CONTRACT_ABI
        
        # Connect to Sepolia via RPC
        self.web3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
        
        # Add PoA middleware for testnets
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check connection
        if not self.web3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum RPC")
        
        logger.info(f"   Connected to Ethereum (Chain ID: {self.web3.eth.chain_id})")
        
        # Load account from private key
        if settings.BLOCKCHAIN_PRIVATE_KEY:
            self.account = self.web3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
            self.web3.eth.default_account = self.account.address
            
            # Check balance
            balance = self.web3.eth.get_balance(self.account.address)
            balance_eth = self.web3.from_wei(balance, 'ether')
            logger.info(f"   Account balance: {balance_eth:.4f} ETH")
            
            if balance == 0:
                logger.warning("   ⚠️  Account has 0 ETH! Get testnet ETH from faucet")
        else:
            logger.warning("   No private key configured - read-only mode")
        
        # Load smart contract
        if settings.BLOCKCHAIN_CONTRACT_ADDRESS:
            self.contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(settings.BLOCKCHAIN_CONTRACT_ADDRESS),
                abi=CONTRACT_ABI
            )
            logger.info(f"   Contract loaded successfully")
        else:
            logger.warning("   No contract address configured")
    
    async def log_decision(
        self,
        device_id: str,
        decision: ControlDecision,
        prediction: Optional[SmokePrediction] = None
    ) -> BlockchainLog:
        """
        Log control decision to blockchain.
        
        Args:
            device_id: ESP32 device identifier
            decision: Control decision to log
            prediction: Optional prediction that led to decision
        
        Returns:
            BlockchainLog entry
        """
        log_data = {
            "fan_on": decision.fan_on,
            "fan_intensity": decision.fan_intensity,
            "reasoning": decision.reasoning,
            "override_reason": decision.override_reason
        }
        
        if prediction:
            log_data["predicted_smoke_peak"] = prediction.estimated_peak_value
            log_data["prediction_confidence"] = prediction.confidence

        log_entry = BlockchainLog(
            event_type="decision",
            timestamp=datetime.utcnow(),
            device_id=device_id,
            data=log_data
        )

        
        if self.enabled and self.contract and self.account:
            try:
                # Write to real blockchain
                tx_hash = await self._write_decision_to_blockchain(device_id, log_entry.data)
                log_entry.hash = tx_hash
                logger.info(f"✅ Decision logged to blockchain: {tx_hash}")
            except Exception as e:
                logger.error(f"❌ Failed to write to blockchain: {str(e)}")
                logger.warning("   Using simulated hash instead")
                log_entry.hash = self._generate_mock_hash(log_entry)
        else:
            # Simulated ledger
            log_entry.hash = self._generate_mock_hash(log_entry)
            logger.info(f"📝 Decision logged to simulated ledger: {log_entry.hash}")
        
        self.ledger.append(log_entry)
        return log_entry
    
    async def log_fault(
        self,
        device_id: str,
        fault: FaultDetectionResult,
        healing: SelfHealingAction
    ) -> BlockchainLog:
        """
        Log fault and healing action to blockchain.
        
        Args:
            device_id: ESP32 device identifier
            fault: Detected fault
            healing: Healing action taken
        
        Returns:
            BlockchainLog entry
        """
        log_entry = BlockchainLog(
            event_type="fault",
            timestamp=datetime.utcnow(),
            device_id=device_id,
            data={
                "fault_type": fault.fault_type.value,
                "affected_sensor": fault.affected_sensor,
                "severity": fault.severity,
                "details": fault.details,
                "healing_action": healing.action_taken,
                "ignored_sensors": healing.ignored_sensors
            }
        )
        
        if self.enabled and self.contract and self.account:
            try:
                tx_hash = await self._write_fault_to_blockchain(device_id, log_entry.data)
                log_entry.hash = tx_hash
                logger.warning(f"⚠️  Fault logged to blockchain: {tx_hash}")
            except Exception as e:
                logger.error(f"❌ Failed to write fault to blockchain: {str(e)}")
                log_entry.hash = self._generate_mock_hash(log_entry)
        else:
            log_entry.hash = self._generate_mock_hash(log_entry)
            logger.warning(f"⚠️  Fault logged to simulated ledger: {log_entry.hash}")
        
        self.ledger.append(log_entry)
        return log_entry
    
    def get_recent_logs(self, limit: int = 20) -> List[BlockchainLog]:
        """
        Get recent blockchain logs from local cache.
        
        Args:
            limit: Number of recent logs to return
        
        Returns:
            List of recent blockchain logs
        """
        return self.ledger[-limit:] if len(self.ledger) > limit else self.ledger
    
    def get_logs_by_device(self, device_id: str, limit: int = 20) -> List[BlockchainLog]:
        """
        Get blockchain logs for a specific device.
        
        Args:
            device_id: ESP32 device identifier
            limit: Number of logs to return
        
        Returns:
            List of blockchain logs for the device
        """
        device_logs = [log for log in self.ledger if log.device_id == device_id]
        return device_logs[-limit:] if len(device_logs) > limit else device_logs
    
    async def get_blockchain_log_count(self) -> Optional[int]:
        """
        Get total log count from blockchain smart contract.
        
        Returns:
            Total number of logs on blockchain, or None if not available
        """
        if self.enabled and self.contract:
            try:
                count = self.contract.functions.getLogCount().call()
                return count
            except Exception as e:
                logger.error(f"Failed to get log count from blockchain: {str(e)}")
                return None
        return len(self.ledger)
    
    def _generate_mock_hash(self, log_entry: BlockchainLog) -> str:
        """
        Generate mock transaction hash for simulated ledger.
        
        Args:
            log_entry: Log entry to hash
        
        Returns:
            Mock transaction hash (looks like real Ethereum tx hash)
        """
        import hashlib
        
        data_str = json.dumps({
            "event_type": log_entry.event_type,
            "timestamp": log_entry.timestamp.isoformat(),
            "device_id": log_entry.device_id,
            "data": log_entry.data
        }, sort_keys=True)
        
        hash_obj = hashlib.sha256(data_str.encode())
        return f"0x{hash_obj.hexdigest()}"
    
    async def _write_decision_to_blockchain(self, device_id: str, data: Dict) -> str:
        """
        Write decision log to blockchain smart contract.
        
        Args:
            device_id: ESP32 device identifier
            data: Decision data to log
        
        Returns:
            Transaction hash
        """
        # Prepare data as JSON string
        data_json = json.dumps(data)
        
        # Build transaction
        tx = self.contract.functions.logDecision(
            device_id,
            data_json
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'gas': 200000,  # Estimate gas
            'gasPrice': self.web3.eth.gas_price,
        })
        
        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
        
        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for confirmation (optional - comment out for faster response)
        # receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        return tx_hash.hex()
    
    async def _write_fault_to_blockchain(self, device_id: str, data: Dict) -> str:
        """
        Write fault log to blockchain smart contract.
        
        Args:
            device_id: ESP32 device identifier
            data: Fault data to log
        
        Returns:
            Transaction hash
        """
        data_json = json.dumps(data)
        
        tx = self.contract.functions.logFault(
            device_id,
            data_json
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'gas': 200000,
            'gasPrice': self.web3.eth.gas_price,
        })
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash.hex()
    
    def get_etherscan_url(self, tx_hash: str) -> str:
        """
        Get Etherscan URL for a transaction hash.
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            Etherscan URL
        """
        if settings.BLOCKCHAIN_RPC_URL and "sepolia" in settings.BLOCKCHAIN_RPC_URL.lower():
            return f"https://sepolia.etherscan.io/tx/{tx_hash}"
        else:
            return f"https://etherscan.io/tx/{tx_hash}"
