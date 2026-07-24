import re
from typing import List, Dict, Any, Optional
from schemas.project import CanonicalTimeline, LineTiming, WordTiming
from schemas.composition import (
    VisualPlan, CompositionPlan, SceneDefinition, LayoutConfig, 
    WordComposition, WordStyle, CameraMotion
)

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "or", "but", "if", "so", "my", "your"
}

SEMANTIC_RULES = {
    "fall": {"preset": "drop", "action": "fall", "path": "drop-down"},
    "falling": {"preset": "drop", "action": "fall", "path": "drop-down"},
    "down": {"preset": "drop", "action": "fall", "path": "drop-down"},
    "drop": {"preset": "drop", "action": "fall", "path": "drop-down"},
    "rise": {"preset": "scale-pop", "action": "rise", "path": "float-up"},
    "rising": {"preset": "scale-pop", "action": "rise", "path": "float-up"},
    "fly": {"preset": "slide-in", "action": "rise", "path": "float-up"},
    "sky": {"preset": "fade-up", "action": "rise", "path": "float-up"},
    "high": {"preset": "scale-pop", "action": "rise", "path": "float-up"},
    "break": {"preset": "cascade", "action": "break", "active": "vibrate"},
    "shatter": {"preset": "cascade", "action": "break", "active": "vibrate"},
    "broken": {"preset": "cascade", "action": "break", "active": "vibrate"},
    "run": {"preset": "slide-in", "action": "run", "path": "horizontal-drift"},
    "running": {"preset": "slide-in", "action": "run", "path": "horizontal-drift"},
    "fast": {"preset": "slide-in", "action": "run", "path": "horizontal-drift"},
    "whisper": {"preset": "fade", "action": "whisper", "active": "breathe"},
    "soft": {"preset": "fade", "action": "whisper", "active": "breathe"},
    "quiet": {"preset": "fade", "action": "whisper", "active": "breathe"},
    "shout": {"preset": "scale-pop", "action": "shout", "active": "glow-pulse"},
    "loud": {"preset": "scale-pop", "action": "shout", "active": "glow-pulse"},
    "scream": {"preset": "scale-pop", "action": "shout", "active": "vibrate"},
    "fire": {"preset": "scale-pop", "action": "fire", "active": "glow-pulse", "color": "#ff5722"},
    "flame": {"preset": "scale-pop", "action": "fire", "active": "glow-pulse", "color": "#ff9800"},
    "burn": {"preset": "fade-up", "action": "fire", "active": "glow-pulse", "color": "#ff5722"},
    "rain": {"preset": "drop", "action": "rain", "particles": True, "color": "#00bcd4"},
    "storm": {"preset": "cascade", "action": "rain", "particles": True, "color": "#009688"},
    "heart": {"preset": "scale-pop", "action": "heartbeat", "active": "heartbeat", "color": "#e91e63"},
    "heartbeat": {"preset": "scale-pop", "action": "heartbeat", "active": "heartbeat", "color": "#e91e63"},
    "love": {"preset": "blur-focus", "action": "heartbeat", "active": "breathe", "color": "#f44336"},
    "alone": {"preset": "blur-focus", "action": "alone", "layout": "full-screen-keyword"},
    "together": {"preset": "cascade", "action": "together", "active": "pulse"},
}

COLOR_PALETTES = {
    "default": {"accent": "#f39c12", "text": "#ffffff", "subtext": "#b0bec5"},
    "editorial": {"accent": "#e63946", "text": "#f1faee", "subtext": "#a8dadc"},
    "cinematic": {"accent": "#ffb703", "text": "#fb8500", "subtext": "#8ecae6"},
    "neon": {"accent": "#00f5d4", "text": "#7b2cbf", "subtext": "#f15bb5"}
}

