import os
import hashlib
import secrets
import re
from datetime import datetime
from werkzeug.utils import secure_filename

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): The name of the file to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    return file_extension in ALLOWED_EXTENSIONS

def generate_image_id():
    """
    Generate a unique image ID for blockchain storage.
    
    Returns:
        str: A unique image ID in format: IMG-{timestamp}-{random_hex}
    """
    timestamp = int(datetime.now().timestamp())
    random_hex = secrets.token_hex(8)
    return f"IMG-{timestamp}-{random_hex}"

def validate_image_id(image_id):
    """
    Validate if the provided image ID has the correct format.
    
    Args:
        image_id (str): The image ID to validate
        
    Returns:
        bool: True if the image ID format is valid, False otherwise
    """
    if not image_id or not isinstance(image_id, str):
        return False
    
    # Pattern: IMG-{timestamp}-{8_character_hex}
    pattern = r'^IMG-\d{10}-[a-f0-9]{16}$'
    return bool(re.match(pattern, image_id))

def secure_filename_custom(filename):
    """
    Create a secure filename by removing dangerous characters.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: A secure filename
    """
    return secure_filename(filename)

def generate_file_hash(file_path):
    """
    Generate SHA-256 hash of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: SHA-256 hash of the file
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        raise Exception(f"Failed to generate file hash: {str(e)}")

def validate_ethereum_address(address):
    """
    Validate Ethereum address format.
    
    Args:
        address (str): Ethereum address to validate
        
    Returns:
        bool: True if the address format is valid, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
    
    # Check if address starts with 0x and has correct length
    if not address.startswith('0x') or len(address) != 42:
        return False
    
    # Check if remaining characters are valid hex
    hex_part = address[2:]
    return all(c in '0123456789abcdefABCDEF' for c in hex_part)

def format_timestamp(timestamp):
    """
    Format timestamp to ISO format string.
    
    Args:
        timestamp (int): Unix timestamp
        
    Returns:
        str: ISO formatted timestamp string
    """
    try:
        return datetime.fromtimestamp(timestamp).isoformat()
    except Exception:
        return datetime.now().isoformat()

def get_file_size_mb(file_path):
    """
    Get file size in megabytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        float: File size in megabytes
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0

def validate_secret_data(data):
    """
    Validate secret data to be hidden in image.
    
    Args:
        data (str): Secret data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data or not isinstance(data, str):
        return False, "Secret data is required"
    
    if len(data.strip()) == 0:
        return False, "Secret data cannot be empty"
    
    if len(data) > 10000:  # 10KB limit
        return False, "Secret data is too large (max 10KB)"
    
    # Check for potentially dangerous content
    dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
    data_lower = data.lower()
    
    for pattern in dangerous_patterns:
        if pattern in data_lower:
            return False, "Secret data contains potentially dangerous content"
    
    return True, None

def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return True, None  # Password is optional
    
    if len(password) < 4:
        return False, "Password must be at least 4 characters long"
    
    if len(password) > 100:
        return False, "Password is too long (max 100 characters)"
    
    return True, None

def create_metadata(original_filename, file_size, has_password=False, method='LSB'):
    """
    Create metadata dictionary for image record.
    
    Args:
        original_filename (str): Original filename
        file_size (int): File size in bytes
        has_password (bool): Whether password protection is used
        method (str): Steganography method used
        
    Returns:
        dict: Metadata dictionary
    """
    return {
        'originalFilename': original_filename,
        'timestamp': int(datetime.now().timestamp()),
        'hasPassword': has_password,
        'fileSize': file_size,
        'steganographyMethod': method,
        'imageFormat': 'PNG',
        'version': '1.0'
    }

def sanitize_input(text, max_length=1000):
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text (str): Input text to sanitize
        max_length (int): Maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def generate_temp_filename(original_filename, prefix="temp"):
    """
    Generate a temporary filename for processing.
    
    Args:
        original_filename (str): Original filename
        prefix (str): Prefix for temporary file
        
    Returns:
        str: Temporary filename
    """
    timestamp = int(datetime.now().timestamp())
    random_hex = secrets.token_hex(4)
    extension = os.path.splitext(original_filename)[1] if original_filename else '.png'
    
    return f"{prefix}_{timestamp}_{random_hex}{extension}"

def cleanup_temp_files(file_paths):
    """
    Clean up temporary files.
    
    Args:
        file_paths (list): List of file paths to delete
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Cleaned up: {file_path}")
        except Exception as e:
            print(f"⚠️ Failed to cleanup {file_path}: {e}")

def validate_image_dimensions(image_path, max_width=4096, max_height=4096):
    """
    Validate image dimensions.
    
    Args:
        image_path (str): Path to image file
        max_width (int): Maximum allowed width
        max_height (int): Maximum allowed height
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            width, height = img.size
            
            if width > max_width or height > max_height:
                return False, f"Image too large. Max dimensions: {max_width}x{max_height}"
            
            if width < 100 or height < 100:
                return False, "Image too small. Minimum dimensions: 100x100"
            
            return True, None
            
    except Exception as e:
        return False, f"Failed to validate image: {str(e)}"

def calculate_storage_cost(file_size_bytes):
    """
    Calculate estimated storage cost for blockchain transaction.
    
    Args:
        file_size_bytes (int): File size in bytes
        
    Returns:
        dict: Cost information
    """
    # Rough estimates (these would need to be updated based on current gas prices)
    base_gas = 200000  # Base gas for transaction
    gas_per_byte = 68  # Gas per byte of data
    
    estimated_gas = base_gas + (file_size_bytes * gas_per_byte)
    gas_price_gwei = 20  # Example gas price in Gwei
    
    # Convert to ETH
    gas_cost_eth = (estimated_gas * gas_price_gwei) / 1e9
    
    return {
        'estimated_gas': estimated_gas,
        'gas_price_gwei': gas_price_gwei,
        'estimated_cost_eth': gas_cost_eth,
        'estimated_cost_usd': gas_cost_eth * 2000  # Assuming $2000/ETH
    }
