import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config({ path: "../.env" });

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 300 },
    },
  },
  networks: {
    hardhat: {},
    fuji: {
      url: process.env.AVALANCHE_RPC || "https://api.avax-test.network/ext/bc/C/rpc",
      accounts: process.env.PUBLISHER_PRIVATE_KEY ? [process.env.PUBLISHER_PRIVATE_KEY] : [],
      chainId: 43113,
    },
  },
};

export default config;


