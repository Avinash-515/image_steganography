import requests
import json

print('Checking backend /api/health...')
try:
    r = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
    print('Status:', r.status_code)
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print('Health check failed:', e)

print('\nUploading small test file to IPFS node...')
try:
    files = {'file': ('test.txt', b'test content')}
    r = requests.post('http://127.0.0.1:5001/api/v0/add', files=files, timeout=10)
    print('IPFS add status:', r.status_code)
    try:
        print('Response:', r.json())
    except Exception:
        print('Response text:', r.text)
except Exception as e:
    print('IPFS add failed:', e)
