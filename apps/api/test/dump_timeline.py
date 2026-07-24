import urllib.request
import json
import sys

req = urllib.request.Request('http://localhost:8000/api/v1/projects/test-sync-docker-ogh7')
response = urllib.request.urlopen(req)
data = json.loads(response.read())

timeline = data.get("canonical_timeline", {})
lines = timeline.get("lines", [])

for l in lines:
    print(f"{l['start_ms']/1000:.2f} - {l['end_ms']/1000:.2f}: {l['display_text']}")
    for w in l.get('words', []):
        print(f"  {w['start_ms']/1000:.2f} - {w['end_ms']/1000:.2f}: {w['display_text']}")
