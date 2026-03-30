# Image Steganography Registry

A hybrid image steganography app that hides secret data inside images, stores the resulting stego image on IPFS, and records the image metadata on Ethereum via a smart contract.

## Project Overview

This repository contains three main components:

- `frontend-react/` — React frontend for uploading images, hiding/extracting secrets, and verifying blockchain records.
- `backend/` — Flask API for image steganography, IPFS upload/download, and blockchain interaction.
- `contracts/` — Solidity smart contract to register image records and verify ownership.

## Features

- Hide secret text inside an image using LSB steganography
- Optional AES encryption of secret payload with a password
- Upload steganographic images and metadata to IPFS
- Persist image records on Ethereum using `SteganographyRegistry`
- Verify image ownership and retrieve stored records

## Architecture

- `frontend-react`: React app served by Flask in production build mode
- `backend/app.py`: Flask server with REST API endpoints and static asset routing
- `backend/steganography.py`: LSB-based data hiding and extraction + optional AES encryption
- `backend/ipfs_client.py`: Upload/download support for local IPFS or Infura IPFS
- `backend/blockchain_client.py`: Interaction with Ethereum via Web3 and the deployed contract
- `contracts/SteganographyRegistry.sol`: Smart contract for image record storage

## Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ (recommended)
- `virtualenv` or Python venv support
- Hardhat for contract deployment
- IPFS daemon running locally or Infura IPFS credentials

### Install dependencies

1. Clone the repo

```bash
git clone <repo-url>
cd "image stegnography"
```

2. Install backend Python dependencies

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
```

3. Install frontend dependencies

```bash
cd frontend-react
npm install
cd ..
```

4. Install Hardhat dependencies

```bash
npm install
```

## Environment

Create a `.env` file in the repository root with the following values:

```env
INFURA_PROJECT_ID=your_infura_project_id
PRIVATE_KEY=your_eth_private_key
CONTRACT_ADDRESS=0x...            # Optional if using deployed contract
IPFS_HOST=localhost               # Optional for local IPFS
IPFS_PORT=5001                    # Optional for local IPFS
INFURA_IPFS_PROJECT_ID=...        # Optional if using Infura IPFS
INFURA_IPFS_PROJECT_SECRET=...    # Optional if using Infura IPFS
```

> If you use local IPFS, make sure the daemon is running on `http://localhost:5001`.

## Smart Contract Deployment

The Solidity contract is located in `contracts/SteganographyRegistry.sol`.

1. Deploy to local network:

```bash
npm run deploy-local
```

2. Deploy to Sepolia testnet:

```bash
npm run deploy
```

3. After deployment, update `CONTRACT_ADDRESS` in `.env` or `backend/contract-config.json`.

## Running the app

### Backend only

From the project root:

```bash
.\.venv\Scripts\activate
python backend/app.py
```

The backend exposes API endpoints such as:

- `GET /api/health`
- `POST /api/hide`
- `POST /api/extract`
- `POST /api/verify`

### Frontend development

From `frontend-react/`:

```bash
npm start
```

The frontend expects the backend API at `/api` by default. Use `REACT_APP_API_BASE` to override the base URL if needed.

### Production mode

Build the frontend and serve it with Flask:

```bash
cd frontend-react
npm run build
cd ..
.\.venv\Scripts\activate
python backend/app.py
```

## Usage

1. Upload an image and secret text in the frontend.
2. Optionally enter a password to encrypt the hidden payload.
3. Hide secret data and store the stego image on IPFS.
4. Register the IPFS image hash and metadata hash on Ethereum.
5. Use extract/verify flows to recover hidden text and confirm ownership.

## Project Structure

- `backend/`
  - `app.py` — Flask API server
  - `steganography.py` — Image hide/extract logic
  - `ipfs_client.py` — IPFS upload/download logic
  - `blockchain_client.py` — Contract interaction
  - `utils.py` — helper utilities and validation
  - `requirements.txt` — Python dependencies
- `frontend-react/` — React UI source and build artifacts
- `contracts/` — Solidity smart contract source
- `scripts/deploy.js` — Hardhat contract deploy script
- `setup-contract.js` — Deployment guidance helper
- `contract-address.json` — persisted deployed contract address info

## Notes

- The backend limits uploads to 16 MB.
- Supported image formats: `png`, `jpg`, `jpeg`, `gif`, `bmp`, `tiff`, `webp`.
- Sensitive data such as `PRIVATE_KEY` should never be committed to source control.

## License

This project is provided as-is. Update the license section to reflect your preferred license.
