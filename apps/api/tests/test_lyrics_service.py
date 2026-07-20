import pytest
from services.lyrics_service import LyricsService


def test_normalize_text_for_alignment():
    raw = "I remember when we were young, & happy! — 2026"
    normalized = LyricsService.normalize_text_for_alignment(raw)
    assert normalized == "i remember when we were young happy 2026"


def test_process_raw_lyrics_with_sections():
    raw_lyrics = """
[Verse 1]
I remember when we were young
Walking under golden stars

[Chorus]
Let every word move with the music
Feel the energy tonight
"""
    sections, lines = LyricsService.process_raw_lyrics(raw_lyrics)

    assert len(sections) == 3  # Initial Verse + Verse 1 header + Chorus header
    assert len(lines) == 4

    assert lines[0].display_text == "I remember when we were young"
    assert lines[0].alignment_text == "i remember when we were young"
    assert len(lines[0].words) == 6
    assert lines[0].words[0].display_text == "I"
    assert lines[0].words[0].alignment_text == "i"


def test_lrc_parsing():
    lrc_data = """
[00:12.42]I remember when we were young
[00:16.85]Walking under golden stars
"""
    parsed = LyricsService.parse_lrc(lrc_data)
    assert len(parsed) == 2
    assert parsed[0]["start_ms"] == 12420
    assert parsed[0]["display_text"] == "I remember when we were young"
    assert parsed[1]["start_ms"] == 16850
