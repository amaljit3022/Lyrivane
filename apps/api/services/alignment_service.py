import re
from typing import List, Dict, Any
import difflib

class AlignmentService:
    @staticmethod
    def align_user_lyrics_to_whisper(user_lines: List[Dict[str, Any]], whisper_lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        user_words = []
        for line in user_lines:
            for w in line.get("words", []):
                w["_matched"] = False
                user_words.append(w)
                
        whisper_words = []
        for line in whisper_lines:
            for w in line.get("words", []):
                whisper_words.append(w)
                
        if not user_words or not whisper_words:
            return user_lines
            
        def clean_word(w: str) -> str:
            return re.sub(r'[^a-z0-9]', '', w.lower())
            
        u_texts = [clean_word(w.get("alignment_text", w.get("display_text", ""))) for w in user_words]
        w_texts = [clean_word(w.get("alignment_text", w.get("display_text", ""))) for w in whisper_words]
        
        matcher = difflib.SequenceMatcher(None, u_texts, w_texts)
        has_matches = False
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal' or tag == 'replace':
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    if tag == 'replace':
                        sim = difflib.SequenceMatcher(None, u_texts[i], w_texts[j]).ratio()
                        if sim < 0.5:
                            continue
                    user_words[i]["start_ms"] = whisper_words[j]["start_ms"]
                    user_words[i]["end_ms"] = whisper_words[j]["end_ms"]
                    user_words[i]["_matched"] = True
                    has_matches = True
                    
        if not has_matches:
            total_duration = whisper_words[-1]["end_ms"] if whisper_words else 180000
            word_duration = total_duration // max(1, len(user_words))
            for i, w in enumerate(user_words):
                w["start_ms"] = int(i * word_duration)
                w["end_ms"] = int((i + 1) * word_duration)
        else:
            first_match_idx = -1
            for i, w in enumerate(user_words):
                if w.get("_matched"):
                    first_match_idx = i
                    break
                    
            if first_match_idx > -1:
                first_start = user_words[first_match_idx]["start_ms"]
                curr_end = first_start
                for i in range(first_match_idx - 1, -1, -1):
                    user_words[i]["end_ms"] = curr_end
                    user_words[i]["start_ms"] = max(0, curr_end - 300)
                    curr_end = user_words[i]["start_ms"]
            
            last_end = user_words[first_match_idx]["end_ms"] if first_match_idx > -1 else 0
            i = max(0, first_match_idx)
            while i < len(user_words):
                if user_words[i].get("_matched"):
                    last_end = user_words[i]["end_ms"]
                    i += 1
                else:
                    next_match_idx = -1
                    next_start = last_end + 300 * (len(user_words) - i)
                    for j in range(i + 1, len(user_words)):
                        if user_words[j].get("_matched"):
                            next_match_idx = j
                            next_start = user_words[j]["start_ms"]
                            break
                    
                    unmatched_count = next_match_idx - i if next_match_idx != -1 else len(user_words) - i
                    available_gap = max(0, next_start - last_end)
                    
                    # Heuristic: Don't stretch a few words over a massive instrumental gap.
                    # Pack them into the beginning of the gap (assuming they were the end of a stanza that Whisper missed)
                    # Maximum 600ms per word allocation.
                    max_total_duration = unmatched_count * 600
                    actual_duration = min(available_gap, max_total_duration)
                    
                    step = actual_duration / max(1, unmatched_count)
                    
                    for j in range(unmatched_count):
                        w = user_words[i + j]
                        w["start_ms"] = int(last_end + j * step)
                        w["end_ms"] = int(w["start_ms"] + min(step * 0.8, 1000))
                    
                    last_end = user_words[i + unmatched_count - 1]["end_ms"]
                    i += unmatched_count
                    
        for w in user_words:
            w.pop("_matched", None)
            
        for line in user_lines:
            if line.get("words"):
                line["start_ms"] = int(line["words"][0]["start_ms"])
                line["end_ms"] = int(line["words"][-1]["end_ms"])
                # Sanity check: cap line duration to 15 seconds to avoid UI lingering on huge gaps
                if line["end_ms"] - line["start_ms"] > 15000:
                    line["end_ms"] = line["start_ms"] + 15000
                
        return user_lines
