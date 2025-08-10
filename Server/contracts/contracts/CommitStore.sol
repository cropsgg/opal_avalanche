// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title CommitStore
 * @dev Opaque encrypted commit storage - type-agnostic
 * @notice Stores only ciphertext and hashes, no semantic information
 */
contract CommitStore {
    event Committed(bytes32 indexed id, bytes32 labelHash, bytes32 dataHash, uint256 ts);
    
    mapping(bytes32 => bytes) private blob; // ciphertext only
    mapping(bytes32 => bytes32) public labelHashes; // for verification
    mapping(bytes32 => bytes32) public dataHashes; // for integrity
    
    /**
     * @dev Commit encrypted data with opaque identifiers
     * @param id Unique identifier for this commit
     * @param labelHash keccak256(secretSalt || label) - hides semantic meaning
     * @param ciphertext Encrypted data - opaque bytes, no type info
     * @param dataHash SHA-256/keccak of plaintext before encryption
     */
    function commit(
        bytes32 id, 
        bytes32 labelHash, 
        bytes calldata ciphertext, 
        bytes32 dataHash
    ) external {
        require(blob[id].length == 0, "exists");
        
        blob[id] = ciphertext;
        labelHashes[id] = labelHash;
        dataHashes[id] = dataHash;
        
        emit Committed(id, labelHash, dataHash, block.timestamp);
    }
    
    /**
     * @dev Retrieve encrypted data
     * @param id The commit identifier
     * @return The stored ciphertext
     */
    function get(bytes32 id) external view returns (bytes memory) {
        return blob[id];
    }
    
    /**
     * @dev Check if a commit exists
     * @param id The commit identifier
     * @return True if data exists for this ID
     */
    function exists(bytes32 id) external view returns (bool) {
        return blob[id].length > 0;
    }
    
    /**
     * @dev Get commit metadata
     * @param id The commit identifier
     * @return labelHash The label hash
     * @return dataHash The data integrity hash
     */
    function getMetadata(bytes32 id) external view returns (bytes32 labelHash, bytes32 dataHash) {
        return (labelHashes[id], dataHashes[id]);
    }
}
