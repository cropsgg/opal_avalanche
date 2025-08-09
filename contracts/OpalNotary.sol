// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract OpalNotary {
    event Notarized(bytes32 indexed runId, bytes32 rootHash, address indexed submitter, uint256 timestamp);
    mapping(bytes32 => bytes32) public roots;      // runId => root
    mapping(bytes32 => uint256) public times;      // runId => ts
    mapping(bytes32 => address) public submitters; // runId => who

    function publish(bytes32 runId, bytes32 rootHash) external {
        require(roots[runId] == bytes32(0), "Already set");
        roots[runId] = rootHash;
        times[runId] = block.timestamp;
        submitters[runId] = msg.sender;
        emit Notarized(runId, rootHash, msg.sender, block.timestamp);
    }

    function get(bytes32 runId) external view returns (bytes32, uint256, address) {
        return (roots[runId], times[runId], submitters[runId]);
    }
}


