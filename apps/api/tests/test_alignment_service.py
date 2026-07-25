from services.alignment_service import AlignmentService


def test_repeated_phrase_does_not_span_whisper_timestamp_jump():
    user_lines = [
        {
            "display_text": "I can't help it",
            "words": [
                {"display_text": "I", "alignment_text": "i"},
                {"display_text": "can't", "alignment_text": "cant"},
                {"display_text": "help", "alignment_text": "help"},
                {"display_text": "it", "alignment_text": "it"},
            ],
        },
        {
            "display_text": "There's nothin' I want more",
            "words": [
                {"display_text": "There's", "alignment_text": "theres"},
                {"display_text": "nothin'", "alignment_text": "nothin"},
                {"display_text": "I", "alignment_text": "i"},
                {"display_text": "want", "alignment_text": "want"},
                {"display_text": "more", "alignment_text": "more"},
            ],
        },
    ]
    whisper_lines = [
        {
            "words": [
                {"text": "I", "start": 200.34, "end": 200.68},
                {"text": "can't", "start": 200.68, "end": 201.34},
                {"text": "help", "start": 201.34, "end": 202.04},
                {"text": "it", "start": 202.04, "end": 202.46},
                {"text": "there's", "start": 202.84, "end": 203.10},
                {"text": "nothing", "start": 203.10, "end": 203.72},
                {"text": "I", "start": 203.72, "end": 204.36},
                {"text": "want", "start": 346.06, "end": 346.56},
                {"text": "more", "start": 346.56, "end": 347.28},
            ]
        }
    ]

    aligned = AlignmentService.align_user_lyrics_to_whisper(user_lines, whisper_lines)
    line = aligned[1]

    assert line["end_ms"] - line["start_ms"] <= 15000
    assert line["words"][-1]["end_ms"] < 210000
    assert all(
        left["end_ms"] <= right["start_ms"]
        for left, right in zip(line["words"], line["words"][1:])
    )


def test_repair_whisper_timestamps_compacts_impossible_segment_gap():
    repaired = AlignmentService.repair_whisper_timestamps([
        {
            "start_ms": 280000,
            "end_ms": 336790,
            "words": [
                {"text": "So", "start": 280.06, "end": 280.34},
                {"text": "you", "start": 280.34, "end": 280.59},
                {"text": "can't", "start": 334.32, "end": 335.60},
                {"text": "tell", "start": 335.60, "end": 336.26},
                {"text": "me", "start": 336.26, "end": 336.79},
            ],
        }
    ])

    words = repaired[0]["words"]
    assert words[-1]["end_ms"] - words[0]["start_ms"] < 5000
    assert repaired[0]["end_ms"] == words[-1]["end_ms"]
