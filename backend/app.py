from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import hashlib
import secrets
from datetime import datetime
import json

from steganography import ImageSteganography
from blockchain_client import BlockchainClient
from ipfs_client import IPFSClient
from utils import allowed_file, generate_image_id, validate_image_id

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
        print(f"📁 Created uploads directory at: {UPLOAD_FOLDER}")
    except Exception as e:
        print(f"❌ Error creating uploads directory: {str(e)}")
        exit(1)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize clients
stego = ImageSteganography()
blockchain = BlockchainClient()
ipfs = IPFSClient()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from frontend directory"""
    return send_from_directory('../frontend', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check IPFS connection
        ipfs_status = ipfs.check_connection()
        
        # Check blockchain connection
        blockchain_status = blockchain.check_connection()
        
        return jsonify({
            'status': 'healthy',
            'ipfs': 'connected' if ipfs_status else 'disconnected',
            'blockchain': 'connected' if blockchain_status else 'disconnected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/hide', methods=['POST'])
def hide_data():
    """Hide secret data in image and store on blockchain"""
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        secret_data = request.form.get('secretData', '')
        password = request.form.get('password', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        if not secret_data:
            return jsonify({'success': False, 'error': 'No secret data provided'}), 400
        
        # Save uploaded file with better error handling
        filename = secrets.token_hex(8) + '_' + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            if not os.path.exists(filepath):
                raise Exception("File failed to save")
            print(f"📁 File saved successfully: {filepath}")
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to save uploaded file: {str(e)}'
            }), 500

        print(f"📁 File saved: {filepath}")
        
        # Generate secure output filename
        output_filename = get_secure_filename(file.filename)
        stego_image_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Perform steganography with specific output path
        print("🔒 Performing steganography...")
        success = stego.hide_data(filepath, secret_data, password, output_path=stego_image_path)
        
        if not success or not os.path.exists(stego_image_path):
            raise Exception("Failed to create steganographic image")

        print(f"💾 Steganographic image saved: {stego_image_path}")

        # Upload steganographic image to IPFS
        print("📡 Uploading to IPFS...")
        with open(stego_image_path, 'rb') as f:
            image_data = f.read()
        
        ipfs_hash = ipfs.upload_file(image_data, f"stego_{filename}")
        print(f"📁 IPFS hash: {ipfs_hash}")
        
        # Create and upload metadata
        metadata = {
            'originalFilename': file.filename,
            'timestamp': int(datetime.now().timestamp()),
            'hasPassword': bool(password),
            'fileSize': len(image_data),
            'steganographyMethod': 'LSB',
            'imageFormat': 'PNG',
            'version': '1.0'
        }
        
        metadata_json = json.dumps(metadata)
        metadata_hash = ipfs.upload_json(metadata)
        print(f"📄 Metadata hash: {metadata_hash}")
        
        # Generate unique image ID
        try:
            image_id = generate_image_id()
            if not image_id:
                raise Exception("generate_image_id returned None")
        except Exception as e:
            print(f"⚠️ Image ID generation failed: {e}")
            # Fallback generation
            timestamp = int(datetime.now().timestamp())
            random_hex = secrets.token_hex(8)
            image_id = f"IMG-{timestamp}-{random_hex}"
        
        print(f"🆔 Generated Image ID: {image_id}")
        
        # Validate image ID
        if not image_id or len(image_id) < 10:
            raise Exception("Invalid image ID generated")
        
        # Store record on blockchain
        print("⛓️ Storing on blockchain...")
        tx_result = blockchain.store_image_record(image_id, ipfs_hash, metadata_hash)
        
        return jsonify({
            'success': True,
            'imageId': image_id,
            'ipfsHash': ipfs_hash,
            'metadataHash': metadata_hash,
            'transactionHash': tx_result.get('transaction_hash', 'N/A'),
            'blockNumber': tx_result.get('block_number', 'N/A'),
            'gasUsed': tx_result.get('gas_used', 'N/A'),
            'downloadUrl': f'/api/download/{image_id}',
            'message': 'Data successfully hidden and stored on blockchain'
        })
        
    except Exception as e:
        print(f"❌ Error in hide_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500
    finally:
        # Only cleanup the input file, keep the output file
        try:
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"⚠️ Cleanup error: {str(e)}")

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract secret data from blockchain and IPFS"""
    try:
        data = request.get_json()
        image_id = data.get('imageId', '').strip()
        password = data.get('password', '')
        
        if not image_id:
            return jsonify({'success': False, 'error': 'Image ID is required'}), 400
        
        if not validate_image_id(image_id):
            return jsonify({'success': False, 'error': 'Invalid Image ID format'}), 400
        
        # Get record from blockchain
        print(f"🔍 Retrieving record for image ID: {image_id}")
        record = blockchain.get_image_record(image_id)
        
        # Download image from IPFS
        print(f"📡 Downloading from IPFS: {record['ipfs_hash']}")
        image_data = ipfs.download_file(record['ipfs_hash'])
        
        # Save image temporarily
        temp_filename = f"temp_{secrets.token_hex(8)}.png"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        safe_file_operations(temp_path, 'wb', image_data)
        
        # Extract hidden data
        print("🔓 Extracting hidden data...")
        extracted_data = stego.extract_data(temp_path, password)
        
        # Download metadata
        try:
            metadata_content = ipfs.download_file(record['metadata_hash'])
            metadata = json.loads(metadata_content.decode('utf-8'))
        except Exception as e:
            print(f"⚠️ Could not load metadata: {e}")
            metadata = {}
        
        # Cleanup
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'data': extracted_data,
            'metadata': {
                'owner': record['owner'],
                'timestamp': datetime.fromtimestamp(record['timestamp']).isoformat(),
                'originalFilename': metadata.get('originalFilename', 'Unknown'),
                'fileSize': metadata.get('fileSize', 0),
                'hasPassword': metadata.get('hasPassword', False)
            }
        })
        
    except Exception as e:
        print(f"❌ Error in extract_data: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Extraction failed: {str(e)}'
        }), 500

