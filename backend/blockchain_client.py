from web3 import Web3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class BlockchainClient:
    def __init__(self):
        # Initialize Web3 connection
        # Use Sepolia network with your Infura credentials
        infura_url = f"https://sepolia.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        
        # Contract configuration
        self.contract_address = os.getenv('CONTRACT_ADDRESS', '0xA44241DCe6A3D340741CE15d3cd8E22fC2e927cE')
        self.private_key = os.getenv('PRIVATE_KEY')
        
        # Contract ABI
        self.contract_abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "imageId", "type": "string"},
                    {"indexed": False, "name": "ipfsHash", "type": "string"},
                    {"indexed": False, "name": "metadataHash", "type": "string"},
                    {"indexed": True, "name": "owner", "type": "address"}
                ],
                "name": "ImageStored",
                "type": "event"
            },
            {
                "inputs": [
                    {"name": "imageId", "type": "string"},
                    {"name": "ipfsHash", "type": "string"},
                    {"name": "metadataHash", "type": "string"}
                ],
                "name": "storeImageRecord",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "imageId", "type": "string"}],
                "name": "getImageRecord",
                "outputs": [
                    {
                        "components": [
                            {"name": "ipfsHash", "type": "string"},
                            {"name": "metadataHash", "type": "string"},
                            {"name": "timestamp", "type": "uint256"},
                            {"name": "owner", "type": "address"},
                            {"name": "exists", "type": "bool"}
                        ],
                        "name": "",
                        "type": "tuple"
                    }
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "user", "type": "address"}],
                "name": "getUserImages",
                "outputs": [{"name": "", "type": "string[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "imageId", "type": "string"},
                    {"name": "user", "type": "address"}
                ],
                "name": "verifyImageOwnership",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Initialize contract
        if self.contract_address and self.w3.is_address(self.contract_address):
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=self.contract_abi
            )
        else:
            self.contract = None
            print("⚠️ Contract address not configured")
        
        # Initialize account
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            # Check account balance
            try:
                balance = self.w3.eth.get_balance(self.account.address)
                balance_eth = self.w3.from_wei(balance, 'ether')
                print(f"💰 Account balance: {balance_eth} ETH")
            except Exception as e:
                print(f"⚠️ Could not check balance: {e}")
        else:
            self.account = None
            print("⚠️ Private key not configured")
    
    def check_connection(self):
        """Check blockchain connection"""
        try:
            return self.w3.is_connected() and self.contract is not None
        except:
            return False
    
    def store_image_record(self, image_id, ipfs_hash, metadata_hash):
        """Store image record on blockchain"""
        try:
            if not self.contract or not self.account:
                raise Exception("Blockchain client not properly configured")
            
            print(f"📝 Storing record: {image_id}")
            
            # Check if image already exists
            try:
                existing_record = self.contract.functions.getImageRecord(image_id).call()
                if existing_record[4]:  # exists field
                    print(f"⚠️ Image ID already exists: {image_id}")
                    # Generate a new unique ID
                    import time
                    import secrets
                    timestamp = int(time.time())
                    random_hex = secrets.token_hex(8)
                    image_id = f"IMG-{timestamp}-{random_hex}"
                    print(f"🔄 Generated new ID: {image_id}")
            except Exception as e:
                print(f"🔍 Image ID check: {e}")
            
            # Get current account info
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            balance = self.w3.eth.get_balance(self.account.address)
            
            print(f"🔍 Account: {self.account.address}")
            print(f"🔍 Nonce: {nonce}")
            print(f"🔍 Gas Price: {gas_price}")
            print(f"🔍 Balance: {self.w3.from_wei(balance, 'ether')} ETH")
            print(f"🔍 Contract Address: {self.contract_address}")
            
            # Estimate gas for the transaction
            try:
                gas_estimate = self.contract.functions.storeImageRecord(
                    image_id, ipfs_hash, metadata_hash
                ).estimate_gas({'from': self.account.address})
                print(f"🔍 Estimated gas: {gas_estimate}")
                gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer
            except Exception as e:
                print(f"⚠️ Gas estimation failed: {e}")
                gas_limit = 200000  # Use default
            
            # Build transaction
            transaction = self.contract.functions.storeImageRecord(
                image_id, ipfs_hash, metadata_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': gas_price
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = tx_hash.hex()
            
            print(f"📤 Transaction sent: {tx_hash_hex}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"🔍 Transaction receipt status: {receipt.status}")
            print(f"🔍 Gas used: {receipt.gasUsed}")
            print(f"🔍 Block number: {receipt.blockNumber}")
            
            if receipt.status == 1:
                print(f"✅ Transaction confirmed in block: {receipt.blockNumber}")
                return {
                    'transaction_hash': tx_hash_hex,
                    'block_number': receipt.blockNumber,
                    'gas_used': receipt.gasUsed
                }
            else:
                # Get more details about the failure
                try:
                    tx = self.w3.eth.get_transaction(tx_hash)
                    print(f"🔍 Transaction details: {tx}")
                except Exception as e:
                    print(f"🔍 Could not get transaction details: {e}")
                raise Exception(f"Transaction failed with status: {receipt.status}")
                
        except Exception as e:
            raise Exception(f"Blockchain storage failed: {str(e)}")
    
    def get_image_record(self, image_id):
        """Retrieve image record from blockchain"""
        try:
            if not self.contract:
                raise Exception("Contract not configured")
            
            print(f"🔍 Retrieving record: {image_id}")
            
            result = self.contract.functions.getImageRecord(image_id).call()
            
            return {
                'ipfs_hash': result[0],
                'metadata_hash': result[1],
                'timestamp': result[2],
                'owner': result[3],
                'exists': result[4]
            }
            
        except Exception as e:
            if "Image not found" in str(e):
                raise Exception(f"Image ID '{image_id}' not found on blockchain")
            else:
                raise Exception(f"Failed to retrieve record: {str(e)}")
    
    def get_user_images(self, user_address):
        """Get all image IDs for a user"""
        try:
            if not self.contract:
                raise Exception("Contract not configured")
            
            user_address = Web3.to_checksum_address(user_address)
            result = self.contract.functions.getUserImages(user_address).call()
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to get user images: {str(e)}")
    
    def verify_ownership(self, image_id, user_address):
        """Verify if user owns the image"""
        try:
            if not self.contract:
                raise Exception("Contract not configured")
            
            user_address = Web3.to_checksum_address(user_address)
            result = self.contract.functions.verifyImageOwnership(image_id, user_address).call()
            
            return result
            
        except Exception as e:
            raise Exception(f"Ownership verification failed: {str(e)}")
    
    def get_transaction_info(self, tx_hash):
        """Get transaction information"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            
            return {
                'status': 'success' if receipt.status == 1 else 'failed',
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'gas_price': transaction.gasPrice,
                'transaction_fee': receipt.gasUsed * transaction.gasPrice / 10**18,
                'timestamp': self.w3.eth.get_block(receipt.blockNumber).timestamp
            }
            
        except Exception as e:
            raise Exception(f"Failed to get transaction info: {str(e)}")
    
    def get_account_balance(self):
        """Get account ETH balance"""
        try:
            if not self.account:
                return 0
            
            balance_wei = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            
            return float(balance_eth)
            
        except Exception as e:
            print(f"Failed to get balance: {e}")
            return 0