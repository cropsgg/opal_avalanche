import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import * as dotenv from "dotenv";

dotenv.config({ path: "../.env" });

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { 
        enabled: true, 
        runs: 1000 // Higher optimization for immutable contracts
      },
      viaIR: true // Enable intermediate representation for better optimization
    },
  },
  networks: {
    hardhat: {
      chainId: 43210,
      initialBaseFeePerGas: 20000000, // Match subnet genesis
    },
    subnet: {
      url: process.env.SUBNET_RPC || "http://localhost:9650/ext/bc/opal/rpc",
      accounts: process.env.SUBNET_SENDER_PK ? [process.env.SUBNET_SENDER_PK] : [],
      chainId: 43210,
      gasPrice: 25000000, // 25 gwei
      gas: 8000000,
    },
    local: {
      url: "http://localhost:8545",
      accounts: process.env.SUBNET_SENDER_PK ? [process.env.SUBNET_SENDER_PK] : [],
      chainId: 31337, // Local Hardhat network
    }
  },
  gasReporter: {
    enabled: true,
    currency: "USD",
    gasPrice: 25, // gwei
  },
  etherscan: {
    apiKey: {
      // Placeholder - private subnet won't have public explorer
      subnet: "placeholder"
    },
    customChains: [
      {
        network: "subnet",
        chainId: 43210,
        urls: {
          apiURL: "http://localhost:4000/api", // Placeholder
          browserURL: "http://localhost:4000"
        }
      }
    ]
  }
};

export default config;
