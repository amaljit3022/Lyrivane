import requests
import time
import os
from pathlib import Path

API_URL = "http://localhost:8005/api/v1"

def test_workflow():
    print("1. Creating project...")
    res = requests.post(f"{API_URL}/projects", json={
        "title": "Test Song",
        "artist": "Test Artist",
        "language": "en"
    })
    res.raise_for_status()
    project = res.json()
    project_id = project["project_id"]
    print(f"Created project: {project_id}")

    print("2. Uploading dummy audio...")
    # Create a dummy .mp3 file
    dummy_mp3 = Path("dummy.mp3")
    if not dummy_mp3.exists():
        os.system("ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 10 -q:a 9 -acodec libmp3lame dummy.mp3")
    
    with open(dummy_mp3, "rb") as f:
        res = requests.post(f"{API_URL}/projects/{project_id}/audio", files={"file": ("dummy.mp3", f, "audio/mpeg")})
    res.raise_for_status()
    print("Audio uploaded.")

    print("3. Uploading lyrics...")
    lyrics = "[00:01.00] This is a test\n[00:05.00] Of the alignment system"
    res = requests.post(f"{API_URL}/projects/{project_id}/lyrics", data={"raw_text": lyrics})
    res.raise_for_status()
    print("Lyrics uploaded.")

    print("4. Triggering synchronization...")
    res = requests.post(f"{API_URL}/projects/{project_id}/synchronize")
    res.raise_for_status()
    print("Sync triggered. Polling...")

    is_done = False
    while not is_done:
        time.sleep(2)
        res = requests.get(f"{API_URL}/projects/{project_id}")
        data = res.json()
        status = data.get("status")
        progress = data.get("sync_progress", {})
        msg = progress.get("message", "")
        pct = progress.get("percent", 0)
        print(f"Status: {status} | Progress: {msg} ({pct}%)")
        if status in ["synchronized", "error"]:
            is_done = True
            print("Final data lines:")
            for line in data.get("lines", []):
                print(f"  [{line['start_ms']} - {line['end_ms']}] {line['display_text']}")

if __name__ == "__main__":
    test_workflow()
