import { ethers } from "hardhat";
import fs from "fs";
import path from "path";

async function main() {
  console.log("🚀 Deploying OPAL Subnet Contracts...");
  
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)));

  // Deploy Notary
  console.log("\n📝 Deploying Notary...");
  const Notary = await ethers.getContractFactory("Notary");
  const notary = await Notary.deploy();
  await notary.waitForDeployment();
  const notaryAddress = await notary.getAddress();
  console.log("✅ Notary deployed to:", notaryAddress);

  // Deploy CommitStore
  console.log("\n🔒 Deploying CommitStore...");
  const CommitStore = await ethers.getContractFactory("CommitStore");
  const commitStore = await CommitStore.deploy();
  await commitStore.waitForDeployment();
  const commitStoreAddress = await commitStore.getAddress();
  console.log("✅ CommitStore deployed to:", commitStoreAddress);

  // Deploy ProjectRegistry
  console.log("\n📋 Deploying ProjectRegistry...");
  const ProjectRegistry = await ethers.getContractFactory("ProjectRegistry");
  const projectRegistry = await ProjectRegistry.deploy();
  await projectRegistry.waitForDeployment();
  const projectRegistryAddress = await projectRegistry.getAddress();
  console.log("✅ ProjectRegistry deployed to:", projectRegistryAddress);

  // Save deployment info
  const deploymentInfo = {
    network: (await ethers.provider.getNetwork()).name,
    chainId: (await ethers.provider.getNetwork()).chainId.toString(),
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      Notary: {
        address: notaryAddress,
        abi: JSON.parse(JSON.stringify(Notary.interface.fragments))
      },
      CommitStore: {
        address: commitStoreAddress,
        abi: JSON.parse(JSON.stringify(CommitStore.interface.fragments))
      },
      ProjectRegistry: {
        address: projectRegistryAddress,
        abi: JSON.parse(JSON.stringify(ProjectRegistry.interface.fragments))
      }
    }
  };

  // Write deployment info to backend
  const backendDir = path.join(__dirname, "../../backend/app/subnet");
  if (!fs.existsSync(backendDir)) {
    fs.mkdirSync(backendDir, { recursive: true });
  }

  fs.writeFileSync(
    path.join(backendDir, "deployment.json"),
    JSON.stringify(deploymentInfo, null, 2)
  );

  // Write individual ABI files
  fs.writeFileSync(
    path.join(backendDir, "notary_abi.json"),
    JSON.stringify(Notary.interface.fragments, null, 2)
  );

  fs.writeFileSync(
    path.join(backendDir, "commit_store_abi.json"),
    JSON.stringify(CommitStore.interface.fragments, null, 2)
  );

  fs.writeFileSync(
    path.join(backendDir, "project_registry_abi.json"),
    JSON.stringify(ProjectRegistry.interface.fragments, null, 2)
  );

  console.log("\n🎉 Deployment Complete!");
  console.log("📁 Contract info saved to backend/app/subnet/");
  console.log("\n📋 Summary:");
  console.log("Notary:", notaryAddress);
  console.log("CommitStore:", commitStoreAddress);
  console.log("ProjectRegistry:", projectRegistryAddress);
  
  console.log("\n⚙️  Add these to your .env:");
  console.log(`SUBNET_NOTARY_ADDR=${notaryAddress}`);
  console.log(`SUBNET_COMMIT_ADDR=${commitStoreAddress}`);
  console.log(`SUBNET_REGISTRY_ADDR=${projectRegistryAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