@app.route('/api/verify', methods=['POST'])
def verify_ownership():
    """Verify image ownership"""
    try:
        data = request.get_json()
        image_id = data.get('imageId', '').strip()
        user_address = data.get('userAddress', '').strip()
        
        if not image_id or not user_address:
            return jsonify({
                'success': False, 
                'error': 'Image ID and user address are required'
            }), 400
        
        # Validate inputs
        if not validate_image_id(image_id):
            return jsonify({'success': False, 'error': 'Invalid Image ID format'}), 400
        
        if not user_address.startswith('0x') or len(user_address) != 42:
            return jsonify({'success': False, 'error': 'Invalid Ethereum address format'}), 400
        
        # Get record and verify ownership
        print(f"🔍 Verifying ownership for {image_id}")
        record = blockchain.get_image_record(image_id)
        is_owner = blockchain.verify_ownership(image_id, user_address)
        
        return jsonify({
            'success': True,
            'isOwner': is_owner,
            'record': {
                'owner': record['owner'],
                'ipfsHash': record['ipfs_hash'],
                'metadataHash': record['metadata_hash'],
                'timestamp': datetime.fromtimestamp(record['timestamp']).isoformat(),
                'exists': record['exists']
            }
        })
        
    except Exception as e:
        print(f"❌ Error in verify_ownership: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Verification failed: {str(e)}'
        }), 500

@app.route('/api/user-images/<address>', methods=['GET'])
def get_user_images(address):
    """Get all images for a user"""
    try:
        if not address.startswith('0x') or len(address) != 42:
            return jsonify({'success': False, 'error': 'Invalid address format'}), 400
        
        image_ids = blockchain.get_user_images(address)
        
        return jsonify({
            'success': True,
            'imageCount': len(image_ids),
            'imageIds': image_ids
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download/<image_id>', methods=['GET'])
def download_steganographic_image(image_id):
    """Download steganographic image from IPFS"""
    try:
        # Validate image ID
        if not validate_image_id(image_id):
            return jsonify({'success': False, 'error': 'Invalid Image ID format'}), 400
        
        # Get record from blockchain
        print(f"🔍 Retrieving record for image ID: {image_id}")
        record = blockchain.get_image_record(image_id)
        
        if not record['exists']:
            return jsonify({'success': False, 'error': 'Image not found'}), 404
        
        # Download image from IPFS
        print(f"📡 Downloading from IPFS: {record['ipfs_hash']}")
        image_data = ipfs.download_file(record['ipfs_hash'])
        
        # Create response with image data
        from flask import Response
        return Response(
            image_data,
            mimetype='image/png',
            headers={
                'Content-Disposition': f'attachment; filename="steganographic_{image_id}.png"',
                'Content-Type': 'image/png'
            }
        )
        
    except Exception as e:
        print(f"❌ Error in download_steganographic_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Download failed: {str(e)}'
        }), 500

def safe_file_operations(filepath, mode='wb', data=None):
    """Safely handle file operations with proper error handling"""
    try:
        with open(filepath, mode) as f:
            if data:
                if isinstance(data, bytes):
                    f.write(data)
                else:
                    f.write(data.encode('utf-8'))
            return True
    except Exception as e:
        print(f"❌ File operation failed: {str(e)}")
        return False

def get_secure_filename(original_filename):
    """Generate a secure filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_hex = secrets.token_hex(4)
    name, ext = os.path.splitext(original_filename)
    return f"stego_{timestamp}_{random_hex}{ext}"

if __name__ == '__main__':
    print("🚀 Starting Blockchain Steganography Server...")
    print("🔗 Checking connections...")
    
    # Check IPFS connection
    if ipfs.check_connection():
        print("✅ IPFS connected")
    else:
        print("⚠️ IPFS not connected - please start IPFS daemon")
    
    # Check blockchain connection
    if blockchain.check_connection():
        print("✅ Blockchain connected")
    else:
        print("⚠️ Blockchain connection issues")
    
    print("🌐 Server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)