class VisualIntelligenceService:
    """
    Analyzes lyrics, timeline structure, and section dynamics to generate section-aware storyboards.
    """

    @classmethod
    def analyze_word_importance(cls, word_text: str) -> float:
        clean = re.sub(r'[^\w]', '', word_text.lower())
        if not clean:
            return 0.5
        if clean in STOP_WORDS:
            return 0.3
        if clean in SEMANTIC_RULES:
            return 0.95
        length_score = min(1.0, len(clean) / 8.0)
        return max(0.5, length_score)

    @classmethod
    def classify_line_section(
        cls, 
        line_idx: int, 
        total_lines: int, 
        line_text: str, 
        line_counts: Dict[str, int]
    ) -> str:
        if total_lines == 0:
            return "verse"
        
        ratio = line_idx / max(1, total_lines)
        clean_text = re.sub(r'[^\w\s]', '', line_text.lower()).strip()
        is_repeated = line_counts.get(clean_text, 0) > 1

        if ratio <= 0.08:
            return "intro"
        elif ratio >= 0.92:
            return "outro"
        elif 0.35 <= ratio <= 0.60 and is_repeated:
            return "chorus"
        elif 0.75 <= ratio <= 0.90 and is_repeated:
            return "final_chorus"
        elif 0.25 <= ratio < 0.35:
            return "pre_chorus"
        elif 0.60 <= ratio < 0.75:
            return "bridge"
        else:
            return "verse"

    @classmethod
    def generate_word_composition(
        cls, 
        word: WordTiming, 
        section_type: str = "verse",
        palette_key: str = "default",
        motion_intensity: float = 0.5
    ) -> WordComposition:
        raw_text = word.display_text
        clean = re.sub(r'[^\w]', '', raw_text.lower())
        importance = cls.analyze_word_importance(raw_text)

        palette = COLOR_PALETTES.get(palette_key, COLOR_PALETTES["default"])
        
        style = WordStyle(
            font_size_mult=1.0,
            font_weight=700 if importance > 0.6 else 400,
            opacity=1.0 if importance > 0.4 else 0.75
        )

        enter_preset = "fade-up"
        active_preset = None
        exit_preset = "fade"
        semantic_action = None
        path = None
        particles = False

        # Section-specific default preset overrides
        if section_type in ["chorus", "final_chorus"]:
            enter_preset = "scale-pop"
            active_preset = "glow-pulse"
            style.font_size_mult *= 1.25
        elif section_type == "pre_chorus":
            enter_preset = "slide-in"
        elif section_type == "bridge":
            enter_preset = "blur-focus"
            active_preset = "breathe"

        # Apply semantic rule if matched
        if clean in SEMANTIC_RULES:
            rule = SEMANTIC_RULES[clean]
            semantic_action = rule.get("action")
            enter_preset = rule.get("preset", enter_preset)
            if "active" in rule:
                active_preset = rule["active"]
            if "path" in rule:
                path = rule["path"]
            if rule.get("particles"):
                particles = True
            if "color" in rule:
                style.color = rule["color"]

        # High importance word styling
        if importance >= 0.8:
            multiplier = 1.8 if section_type in ["chorus", "final_chorus"] else 1.5
            style.font_size_mult = multiplier + (importance - 0.8) * 2.0
            style.font_weight = 900
            style.text_transform = "uppercase"
            if not style.color:
                style.color = palette["accent"]
            style.glow_color = style.color
            if not enter_preset or enter_preset == "fade-up":
                enter_preset = "scale-pop"
        elif importance <= 0.35:
            style.font_size_mult = 0.8
            style.color = palette["subtext"]

        return WordComposition(
            match=word.alignment_text or word.display_text,
            display_text=raw_text,
            importance=importance,
            style=style,
            enter_preset=enter_preset,
            active_preset=active_preset,
            exit_preset=exit_preset,
            semantic_action=semantic_action,
            path=path,
            particles=particles
        )

    @classmethod
    def generate_visual_plan(
        cls, 
        timeline: CanonicalTimeline, 
        style: str = "editorial-motion",
        palette: str = "default",
        aspect_ratio: str = "16:9",
        motion_intensity: float = 0.5
    ) -> VisualPlan:
        line_plans: Dict[str, CompositionPlan] = {}

        # Count line frequencies to identify repeated choruses
        line_counts: Dict[str, int] = {}
        for line in timeline.lines:
            clean_t = re.sub(r'[^\w\s]', '', line.display_text.lower()).strip()
            line_counts[clean_t] = line_counts.get(clean_t, 0) + 1

        total_lines = len(timeline.lines)
        max_line_width = 85.0
        if aspect_ratio == "9:16":
            max_line_width = 92.0
        elif aspect_ratio == "1:1":
            max_line_width = 88.0

        overall_max_importance = 0.0
        for line_idx, line in enumerate(timeline.lines):
            section_type = cls.classify_line_section(line_idx, total_lines, line.display_text, line_counts)
            word_comps: List[WordComposition] = []
            max_line_importance = 0.0

            for word in line.words:
                w_comp = cls.generate_word_composition(
                    word, 
                    section_type=section_type, 
                    palette_key=palette, 
                    motion_intensity=motion_intensity
                )
                word_comps.append(w_comp)
                if w_comp.importance > max_line_importance:
                    max_line_importance = w_comp.importance

            if max_line_importance > overall_max_importance:
                overall_max_importance = max_line_importance

            # Determine section-aware layout type
            if section_type in ["chorus", "final_chorus"]:
                layout_type = "full-screen-keyword" if len(line.words) <= 3 else "scattered"
            elif section_type == "pre_chorus":
                layout_type = "asymmetric-stack"
            elif section_type == "bridge":
                layout_type = "vertical-stack"
            elif line_idx % 3 == 1:
                layout_type = "editorial-left"
            else:
                layout_type = "center"

            layout_config = LayoutConfig(
                type=layout_type,
                anchor="center-center",
                max_line_width_percent=max_line_width,
                row_gap_px=24 if aspect_ratio == "9:16" else 20,
                word_gap_px=18
            )

            background = "cinematic-dark"
            if section_type == "bridge":
                background = "#070b19"
            elif section_type in ["chorus", "final_chorus"]:
                background = "#0f051d"

            scene_def = SceneDefinition(
                duration="lyric",
                background=background,
                aspect_ratio=aspect_ratio  # type: ignore
            )

            plan = CompositionPlan(
                line_id=line.id,
                section_type=section_type,
                scene=scene_def,
                layout=layout_config,
                words=word_comps,
                camera=CameraMotion(zoom_from=1.0, zoom_to=1.08 if section_type in ["chorus", "final_chorus"] else 1.04)
            )
            line_plans[line.id] = plan

        return VisualPlan(
            mood="dramatic" if overall_max_importance > 0.8 else "nostalgic",
            style=style,
            palette=palette,
            motion_intensity=motion_intensity,
            aspect_ratio=aspect_ratio, # type: ignore
            line_plans=line_plans
        )
