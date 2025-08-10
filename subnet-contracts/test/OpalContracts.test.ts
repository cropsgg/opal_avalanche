import { expect } from "chai";
import { ethers } from "hardhat";
import { Notary, CommitStore, ProjectRegistry } from "../typechain-types";

describe("OPAL Phase 2 Contracts", function () {
  let notary: Notary;
  let commitStore: CommitStore;
  let projectRegistry: ProjectRegistry;
  let owner: any;
  let addr1: any;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    // Deploy Notary
    const NotaryFactory = await ethers.getContractFactory("Notary");
    notary = await NotaryFactory.deploy();

    // Deploy CommitStore
    const CommitStoreFactory = await ethers.getContractFactory("CommitStore");
    commitStore = await CommitStoreFactory.deploy();

    // Deploy ProjectRegistry
    const ProjectRegistryFactory = await ethers.getContractFactory("ProjectRegistry");
    projectRegistry = await ProjectRegistryFactory.deploy();
  });

  describe("Notary Contract", function () {
    it("Should publish and retrieve Merkle roots", async function () {
      const runId = ethers.keccak256(ethers.toUtf8Bytes("test-run-123"));
      const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("test evidence"));

      // Initially should be empty
      expect(await notary.get(runId)).to.equal("0x" + "00".repeat(32));

      // Publish
      await notary.publish(runId, merkleRoot);

      // Should return the published root
      expect(await notary.get(runId)).to.equal(merkleRoot);
    });

    it("Should prevent duplicate publications", async function () {
      const runId = ethers.keccak256(ethers.toUtf8Bytes("test-run-123"));
      const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("test evidence"));

      // First publication should work
      await notary.publish(runId, merkleRoot);

      // Second publication should fail
      await expect(notary.publish(runId, merkleRoot)).to.be.revertedWith("set");
    });

    it("Should emit Notarized event", async function () {
      const runId = ethers.keccak256(ethers.toUtf8Bytes("test-run-123"));
      const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("test evidence"));

      const tx = await notary.publish(runId, merkleRoot);
      const receipt = await tx.wait();
      const block = await ethers.provider.getBlock(receipt!.blockNumber);

      await expect(tx)
        .to.emit(notary, "Notarized")
        .withArgs(runId, merkleRoot, owner.address, block!.timestamp);
    });
  });

  describe("CommitStore Contract", function () {
    it("Should store and retrieve encrypted data", async function () {
      const commitId = ethers.keccak256(ethers.toUtf8Bytes("test-commit-123"));
      const labelHash = ethers.keccak256(ethers.toUtf8Bytes("test-label"));
      const ciphertext = ethers.toUtf8Bytes("encrypted-data-here");
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("original-data"));

      // Initially should be empty
      expect(await commitStore.get(commitId)).to.equal("0x");

      // Commit data
      await commitStore.commit(commitId, labelHash, ciphertext, dataHash);

      // Should return the stored data
      expect(await commitStore.get(commitId)).to.equal(ethers.hexlify(ciphertext));
    });

    it("Should prevent duplicate commits", async function () {
      const commitId = ethers.keccak256(ethers.toUtf8Bytes("test-commit-123"));
      const labelHash = ethers.keccak256(ethers.toUtf8Bytes("test-label"));
      const ciphertext = ethers.toUtf8Bytes("encrypted-data-here");
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("original-data"));

      // First commit should work
      await commitStore.commit(commitId, labelHash, ciphertext, dataHash);

      // Second commit should fail
      await expect(commitStore.commit(commitId, labelHash, ciphertext, dataHash))
        .to.be.revertedWith("exists");
    });

    it("Should emit Committed event", async function () {
      const commitId = ethers.keccak256(ethers.toUtf8Bytes("test-commit-123"));
      const labelHash = ethers.keccak256(ethers.toUtf8Bytes("test-label"));
      const ciphertext = ethers.toUtf8Bytes("encrypted-data-here");
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("original-data"));

      const tx = await commitStore.commit(commitId, labelHash, ciphertext, dataHash);
      const receipt = await tx.wait();
      const block = await ethers.provider.getBlock(receipt!.blockNumber);

      await expect(tx)
        .to.emit(commitStore, "Committed")
        .withArgs(commitId, labelHash, dataHash, block!.timestamp);
    });

    it("Should store metadata correctly", async function () {
      const commitId = ethers.keccak256(ethers.toUtf8Bytes("test-commit-123"));
      const labelHash = ethers.keccak256(ethers.toUtf8Bytes("test-label"));
      const ciphertext = ethers.toUtf8Bytes("encrypted-data-here");
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("original-data"));

      await commitStore.commit(commitId, labelHash, ciphertext, dataHash);

      const [storedLabelHash, storedDataHash] = await commitStore.getMetadata(commitId);
      expect(storedLabelHash).to.equal(labelHash);
      expect(storedDataHash).to.equal(dataHash);
    });
  });

  describe("ProjectRegistry Contract", function () {
    it("Should register and retrieve project releases", async function () {
      const version = "v1.0.0";
      const versionId = ethers.keccak256(ethers.toUtf8Bytes(version));
      const sourceHash = ethers.keccak256(ethers.toUtf8Bytes("git-commit-hash"));
      const artifactHash = ethers.keccak256(ethers.toUtf8Bytes("artifact-hash"));

      // Initially should not be released
      expect(await projectRegistry.isReleased(versionId)).to.be.false;

      // Register release
      await projectRegistry.register(versionId, sourceHash, artifactHash, version);

      // Should be marked as released
      expect(await projectRegistry.isReleased(versionId)).to.be.true;

      // Should return correct release info
      const releaseInfo = await projectRegistry.getRelease(versionId);
      expect(releaseInfo.sourceHash).to.equal(sourceHash);
      expect(releaseInfo.artifactHash).to.equal(artifactHash);
      expect(releaseInfo.version).to.equal(version);
      expect(releaseInfo.exists).to.be.true;
    });

    it("Should prevent duplicate registrations", async function () {
      const version = "v1.0.0";
      const versionId = ethers.keccak256(ethers.toUtf8Bytes(version));
      const sourceHash = ethers.keccak256(ethers.toUtf8Bytes("git-commit-hash"));
      const artifactHash = ethers.keccak256(ethers.toUtf8Bytes("artifact-hash"));

      // First registration should work
      await projectRegistry.register(versionId, sourceHash, artifactHash, version);

      // Second registration should fail
      await expect(projectRegistry.register(versionId, sourceHash, artifactHash, version))
        .to.be.revertedWith("done");
    });

    it("Should emit Release event", async function () {
      const version = "v1.0.0";
      const versionId = ethers.keccak256(ethers.toUtf8Bytes(version));
      const sourceHash = ethers.keccak256(ethers.toUtf8Bytes("git-commit-hash"));
      const artifactHash = ethers.keccak256(ethers.toUtf8Bytes("artifact-hash"));

      const tx = await projectRegistry.register(versionId, sourceHash, artifactHash, version);
      const receipt = await tx.wait();
      const block = await ethers.provider.getBlock(receipt!.blockNumber);

      await expect(tx)
        .to.emit(projectRegistry, "Release")
        .withArgs(versionId, sourceHash, artifactHash, block!.timestamp, version);
    });

    it("Should verify hashes correctly", async function () {
      const version = "v1.0.0";
      const versionId = ethers.keccak256(ethers.toUtf8Bytes(version));
      const sourceHash = ethers.keccak256(ethers.toUtf8Bytes("git-commit-hash"));
      const artifactHash = ethers.keccak256(ethers.toUtf8Bytes("artifact-hash"));

      await projectRegistry.register(versionId, sourceHash, artifactHash, version);

      // Correct hashes should verify
      expect(await projectRegistry.verify(versionId, sourceHash, artifactHash)).to.be.true;

      // Wrong hashes should not verify
      const wrongHash = ethers.keccak256(ethers.toUtf8Bytes("wrong-hash"));
      expect(await projectRegistry.verify(versionId, wrongHash, artifactHash)).to.be.false;
      expect(await projectRegistry.verify(versionId, sourceHash, wrongHash)).to.be.false;
    });
  });

  describe("Integration Tests", function () {
    it("Should handle complete notarization workflow", async function () {
      const runId = ethers.keccak256(ethers.toUtf8Bytes("integration-test-run"));
      const merkleRoot = ethers.keccak256(ethers.toUtf8Bytes("evidence1evidence2evidence3"));
      
      const commitId = runId; // Use same ID for commit
      const labelHash = ethers.keccak256(ethers.toUtf8Bytes("run-audit-v1"));
      const auditData = ethers.toUtf8Bytes('{"query":"test","evidence":["item1","item2"]}');
      const dataHash = ethers.keccak256(auditData);

      // 1. Publish notarization
      await notary.publish(runId, merkleRoot);
      expect(await notary.get(runId)).to.equal(merkleRoot);

      // 2. Commit encrypted audit data
      await commitStore.commit(commitId, labelHash, auditData, dataHash);
      expect(await commitStore.get(commitId)).to.equal(ethers.hexlify(auditData));

      // 3. Register project version
      const version = "integration-test-v1";
      const versionId = ethers.keccak256(ethers.toUtf8Bytes(version));
      const sourceHash = ethers.keccak256(ethers.toUtf8Bytes("current-commit"));
      const artifactHash = ethers.keccak256(ethers.toUtf8Bytes("built-artifact"));

      await projectRegistry.register(versionId, sourceHash, artifactHash, version);
      expect(await projectRegistry.isReleased(versionId)).to.be.true;

      // Verify complete workflow
      expect(await notary.isNotarized(runId)).to.be.true;
      expect(await commitStore.exists(commitId)).to.be.true;
      expect(await projectRegistry.verify(versionId, sourceHash, artifactHash)).to.be.true;
    });
  });
});
