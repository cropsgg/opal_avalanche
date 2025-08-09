import { ethers } from "hardhat";

async function main() {
  const F = await ethers.getContractFactory("OpalNotary");
  const c = await F.deploy();
  await c.waitForDeployment();
  console.log("Notary:", await c.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});


