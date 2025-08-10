// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProjectRegistry
 * @dev Lock code baseline releases for transparency
 * @notice Immutable registry of project versions and their hashes
 */
contract ProjectRegistry {
    event Release(
        bytes32 indexed versionId, 
        bytes32 sourceHash, 
        bytes32 artifactHash, 
        uint256 ts,
        string version
    );
    
    struct ReleaseInfo {
        bytes32 sourceHash;
        bytes32 artifactHash;
        uint256 timestamp;
        string version;
        bool exists;
    }
    
    mapping(bytes32 => ReleaseInfo) public releases;
    mapping(bytes32 => bool) public released;
    
    /**
     * @dev Register a new project release
     * @param versionId Unique identifier for this version (e.g., keccak256(version))
     * @param sourceHash Hash of source code (e.g., git commit hash)
     * @param artifactHash Hash of built artifacts (e.g., zip of backend)
     * @param version Human-readable version string
     */
    function register(
        bytes32 versionId, 
        bytes32 sourceHash, 
        bytes32 artifactHash,
        string calldata version
    ) external {
        require(!released[versionId], "done");
        
        released[versionId] = true;
        releases[versionId] = ReleaseInfo({
            sourceHash: sourceHash,
            artifactHash: artifactHash,
            timestamp: block.timestamp,
            version: version,
            exists: true
        });
        
        emit Release(versionId, sourceHash, artifactHash, block.timestamp, version);
    }
    
    /**
     * @dev Get release information
     * @param versionId The version identifier
     * @return info Complete release information
     */
    function getRelease(bytes32 versionId) external view returns (ReleaseInfo memory info) {
        return releases[versionId];
    }
    
    /**
     * @dev Check if a version is registered
     * @param versionId The version identifier
     * @return True if this version is registered
     */
    function isReleased(bytes32 versionId) external view returns (bool) {
        return released[versionId];
    }
    
    /**
     * @dev Verify source and artifact hashes for a version
     * @param versionId The version identifier
     * @param expectedSourceHash Expected source hash
     * @param expectedArtifactHash Expected artifact hash
     * @return True if both hashes match the registered values
     */
    function verify(
        bytes32 versionId,
        bytes32 expectedSourceHash,
        bytes32 expectedArtifactHash
    ) external view returns (bool) {
        ReleaseInfo memory info = releases[versionId];
        return info.exists && 
               info.sourceHash == expectedSourceHash && 
               info.artifactHash == expectedArtifactHash;
    }
}
