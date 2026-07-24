import requests
import time
import json
import os
import sys

BASE_URL = "http://localhost:8005/api/v1"

def create_project(title):
    res = requests.post(f"{BASE_URL}/projects", json={"title": title})
    res.raise_for_status()
    return res.json()["project_id"]

def upload_audio(project_id, file_path):
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/projects/{project_id}/audio", files={"file": f})
        res.raise_for_status()

def upload_lyrics(project_id, file_path):
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/projects/{project_id}/lyrics", files={"file": f})
        res.raise_for_status()

def trigger_sync(project_id):
    res = requests.post(f"{BASE_URL}/projects/{project_id}/synchronize")
    res.raise_for_status()

def get_status(project_id):
    res = requests.get(f"{BASE_URL}/projects/{project_id}")
    res.raise_for_status()
    return res.json()

def main():
    print("Creating project...")
    project_id = create_project("test-sync-1")
    print(f"Project ID: {project_id}")
    
    print("Uploading audio...")
    upload_audio(project_id, "Bryan Adams - (Everything I Do) I Do It For You (Classic Version).mp4")
    
    print("Uploading lyrics...")
    upload_lyrics(project_id, "sample_lyrics.txt")
    
    print("Triggering sync...")
    trigger_sync(project_id)
    
    while True:
        status = get_status(project_id)
        if status["status"] == "synchronized":
            print("Sync complete!")
            print(json.dumps(status["sync_progress"], indent=2))
            break
        elif status["status"] == "error":
            print("Sync failed!")
            print(json.dumps(status["sync_progress"], indent=2))
            break
        else:
            prog = status.get("sync_progress", {})
            print(f"Status: {status['status']} - {prog.get('percent', 0)}% - {prog.get('message', '')}")
            time.sleep(2)
            
if __name__ == "__main__":
    main()
