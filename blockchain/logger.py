"""
Blockchain Logger
Logs critical events to blockchain (or simulated ledger)
"""

from typing import List, Dict
from datetime import datetime
import logging
import json

from models.schemas import (
    BlockchainLog,
    ControlDecision,
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
    - If BLOCKCHAIN_ENABLED=True: Use Ethereum testnet (Sepolia)
    
    Events logged:
    - Control decisions (when fan turns ON/OFF)
    - Fault detections
    - Self-healing actions
    """
    
    def __init__(self):
        """Initialize blockchain logger."""
        self.enabled = settings.BLOCKCHAIN_ENABLED
        
        # In-memory simulated ledger
        self.ledger: List[BlockchainLog] = []
        
        if self.enabled:
            # TODO: Initialize Web3 connection to Ethereum testnet
            # from web3 import Web3
            # self.web3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
            # self.contract = self.web3.eth.contract(...)
            logger.info("Blockchain logger initialized with real blockchain")
        else:
            logger.info("Blockchain logger initialized with simulated ledger")
    
    async def log_decision(
        self,
        device_id: str,
        decision: ControlDecision
    ) -> BlockchainLog:
        """
        Log control decision to blockchain.
        
        Args:
            device_id: ESP32 device identifier
            decision: Control decision to log
        
        Returns:
            BlockchainLog entry
        """
        log_entry = BlockchainLog(
            event_type="decision",
            timestamp=datetime.utcnow(),
            device_id=device_id,
            data={
                "fan_on": decision.fan_on,
                "fan_intensity": decision.fan_intensity,
                "reasoning": decision.reasoning,
                "override_reason": decision.override_reason
            }
        )
        
        if self.enabled:
            # TODO: Write to real blockchain
            # tx_hash = await self._write_to_blockchain(log_entry)
            # log_entry.hash = tx_hash
            pass
        else:
            # Simulated ledger
            log_entry.hash = self._generate_mock_hash(log_entry)
        
        self.ledger.append(log_entry)
        logger.info(f"Logged decision to blockchain: {log_entry.hash}")
        
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
        
        if self.enabled:
            # TODO: Write to real blockchain
            pass
        else:
            log_entry.hash = self._generate_mock_hash(log_entry)
        
        self.ledger.append(log_entry)
        logger.warning(f"Logged fault to blockchain: {log_entry.hash}")
        
        return log_entry
    
    def get_recent_logs(self, limit: int = 20) -> List[BlockchainLog]:
        """
        Get recent blockchain logs.
        
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
    
    def _generate_mock_hash(self, log_entry: BlockchainLog) -> str:
        """
        Generate mock transaction hash for simulated ledger.
        
        Args:
            log_entry: Log entry to hash
        
        Returns:
            Mock transaction hash
        """
        import hashlib
        
        data_str = json.dumps({
            "event_type": log_entry.event_type,
            "timestamp": log_entry.timestamp.isoformat(),
            "device_id": log_entry.device_id,
            "data": log_entry.data
        }, sort_keys=True)
        
        hash_obj = hashlib.sha256(data_str.encode())
        return f"0x{hash_obj.hexdigest()[:40]}"
    
    async def _write_to_blockchain(self, log_entry: BlockchainLog) -> str:
        """
        Write log entry to real blockchain.
        
        This is a placeholder for actual blockchain integration.
        
        Args:
            log_entry: Log entry to write
        
        Returns:
            Transaction hash
        """
        # TODO: Implement real blockchain writing
        # Example with Web3.py:
        # tx = self.contract.functions.logEvent(
        #     log_entry.event_type,
        #     log_entry.device_id,
        #     json.dumps(log_entry.data)
        # ).buildTransaction({
        #     'from': self.web3.eth.default_account,
        #     'nonce': self.web3.eth.get_transaction_count(self.web3.eth.default_account),
        # })
        # signed_tx = self.web3.eth.account.sign_transaction(tx, settings.BLOCKCHAIN_PRIVATE_KEY)
        # tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        # return tx_hash.hex()
        
        raise NotImplementedError("Real blockchain integration not yet implemented")
