import requests
import json
from io import BytesIO
import os


class IPFSClient:
    def __init__(self, host='localhost', port=5001):
        self.host = host
        self.port = port
        self.api_url = f"http://{host}:{port}/api/v0"
        self.client = None

        try:
            # Test connection using HTTP API
            response = requests.post(f"{self.api_url}/version", timeout=5)
            if response.status_code == 200:
                print("✅ IPFS client initialized (HTTP API)")
                self.client = True
            else:
                print(f"⚠️ IPFS API returned status {response.status_code}")
                self.client = None
        except Exception as e:
            print(f"⚠️ IPFS client initialization failed: {e}")
            self.client = None

    def check_connection(self):
        """Check IPFS connection"""
        try:
            if self.client:
                response = requests.post(f"{self.api_url}/version", timeout=5)
                return response.status_code == 200
            return False
        except:
            return False

    def upload_file(self, file_data, filename):
        """Upload file to IPFS"""
        try:
            if not self.client:
                raise Exception("IPFS client not connected")

            print(f"📤 Uploading to IPFS: {filename}")

            # Upload file using HTTP API
            files = {'file': (filename, BytesIO(file_data))}
            response = requests.post(f"{self.api_url}/add", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                hash_value = result['Hash']
                print(f"✅ File uploaded to IPFS: {hash_value}")
                return hash_value
            else:
                raise Exception(f"Upload failed with status {response.status_code}")

        except Exception as e:
            raise Exception(f"IPFS upload failed: {str(e)}")

    def upload_json(self, data):
        """Upload JSON data to IPFS"""
        try:
            if isinstance(data, dict):
                json_data = json.dumps(data)
            else:
                json_data = data

            json_bytes = json_data.encode('utf-8')
            return self.upload_file(json_bytes, 'metadata.json')

        except Exception as e:
            raise Exception(f"JSON upload failed: {str(e)}")

    def download_file(self, hash_value):
        """Download file from IPFS"""
        try:
            if not self.client:
                raise Exception("IPFS client not connected")

            print(f"📥 Downloading from IPFS: {hash_value}")

            # Download file using HTTP API
            response = requests.post(f"{self.api_url}/cat", params={'arg': hash_value}, timeout=30)
            
            if response.status_code == 200:
                file_data = response.content
                print(f"✅ File downloaded: {len(file_data)} bytes")
                return file_data
            else:
                raise Exception(f"Download failed with status {response.status_code}")

        except Exception as e:
            raise Exception(f"IPFS download failed: {str(e)}")


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0

    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def get_image_info(image_path):
    """Get basic image information"""
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'mode': img.mode,
                'format': img.format,
                'size_bytes': os.path.getsize(image_path)
            }
    except Exception as e:
        return {'error': str(e)}
