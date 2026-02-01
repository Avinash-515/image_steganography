import requests
import json
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()


class IPFSClient:
    def __init__(self, host=None, port=None):
        # Allow configuration via environment variables
        env_host = os.getenv('IPFS_HOST')
        env_port = os.getenv('IPFS_PORT')
        self.host = host or env_host or 'localhost'
        self.port = port or env_port or 5001

        # Check for Infura IPFS credentials (optional)
        self.infura_project_id = os.getenv('INFURA_IPFS_PROJECT_ID')
        self.infura_project_secret = os.getenv('INFURA_IPFS_PROJECT_SECRET')
        self.use_infura = bool(self.infura_project_id and self.infura_project_secret)

        if self.use_infura:
            # Use Infura IPFS HTTP API (requires project id & secret)
            self.api_url = 'https://ipfs.infura.io:5001/api/v0'
            self.auth = (self.infura_project_id, self.infura_project_secret)
            print(f"🔒 IPFS configured to use Infura API: {self.api_url}")
        else:
            self.api_url = f"http://{self.host}:{self.port}/api/v0"
            self.auth = None
            print(f"🔌 IPFS configured to use local API: {self.api_url}")

        self.client = None

        try:
            # Test connection using HTTP API
            response = requests.post(f"{self.api_url}/version", timeout=5, auth=self.auth)
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
            # Always attempt to call the /version endpoint so the client can detect a daemon
            response = requests.post(f"{self.api_url}/version", timeout=5, auth=self.auth)
            return response.status_code == 200
        except Exception:
            return False

    def upload_file(self, file_data, filename):
        """Upload file to IPFS"""
        try:
            # If the daemon was started after the client, re-check availability
            if not self.client:
                if self.check_connection():
                    self.client = True
                else:
                    raise Exception("IPFS client not connected")

            print(f"📤 Uploading to IPFS: {filename}")

            # Upload file using HTTP API (supports Infura or local node)
            files = {'file': (filename, BytesIO(file_data))}
            response = requests.post(f"{self.api_url}/add", files=files, timeout=60, auth=self.auth)

            if response.status_code == 200:
                # Infura may return JSON array or object; handle both
                try:
                    result = response.json()
                except Exception:
                    # Some gateways stream newline separated JSON; take first line
                    content = response.content.decode('utf-8').splitlines()[0]
                    result = json.loads(content)

                hash_value = result.get('Hash') or result.get('Cid') or result.get('hash')
                if not hash_value:
                    raise Exception(f"Unexpected response from IPFS add: {result}")

                print(f"✅ File uploaded to IPFS: {hash_value}")
                return hash_value
            else:
                raise Exception(f"Upload failed with status {response.status_code}: {response.text}")

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
            # If the daemon was started after the client, re-check availability
            if not self.client:
                if self.check_connection():
                    self.client = True
                else:
                    raise Exception("IPFS client not connected")

            print(f"📥 Downloading from IPFS: {hash_value}")

            # Download file using HTTP API
            response = requests.post(f"{self.api_url}/cat", params={'arg': hash_value}, timeout=60, auth=self.auth)

            if response.status_code == 200:
                file_data = response.content
                print(f"✅ File downloaded: {len(file_data)} bytes")
                return file_data
            else:
                raise Exception(f"Download failed with status {response.status_code}: {response.text}")

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