"""Quick test script for BharatShield API."""
import urllib.request
import json

url = 'http://localhost:8000/api/verify'
filepath = r'C:\Users\himan\Desktop\BharatShield-MVP\backend\test_data\clean_pan.png'

boundary = '----FormBoundary7MA4YWxkTrZu0gW'
with open(filepath, 'rb') as f:
    file_data = f.read()

disp = b'Content-Disposition: form-data; name="document"; filename="clean_pan.png"\r\n'
body = (
    ('--' + boundary + '\r\n').encode() +
    disp +
    b'Content-Type: image/png\r\n\r\n' +
    file_data +
    ('\r\n--' + boundary + '--\r\n').encode()
)

req = urllib.request.Request(url, data=body, method='POST')
req.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
req.add_header('Content-Length', str(len(body)))

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        print('CLEAN DOC TEST:')
        print(f'  ID: {result["verification_id"]}')
        print(f'  Trust Score: {result["trust_score"]}')
        print(f'  Risk: {result["risk_level"]}')
        print(f'  Doc Type: {result["document_type"]}')
        print(f'  Time: {result["processing_time"]}s')
        sigs = {k: v['status'] for k, v in result['signals'].items()}
        print(f'  Signals: {sigs}')
        print('  Reasons:')
        for r in result.get('reasons', []):
            print(f'    [{r["impact"]:+d}] {r["reason"]}')
except Exception as e:
    print(f'ERROR: {e}')

# Now test tampered doc
print()
filepath2 = r'C:\Users\himan\Desktop\BharatShield-MVP\backend\test_data\tampered_aadhaar.png'
with open(filepath2, 'rb') as f:
    file_data2 = f.read()

disp2 = b'Content-Disposition: form-data; name="document"; filename="tampered_aadhaar.png"\r\n'
body2 = (
    ('--' + boundary + '\r\n').encode() +
    disp2 +
    b'Content-Type: image/png\r\n\r\n' +
    file_data2 +
    ('\r\n--' + boundary + '--\r\n').encode()
)

req2 = urllib.request.Request(url, data=body2, method='POST')
req2.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)
req2.add_header('Content-Length', str(len(body2)))

try:
    with urllib.request.urlopen(req2, timeout=60) as resp:
        result2 = json.loads(resp.read())
        print('TAMPERED DOC TEST:')
        print(f'  ID: {result2["verification_id"]}')
        print(f'  Trust Score: {result2["trust_score"]}')
        print(f'  Risk: {result2["risk_level"]}')
        print(f'  Doc Type: {result2["document_type"]}')
        print(f'  Time: {result2["processing_time"]}s')
        sigs2 = {k: v['status'] for k, v in result2['signals'].items()}
        print(f'  Signals: {sigs2}')
        print('  Reasons:')
        for r in result2.get('reasons', []):
            print(f'    [{r["impact"]:+d}] {r["reason"]}')
except Exception as e:
    print(f'ERROR: {e}')
