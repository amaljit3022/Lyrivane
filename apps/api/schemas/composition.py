from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# Lyrivane Composition Schema (Visual Grammar - Phase 3 Expanded)
# -------------------------------------------------------------------

class WordStyle(BaseModel):
    font_family: Optional[str] = Field(default=None, description="Font family override.")
    font_size_mult: float = Field(default=1.0, description="Size multiplier relative to base font size.")
    font_weight: int = Field(default=700, description="Font weight (e.g. 400, 700, 900).")
    color: Optional[str] = Field(default=None, description="CSS text color hex or rgb.")
    gradient: Optional[str] = Field(default=None, description="CSS gradient string (e.g. linear-gradient(...)).")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    rotation_deg: float = Field(default=0.0, description="Rotation angle in degrees.")
    letter_spacing_em: float = Field(default=0.0, description="Letter spacing in em units.")
    glow_color: Optional[str] = Field(default=None, description="CSS drop-shadow or text-shadow glow color.")
    stroke_color: Optional[str] = Field(default=None, description="Text stroke outline color.")
    stroke_width_px: float = Field(default=0.0, description="Text stroke outline width in pixels.")
    text_transform: Optional[str] = Field(default=None, description="uppercase, lowercase, capitalize, none")

class WordComposition(BaseModel):
    match: str = Field(description="The exact word text or ID from timeline.")
    display_text: Optional[str] = Field(default=None, description="Text to render.")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Semantic importance score.")
    style: WordStyle = Field(default_factory=WordStyle)
    enter_preset: str = Field(default="fade-up", description="Preset: fade, fade-up, scale-pop, blur-focus, slide-in, drop, cascade")
    active_preset: Optional[str] = Field(default=None, description="Preset: breathe, float, pulse, vibrate, wave, heartbeat, glow-pulse")
    exit_preset: str = Field(default="fade", description="Preset: fade, dissolve, blur, scatter, drop, shrink")
    semantic_action: Optional[str] = Field(default=None, description="Detected semantic rule: fall, rise, break, run, whisper, shout, fire, rain, heartbeat, alone, together")
    path: Optional[str] = Field(default=None, description="Movement trajectory: horizontal-drift, float-up, drop-down")
    particles: bool = Field(default=False, description="Enable particle dispersion or ambient particles.")

class LayoutConfig(BaseModel):
    type: str = Field(
        default="center", 
        description="Layout types: center, editorial-left, asymmetric-stack, scattered, vertical-stack, full-screen-keyword"
    )
    anchor: str = Field(default="center-center", description="Anchor positioning: top-left, center-center, bottom-center, etc.")
    max_line_width_percent: float = Field(default=85.0, description="Max width percentage of container.")
    row_gap_px: int = Field(default=20)
    word_gap_px: int = Field(default=16)

class CameraMotion(BaseModel):
    zoom_from: float = Field(default=1.0)
    zoom_to: float = Field(default=1.04)
    pan_x_from: float = Field(default=0.0)
    pan_x_to: float = Field(default=0.0)
    pan_y_from: float = Field(default=0.0)
    pan_y_to: float = Field(default=0.0)
    easing: str = Field(default="ease-in-out")

class SceneDefinition(BaseModel):
    duration: Literal["lyric", "section", "song"] = Field(default="lyric")
    background: str = Field(default="cinematic-dark", description="Background preset or hex color.")
    ambient_particles: bool = Field(default=False)
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(default="16:9")

class CompositionPlan(BaseModel):
    """
    Main layout & styling definition for a line or section of lyrics.
    """
    line_id: Optional[str] = None
    section_id: Optional[str] = None
    section_type: str = Field(default="verse", description="verse, chorus, intro, bridge, outro, etc.")
    scene: SceneDefinition = Field(default_factory=SceneDefinition)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    words: List[WordComposition] = Field(default_factory=list)
    camera: Optional[CameraMotion] = Field(default=None)

class VisualPlan(BaseModel):
    """
    Top-level visual configuration for the entire project.
    """
    mood: str = Field(default="nostalgic", description="nostalgic, high-energy, calm, dramatic, moody, cheerful")
    style: str = Field(default="editorial-motion", description="Template identifier.")
    palette: str = Field(default="default", description="Color palette key.")
    motion_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(default="16:9")
    line_plans: Dict[str, CompositionPlan] = Field(default_factory=dict, description="Line ID -> CompositionPlan map.")
