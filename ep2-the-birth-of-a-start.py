# Logic in Motion Ep.02 The Birth of a Star 14s

# Youtube:
# https://youtube.com/shorts/muV9ty3UkDw?feature=share

"""
Scenes:

	Scene 0  Collection cover  2s
	Scene 1  Split studio code editor + live preview  7s
	Scene 2  Zoom transition studio → full canvas  0.5s
	Scene 3  Star draw (finishes when last stroke lands)  2.5s
	Scene 4  End card Code in github  2s
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image

from lib.audio_studio import render_episode_audio
from lib.canvas import TurtleCanvas
from lib.code_panel import draw_code_editor_panel
from lib.pipeline import encode, local_t, render_all, scene_at
from lib.settings import CACHE, FPS, GITHUB_REPO_URL, OUTPUT
from lib.studio_design import (
    composite_preview_panel,
    draw_studio_end_card,
    load_studio_background,
    render_collection_cover,
)
from lib.types import EpisodeConfig, StrokeEvent

# 1. SETTINGS
EPISODE_NUM = 2
EPISODE_TITLE = "The Birth of a Star"
GITHUB_CTA = "Code in github"
SLUG = "02_intersecting_star"

DUR = {0: 2.0, 1: 7.0, 2: 0.5, 3: 2.5, 4: 2.0}
SCENE_START: dict[int, float] = {}
_t = 0.0
for _s in sorted(DUR):
    SCENE_START[_s] = _t
    _t += DUR[_s]
TOTAL_DUR = _t
TOTAL_FRAMES = int(TOTAL_DUR * FPS)

FRAME_DIR = CACHE / f"turtle_{SLUG}_frames"
AUDIO_PATH = CACHE / f"turtle_{SLUG}_audio.wav"
VIDEO_PATH = OUTPUT / "turtle_02_intersecting_star.mp4"

CODE_LINES = [
    "import math, turtle",
    "",
    "def polygon(n, r, rot):",
    "    pts = []",
    "    for i in range(n):",
    "        a = math.radians(rot + i * 360 / n)",
    "        pts.append((r * math.cos(a), r * math.sin(a)))",
    "    for i in range(n):",
    "        turtle.goto(pts[i])",
    "        turtle.pendown()",
    "        turtle.goto(pts[(i + 1) % n])",
    "        turtle.penup()",
    "",
    "for layer in range(8):",
    "    polygon(12, 195 - layer * 7, layer * 7.5)",
]

# 2. DATA Intersecting star layers 
COORD_SCALE = 2.55
SIDES = 12
LAYERS = 8
OUTER_RADIUS = 195
RADIUS_STEP = 7
ROTATION_STEP = 7.5
STAR_SKIP = 5
EDGE_WIDTH = 2.8
DIAG_WIDTH = 1.8

_BG = load_studio_background()
_CANVAS = TurtleCanvas()
_CANVAS.set_background(_BG)
_STROKE_EVENTS: list[StrokeEvent] = []


# 3. DRAW
def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
    h = h % 360.0
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def polygon_points(n: int, radius: float, rotation_deg: float) -> list[tuple[float, float]]:
    return [
        (
            radius * math.cos(math.radians(rotation_deg + i * 360 / n)),
            radius * math.sin(math.radians(rotation_deg + i * 360 / n)),
        )
        for i in range(n)
    ]


def build_intersecting_star(canvas: TurtleCanvas) -> list[int]:
    marks: list[int] = []

    canvas.clear_strokes()
    canvas.set_view(origin_y_frac=0.52, coord_scale=COORD_SCALE)
    canvas.penup()

    for layer in range(LAYERS):
        radius = OUTER_RADIUS - layer * RADIUS_STEP
        rotation = layer * ROTATION_STEP
        pts = polygon_points(SIDES, radius, rotation)
        hue_base = 38 + layer * 14

        canvas.pensize(EDGE_WIDTH)
        for i in range(SIDES):
            canvas.pencolor(rgb_hex(hsv_to_rgb(hue_base + i * 4, 0.88, 1.0)))
            canvas.goto(pts[i][0], pts[i][1])
            canvas.pendown()
            nxt = (i + 1) % SIDES
            canvas.goto(pts[nxt][0], pts[nxt][1])
            canvas.penup()
            marks.append(canvas.stroke_count)

        canvas.pensize(DIAG_WIDTH)
        for i in range(SIDES):
            canvas.pencolor(rgb_hex(hsv_to_rgb(hue_base + 180 + i * 5, 0.75, 0.95)))
            canvas.goto(pts[i][0], pts[i][1])
            canvas.pendown()
            skip = (i + STAR_SKIP) % SIDES
            canvas.goto(pts[skip][0], pts[skip][1])
            canvas.penup()
            marks.append(canvas.stroke_count)

    canvas.goto(0, 0)
    canvas.pensize(12)
    canvas.dot(16, "#FFF8E7")
    canvas.dot(8, "#FFD54F")
    marks.append(canvas.stroke_count)

    return marks


# 4. TIMELINE
def build_timeline(marks: list[int]) -> list[StrokeEvent]:
    if not marks:
        return []

    draw_start = SCENE_START[1]
    draw_end = SCENE_START[3] + DUR[3]
    draw_dur = draw_end - draw_start
    events = [
        StrokeEvent(t=draw_start + (i / max(len(marks) - 1, 1)) * draw_dur, stroke_index=c)
        for i, c in enumerate(marks)
    ]
    if events:
        events[-1] = StrokeEvent(t=draw_end, stroke_index=marks[-1])
    return events


def init_drawing() -> None:
    global _STROKE_EVENTS, _BG, _CANVAS

    _BG = load_studio_background()
    _CANVAS = TurtleCanvas()
    _CANVAS.set_background(_BG)

    marks = build_intersecting_star(_CANVAS)
    _STROKE_EVENTS = build_timeline(marks)
    print(f"  design: Intersecting Star · strokes: {len(marks)} · layers: {LAYERS}")


def visible_at(t: float) -> int:
    count = 0
    for ev in _STROKE_EVENTS:
        if t >= ev.t:
            count = ev.stroke_index
    return max(0, count)


def art_glow(t: float) -> Image.Image:
    return _CANVAS.snapshot(visible_strokes=visible_at(t), glow=True)


# 5. SCENE RENDERERS 
def render_studio_intro(lt: float) -> Image.Image:
    editor = draw_code_editor_panel(
        _BG.copy(),
        lt,
        DUR[1],
        code_lines=CODE_LINES,
        title="star.py",
    )
    preview = _CANVAS.snapshot(visible_strokes=visible_at(SCENE_START[1] + lt), glow=True)
    return composite_preview_panel(editor, preview)


def render_transition(lt: float) -> Image.Image:
    p = min(1.0, lt / max(DUR[2], 0.01))
    studio = render_studio_intro(DUR[1])
    full = art_glow(SCENE_START[2] + lt)
    return Image.blend(studio, full, p)


def render_frame(fi: int) -> Image.Image:
    t = fi / FPS
    sc = scene_at(t, DUR)
    lt = local_t(t, sc, SCENE_START)

    if sc == 0:
        return render_collection_cover(
            lt, DUR[0], episode_num=EPISODE_NUM, episode_title=EPISODE_TITLE
        )

    if sc == 1:
        return render_studio_intro(lt)

    if sc == 2:
        return render_transition(lt)

    if sc == 3:
        return art_glow(t)

    progress = min(1.0, lt / max(DUR[4] * 0.5, 0.01))
    return draw_studio_end_card(
        _CANVAS.snapshot(glow=True),
        GITHUB_CTA,
        progress=progress,
        headline="",
        title_upper=False,
        repo_url=GITHUB_REPO_URL,
    )


# 6. AUDIO

def build_audio() -> None:
    render_episode_audio(TOTAL_DUR, AUDIO_PATH)


# 7. RENDER + ENCODE 

def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    print(f"Logic in Motion Ep.02 Birth of a Star {TOTAL_DUR:.1f}s · {TOTAL_FRAMES} frames")
    init_drawing()
    config = EpisodeConfig(
        slug=SLUG,
        dur=DUR,
        frame_dir=FRAME_DIR,
        audio_path=AUDIO_PATH,
        video_path=VIDEO_PATH,
        render_frame_fn=render_frame,
        stroke_events=_STROKE_EVENTS,
    )
    build_audio()
    render_all(config)
    encode(config)


if __name__ == "__main__":
    main()
