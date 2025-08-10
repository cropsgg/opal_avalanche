// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Notary
 * @dev Immutable notarization contract for OPAL research runs
 * @notice No owner, no upgradeability - bytecode is final
 */
contract Notary {
    event Notarized(bytes32 indexed runId, bytes32 rootHash, address indexed submitter, uint256 ts);
    
    mapping(bytes32 => bytes32) public roots;
    
    /**
     * @dev Publish a Merkle root for a research run
     * @param runId Unique identifier for the research run
     * @param rootHash Merkle root of the research evidence
     */
    function publish(bytes32 runId, bytes32 rootHash) external {
        require(roots[runId] == bytes32(0), "set");
        roots[runId] = rootHash;
        emit Notarized(runId, rootHash, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Get the stored root hash for a run
     * @param runId The run identifier
     * @return The stored Merkle root
     */
    function get(bytes32 runId) external view returns (bytes32) {
        return roots[runId];
    }
    
    /**
     * @dev Check if a run has been notarized
     * @param runId The run identifier
     * @return True if the run has a stored root
     */
    function isNotarized(bytes32 runId) external view returns (bool) {
        return roots[runId] != bytes32(0);
    }
}
