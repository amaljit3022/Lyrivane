import urllib.request
import json

req = urllib.request.Request('http://localhost:8000/api/v1/projects/test-sync-docker-2dal')
response = urllib.request.urlopen(req)
data = json.loads(response.read())

for line in data['canonical_timeline']['lines']:
    start_sec = line['start_ms'] / 1000
    end_sec = line['end_ms'] / 1000
    if start_sec > 130:
        print(f"{start_sec:.2f} - {end_sec:.2f}: {line.get('display_text')}")
