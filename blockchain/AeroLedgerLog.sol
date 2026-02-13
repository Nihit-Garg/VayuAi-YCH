// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AeroLedgerLog
 * @dev Smart contract for logging AeroLedger events to Ethereum blockchain
 * 
 * This contract stores immutable logs of:
 * - AI control decisions (fan ON/OFF, intensity)
 * - Fault detection events
 * - Self-healing actions
 * 
 * All events are permanently recorded and verifiable on Etherscan
 */
contract AeroLedgerLog {
    
    // Struct to store log entries
    struct LogEntry {
        string deviceId;
        string eventType;      // "decision", "fault", or "healing"
        uint256 timestamp;
        string data;           // JSON string with event details
        address logger;        // Address that logged the event
    }
    
    // Array of all log entries
    LogEntry[] public logs;
    
    // Mapping from device ID to their log indices
    mapping(string => uint256[]) public deviceLogs;
    
    // Events for off-chain monitoring
    event DecisionLogged(
        string indexed deviceId,
        uint256 indexed logIndex,
        uint256 timestamp,
        string data
    );
    
    event FaultLogged(
        string indexed deviceId,
        uint256 indexed logIndex,
        uint256 timestamp,
        string data
    );
    
    event HealingLogged(
        string indexed deviceId,
        uint256 indexed logIndex,
        uint256 timestamp,
        string data
    );
    
    /**
     * @dev Log a control decision to blockchain
     * @param deviceId ESP32 device identifier
     * @param data JSON string containing decision details
     */
    function logDecision(string memory deviceId, string memory data) public {
        uint256 logIndex = logs.length;
        
        logs.push(LogEntry({
            deviceId: deviceId,
            eventType: "decision",
            timestamp: block.timestamp,
            data: data,
            logger: msg.sender
        }));
        
        deviceLogs[deviceId].push(logIndex);
        
        emit DecisionLogged(deviceId, logIndex, block.timestamp, data);
    }
    
    /**
     * @dev Log a fault detection event to blockchain
     * @param deviceId ESP32 device identifier
     * @param data JSON string containing fault details
     */
    function logFault(string memory deviceId, string memory data) public {
        uint256 logIndex = logs.length;
        
        logs.push(LogEntry({
            deviceId: deviceId,
            eventType: "fault",
            timestamp: block.timestamp,
            data: data,
            logger: msg.sender
        }));
        
        deviceLogs[deviceId].push(logIndex);
        
        emit FaultLogged(deviceId, logIndex, block.timestamp, data);
    }
    
    /**
     * @dev Log a self-healing action to blockchain
     * @param deviceId ESP32 device identifier
     * @param data JSON string containing healing details
     */
    function logHealing(string memory deviceId, string memory data) public {
        uint256 logIndex = logs.length;
        
        logs.push(LogEntry({
            deviceId: deviceId,
            eventType: "healing",
            timestamp: block.timestamp,
            data: data,
            logger: msg.sender
        }));
        
        deviceLogs[deviceId].push(logIndex);
        
        emit HealingLogged(deviceId, logIndex, block.timestamp, data);
    }
    
    /**
     * @dev Get total number of logs
     * @return Total count of all logs
     */
    function getLogCount() public view returns (uint256) {
        return logs.length;
    }
    
    /**
     * @dev Get a specific log entry
     * @param index Index of the log entry
     * @return LogEntry struct
     */
    function getLog(uint256 index) public view returns (LogEntry memory) {
        require(index < logs.length, "Log index out of bounds");
        return logs[index];
    }
    
    /**
     * @dev Get all log indices for a specific device
     * @param deviceId ESP32 device identifier
     * @return Array of log indices
     */
    function getDeviceLogs(string memory deviceId) public view returns (uint256[] memory) {
        return deviceLogs[deviceId];
    }
    
    /**
     * @dev Get recent logs (last N entries)
     * @param count Number of recent logs to retrieve
     * @return Array of LogEntry structs
     */
    function getRecentLogs(uint256 count) public view returns (LogEntry[] memory) {
        uint256 totalLogs = logs.length;
        uint256 returnCount = count > totalLogs ? totalLogs : count;
        
        LogEntry[] memory recentLogs = new LogEntry[](returnCount);
        
        for (uint256 i = 0; i < returnCount; i++) {
            recentLogs[i] = logs[totalLogs - returnCount + i];
        }
        
        return recentLogs;
    }
}
