import hre from "hardhat";
import fs from 'fs';

async function main() {
  console.log("🚀 Deploying SteganographyRegistry contract...");
  
  // Get the contract factory
  const SteganographyRegistry = await hre.ethers.getContractFactory("SteganographyRegistry");
  
  // Deploy the contract
  const steganographyRegistry = await SteganographyRegistry.deploy();
  
  // Wait for deployment to complete
  await steganographyRegistry.waitForDeployment();
  
  const contractAddress = await steganographyRegistry.getAddress();
  
  console.log("✅ Contract deployed successfully!");
  console.log("📍 Contract Address:", contractAddress);
  console.log("🌐 Network:", hre.network.name);
  
  // Save contract address to a file
  const contractInfo = {
    address: contractAddress,
    network: hre.network.name,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync('contract-address.json', JSON.stringify(contractInfo, null, 2));
  console.log("💾 Contract info saved to contract-address.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
