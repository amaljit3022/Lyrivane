import sys
from pathlib import Path
sys.path.append(str(Path("c:/Worklab/amaljit/Lyrivane/apps/api")))

from services.alignment_service import AlignmentService

user_lines = [
    {"words": [{"display_text": "I"}, {"display_text": "remember"}]},
    {"words": [{"display_text": "when"}, {"display_text": "we"}, {"display_text": "were"}, {"display_text": "young"}]}
]

whisper_lines = [
    {"words": [{"display_text": "MUSIC", "start_ms": 0, "end_ms": 30000}]},
    {"words": [
        {"display_text": "Look", "start_ms": 30000, "end_ms": 31000},
        {"display_text": "into", "start_ms": 31000, "end_ms": 32000},
        {"display_text": "my", "start_ms": 32000, "end_ms": 33000},
        {"display_text": "eyes,", "start_ms": 33000, "end_ms": 34000},
        {"display_text": "young,", "start_ms": 34000, "end_ms": 35000}
    ]}
]

aligned = AlignmentService.align_user_lyrics_to_whisper(user_lines, whisper_lines)
import json
print(json.dumps(aligned, indent=2))
