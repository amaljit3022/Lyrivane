import copy
import difflib
import re
from typing import List, Dict, Any


class AlignmentService:
    """Map user-preserved lyric text onto ASR timestamps safely."""

    MAX_WORD_DURATION_MS = 5000
    MAX_INTRA_SEGMENT_GAP_MS = 4000
    MAX_INTRA_LINE_GAP_MS = 8000
    MAX_LINE_DURATION_MS = 15000
    SYNTHETIC_WORD_GAP_MS = 250

    @classmethod
    def repair_whisper_timestamps(cls, whisper_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Repair impossible word gaps while preserving ASR word order."""
        repaired_lines: List[Dict[str, Any]] = []

        for raw_line in whisper_lines or []:
            line = copy.deepcopy(raw_line)
            repaired_words: List[Dict[str, Any]] = []
            timestamp_shift = 0
            previous_end = None

            for raw_word in raw_line.get("words", []):
                text = str(raw_word.get("text", raw_word.get("display_text", ""))).strip()
                if not text:
                    continue

                try:
                    if "start_ms" in raw_word or "end_ms" in raw_word:
                        start_ms = max(0, int(raw_word["start_ms"]))
                        end_ms = max(0, int(raw_word["end_ms"]))
                    else:
                        start_ms = max(0, int(float(raw_word["start"]) * 1000))
                        end_ms = max(0, int(float(raw_word["end"]) * 1000))
                except (KeyError, TypeError, ValueError):
                    continue

                start_ms += timestamp_shift
                end_ms += timestamp_shift

                if previous_end is not None:
                    gap_ms = start_ms - previous_end
                    if gap_ms > cls.MAX_INTRA_SEGMENT_GAP_MS:
                        timestamp_shift -= gap_ms - cls.SYNTHETIC_WORD_GAP_MS
                        start_ms -= gap_ms - cls.SYNTHETIC_WORD_GAP_MS
                        end_ms -= gap_ms - cls.SYNTHETIC_WORD_GAP_MS
                    start_ms = max(start_ms, previous_end)

                duration_ms = max(40, min(end_ms - start_ms, cls.MAX_WORD_DURATION_MS))
                end_ms = start_ms + duration_ms

                word = dict(raw_word)
                word["text"] = text
                word["start_ms"] = start_ms
                word["end_ms"] = end_ms
                repaired_words.append(word)
                previous_end = end_ms

            if repaired_words:
                line["words"] = repaired_words
                line["start_ms"] = repaired_words[0]["start_ms"]
                line["end_ms"] = repaired_words[-1]["end_ms"]
                repaired_lines.append(line)

        return repaired_lines

    @staticmethod
    def align_user_lyrics_to_whisper(
        user_lines: List[Dict[str, Any]],
        whisper_lines: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        user_words = []
        user_word_lines: List[int] = []

        for line_idx, line in enumerate(user_lines):
            for word in line.get("words", []):
                word["_matched"] = False
                user_words.append(word)
                user_word_lines.append(line_idx)

        whisper_lines = AlignmentService.repair_whisper_timestamps(whisper_lines)
        whisper_words = []
        for line in whisper_lines:
            whisper_words.extend(line.get("words", []))

        if not user_words or not whisper_words:
            return user_lines

        def clean_word(word: str) -> str:
            return re.sub(r"[^a-z0-9]", "", word.lower())

        whisper_texts = [
            clean_word(word.get("alignment_text", word.get("display_text", word.get("text", ""))))
            for word in whisper_words
        ]

        user_texts = [
            clean_word(word.get("alignment_text", word.get("display_text", "")))
            for word in user_words
        ]

        # Global monotonic alignment is used instead of independent fuzzy line
        # searches. It keeps the supplied lyric order, permits Whisper to omit
        # low-energy words, and makes skipping a later repeated chorus costly.
        rows = len(user_texts) + 1
        cols = len(whisper_texts) + 1
        scores = [[0.0] * cols for _ in range(rows)]
        moves = [["skip_user"] * cols for _ in range(rows)]
        for i in range(1, rows):
            scores[i][0] = scores[i - 1][0] - 1.2
        for j in range(1, cols):
            scores[0][j] = scores[0][j - 1] - 0.35

        for i in range(1, rows):
            for j in range(1, cols):
                similarity = difflib.SequenceMatcher(None, user_texts[i - 1], whisper_texts[j - 1]).ratio()
                match_score = 3.0 if user_texts[i - 1] == whisper_texts[j - 1] else (1.4 if similarity >= 0.5 else -2.0)
                options = {
                    "match": scores[i - 1][j - 1] + match_score,
                    "skip_user": scores[i - 1][j] - 1.2,
                    "skip_whisper": scores[i][j - 1] - 0.35,
                }
                moves[i][j] = max(options, key=options.get)
                scores[i][j] = options[moves[i][j]]

        i, j = len(user_texts), len(whisper_texts)
        accepted_matches = []
        while i > 0 and j > 0:
            move = moves[i][j]
            if move == "match":
                similarity = difflib.SequenceMatcher(None, user_texts[i - 1], whisper_texts[j - 1]).ratio()
                if user_texts[i - 1] == whisper_texts[j - 1] or similarity >= 0.5:
                    accepted_matches.append((i - 1, j - 1))
                i -= 1
                j -= 1
            elif move == "skip_user":
                i -= 1
            else:
                j -= 1
        accepted_matches.reverse()

        for user_idx, whisper_idx in accepted_matches:
            user_words[user_idx]["start_ms"] = whisper_words[whisper_idx]["start_ms"]
            user_words[user_idx]["end_ms"] = whisper_words[whisper_idx]["end_ms"]
            user_words[user_idx]["_matched"] = True

        first_match_idx = next((i for i, word in enumerate(user_words) if word.get("_matched")), -1)
        if first_match_idx < 0:
            total_duration = whisper_words[-1]["end_ms"]
            word_duration = total_duration // max(1, len(user_words))
            for index, word in enumerate(user_words):
                word["start_ms"] = int(index * word_duration)
                word["end_ms"] = int((index + 1) * word_duration)
        else:
            cursor = user_words[first_match_idx]["start_ms"]
            for index in range(first_match_idx - 1, -1, -1):
                user_words[index]["end_ms"] = cursor
                user_words[index]["start_ms"] = max(0, cursor - 300)
                cursor = user_words[index]["start_ms"]

            for index, word in enumerate(user_words):
                if word.get("_matched"):
                    cursor = word["end_ms"]
                    continue
                next_match = next((candidate for candidate in user_words[index + 1:] if candidate.get("_matched")), None)
                next_start = next_match["start_ms"] if next_match else cursor + 600
                word["start_ms"] = cursor
                word["end_ms"] = max(cursor + 40, min(next_start, cursor + 1000))
                cursor = word["end_ms"]

        for word in user_words:
            word.pop("_matched", None)

        # Enforce monotonic, bounded word timing. This is deliberately applied
        # to the words, not only the line end, so a renderer cannot inherit an
        # invisible outlier word.
        for line in user_lines:
            if not line.get("words"):
                continue

            line_start = max(0, int(line["words"][0].get("start_ms", 0)))
            cursor = line_start
            line_limit = line_start + AlignmentService.MAX_LINE_DURATION_MS

            for word in line["words"]:
                raw_start = max(0, int(word.get("start_ms", cursor)))
                raw_end = max(raw_start + 40, int(word.get("end_ms", raw_start + 40)))
                duration = max(
                    40,
                    min(raw_end - raw_start, AlignmentService.MAX_WORD_DURATION_MS),
                )
                word_start = max(cursor, raw_start)

                if word_start - cursor > AlignmentService.MAX_INTRA_LINE_GAP_MS:
                    word_start = cursor + AlignmentService.SYNTHETIC_WORD_GAP_MS

                word_start = min(word_start, line_limit - 40)
                word_end = min(word_start + duration, line_limit)
                if word_end <= word_start:
                    word_end = min(word_start + 40, line_limit)

                word["start_ms"] = word_start
                word["end_ms"] = word_end
                cursor = word_end

            line["start_ms"] = int(line["words"][0]["start_ms"])
            line["end_ms"] = int(line["words"][-1]["end_ms"])

        return user_lines
