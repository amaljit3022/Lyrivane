import re
import unicodedata
from typing import List, Tuple, Dict, Any, Optional
from schemas.project import LineTiming, WordTiming, SectionTiming, SectionType


class LyricsService:
    @staticmethod
    def normalize_text_for_alignment(text: str) -> str:
        """
        Normalize text for phonetic audio alignment:
        - Lowercase
        - Strip punctuation (keep spaces)
        - Normalize Unicode characters (accents to ASCII base where applicable)
        - Remove duplicate spaces
        """
        # Convert unicode characters to canonical decomposition
        text = unicodedata.normalize("NFKD", text)

        # Lowercase
        text = text.lower()

        # Replace hyphens/dashes with spaces
        text = re.sub(r"[\-\—\–]", " ", text)

        # Strip all punctuation except spaces and letters/digits
        text = re.sub(r"[^\w\s]", "", text)

        # Collapse multi-spaces
        text = re.sub(r"\s+", " ", text).strip()

        return text

    @staticmethod
    def parse_lrc(lrc_content: str) -> List[Dict[str, Any]]:
        """
        Parse LRC format lines like:
        [00:12.42]I remember when we were young
        Returns list of parsed dicts: [{start_ms, display_text}]
        """
        lrc_regex = re.compile(r"\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)")
        parsed_lines = []

        for line in lrc_content.splitlines():
            match = lrc_regex.match(line.strip())
            if match:
                minutes, seconds, millis, text = match.groups()
                ms_multiplier = 10 if len(millis) == 2 else 1
                total_ms = (int(minutes) * 60 + int(seconds)) * 1000 + int(millis) * ms_multiplier
                display_text = text.strip()
                if display_text:
                    parsed_lines.append({
                        "start_ms": total_ms,
                        "display_text": display_text
                    })

        return parsed_lines

    @classmethod
    def process_raw_lyrics(
        cls,
        raw_text: str,
        total_duration_ms: int = 180000
    ) -> Tuple[List[SectionTiming], List[LineTiming]]:
        """
        Process raw lyrics (pasted or TXT file content) into display lines,
        alignment lines, word tokens, and automatic section markers.
        """
        raw_lines = raw_text.splitlines()
        sections: List[SectionTiming] = []
        lines: List[LineTiming] = []

        current_section = SectionTiming(
            type=SectionType.VERSE,
            display_label="Verse 1",
            start_ms=0,
            end_ms=total_duration_ms
        )
        sections.append(current_section)

        section_counter = {"verse": 1, "chorus": 1, "bridge": 1}

        # Header detection pattern e.g. [Verse 1], [Chorus], [Bridge]
        header_pattern = re.compile(r"^\[(Verse|Chorus|Bridge|Intro|Outro|Pre-Chorus)[\s\d]*\]$", re.IGNORECASE)

        for line in raw_lines:
            stripped = line.strip()

            if not stripped:
                continue

            # Check if this line is a section header
            header_match = header_pattern.match(stripped)
            if header_match:
                section_name = header_match.group(1).lower()
                sec_type = SectionType.OTHER
                if "verse" in section_name:
                    sec_type = SectionType.VERSE
                elif "chorus" in section_name:
                    sec_type = SectionType.CHORUS
                elif "bridge" in section_name:
                    sec_type = SectionType.BRIDGE
                elif "intro" in section_name:
                    sec_type = SectionType.INTRO
                elif "outro" in section_name:
                    sec_type = SectionType.OUTRO

                count = section_counter.get(section_name, 1)
                section_counter[section_name] = count + 1

                current_section = SectionTiming(
                    type=sec_type,
                    display_label=f"{header_match.group(1).capitalize()} {count}",
                    start_ms=0,
                    end_ms=total_duration_ms
                )
                sections.append(current_section)
                continue

            # Regular lyric line processing
            alignment_text = cls.normalize_text_for_alignment(stripped)
            if not alignment_text:
                continue

            # Generate word tokens
            words_raw = stripped.split()
            word_objects: List[WordTiming] = []
            for w in words_raw:
                norm_w = cls.normalize_text_for_alignment(w)
                if norm_w:
                    word_objects.append(WordTiming(
                        display_text=w,
                        alignment_text=norm_w,
                        start_ms=0,
                        end_ms=0,
                        confidence=1.0
                    ))

            line_obj = LineTiming(
                section_id=current_section.id,
                display_text=stripped,
                alignment_text=alignment_text,
                start_ms=0,
                end_ms=0,
                words=word_objects
            )
            lines.append(line_obj)
            
        # Distribute timings evenly as a baseline before alignment
        if lines:
            word_count = sum(len(line.words) for line in lines)
            ms_per_word = total_duration_ms // max(1, word_count)
            
            current_ms = 0
            for line in lines:
                if not line.words:
                    continue
                line.start_ms = current_ms
                for w in line.words:
                    w.start_ms = current_ms
                    w.end_ms = current_ms + ms_per_word
                    current_ms += ms_per_word
                line.end_ms = current_ms

        return sections, lines
