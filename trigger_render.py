import urllib.request
import json

data = json.dumps({
    "template_id": "cinematic-fade",
    "renderer": "remotion",
    "resolution": "1080p",
    "fps": 30,
    "codec": "h264",
    "aspect_ratio": "1:1",
    "motion_intensity": 0.6
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8005/api/v1/projects/test-sync-docker-2dal/render",
    data=data,
    headers={"Content-Type": "application/json"}
)

response = urllib.request.urlopen(req)
print(response.read().decode("utf-8"))
