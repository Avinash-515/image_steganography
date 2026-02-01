# Smart Contract Deployment Guide

## Prerequisites

Before deploying the contract, you need:

1. **Infura Project ID** (Free)
2. **Private Key** with Sepolia ETH
3. **Environment Variables**

## Step 1: Get Infura Project ID

1. Go to https://infura.io/
2. Create a free account
3. Create a new project
4. Select "Ethereum" network
5. Copy your Project ID

## Step 2: Get Sepolia ETH

1. Go to https://sepoliafaucet.com/
2. Enter your wallet address
3. Request test ETH (you'll need some for gas fees)

## Step 3: Create Environment File

Create a `.env` file in the project root with:

```
INFURA_PROJECT_ID=your_infura_project_id_here
PRIVATE_KEY=your_private_key_here
```

## Step 4: Deploy the Contract

Run these commands:

```bash
# Compile the contract
npm run compile

# Deploy to Sepolia testnet
npm run deploy
```

## Step 5: Update Backend Configuration

After deployment, you'll get a contract address. Update your backend `.env` file:

```
INFURA_PROJECT_ID=your_infura_project_id
CONTRACT_ADDRESS=your_deployed_contract_address
PRIVATE_KEY=your_private_key_here
```

## Alternative: Deploy Locally (for testing)

If you want to test locally first:

```bash
# Start local Hardhat node
npx hardhat node

# In another terminal, deploy locally
npm run deploy-local
```

## Troubleshooting

- **"Insufficient funds"**: Get more Sepolia ETH from faucet
- **"Invalid private key"**: Make sure private key starts with 0x
- **"Network not found"**: Check your Infura project ID
