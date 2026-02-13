"""
Contract ABI for AeroLedgerLog smart contract
This is the interface definition for interacting with the deployed contract
"""

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "deviceId", "type": "string"},
            {"internalType": "string", "name": "data", "type": "string"}
        ],
        "name": "logDecision",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "deviceId", "type": "string"},
            {"internalType": "string", "name": "data", "type": "string"}
        ],
        "name": "logFault",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "deviceId", "type": "string"},
            {"internalType": "string", "name": "data", "type": "string"}
        ],
        "name": "logHealing",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getLogCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
        "name": "getLog",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "deviceId", "type": "string"},
                    {"internalType": "string", "name": "eventType", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "data", "type": "string"},
                    {"internalType": "address", "name": "logger", "type": "address"}
                ],
                "internalType": "struct AeroLedgerLog.LogEntry",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "deviceId", "type": "string"}],
        "name": "getDeviceLogs",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "count", "type": "uint256"}],
        "name": "getRecentLogs",
        "outputs": [
            {
                "components": [
                    {"internalType": "string", "name": "deviceId", "type": "string"},
                    {"internalType": "string", "name": "eventType", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "data", "type": "string"},
                    {"internalType": "address", "name": "logger", "type": "address"}
                ],
                "internalType": "struct AeroLedgerLog.LogEntry[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "deviceId", "type": "string"},
            {"indexed": True, "internalType": "uint256", "name": "logIndex", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "data", "type": "string"}
        ],
        "name": "DecisionLogged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "deviceId", "type": "string"},
            {"indexed": True, "internalType": "uint256", "name": "logIndex", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "data", "type": "string"}
        ],
        "name": "FaultLogged",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "string", "name": "deviceId", "type": "string"},
            {"indexed": True, "internalType": "uint256", "name": "logIndex", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "data", "type": "string"}
        ],
        "name": "HealingLogged",
        "type": "event"
    }
]
