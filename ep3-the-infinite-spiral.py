# Logic in Motion Ep.03 The Infinite Spiral 14s

# Youtube:
# https://youtube.com/shorts/KaiHLk4cb4Y?feature=share

"""
Scenes:

	Scene 0  Collection cover  2s
	Scene 1  Split studio code editor + live preview  7s
	Scene 2  Zoom transition studio → full canvas  0.5s
	Scene 3  Golden spiral draw (finishes when last stroke lands)  2.5s
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
EPISODE_NUM = 3
EPISODE_TITLE = "The Infinite Spiral"
GITHUB_CTA = "Code in github"
SLUG = "03_golden_spiral"

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
VIDEO_PATH = OUTPUT / "turtle_03_golden_spiral.mp4"

CODE_LINES = [
    "import math, turtle",
    "",
    "PHI = 1.618",
    "TURNS = 6",
    "",
    "def golden_spiral(a, turns, n):",
    "    for i in range(n):",
    "        t = i / n * turns * 2 * math.pi",
    "        r = a * PHI ** (t / (2 * math.pi))",
    "        x = r * math.cos(t)",
    "        y = r * math.sin(t)",
    "        turtle.goto(x, y)",
    "",
    "golden_spiral(5, TURNS, 240)",
]

# 2. DATA Golden ratio nautilus shell 

COORD_SCALE = 2.45
PHI = 1.618
TURNS = 6
START_R = 5.0
SPIRAL_STEPS = 240
SPIRAL_WIDTH = 4.2
INNER_WIDTH = 2.4
CHAMBERS = 14
CHAMBER_WIDTH = 1.6
OUTER_RIM_STEPS = 48

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


def spiral_point(a: float, theta: float) -> tuple[float, float]:
    r = a * PHI ** (theta / (2 * math.pi))
    return r * math.cos(theta), r * math.sin(theta)


def build_golden_spiral(canvas: TurtleCanvas) -> list[int]:
    marks: list[int] = []

    canvas.clear_strokes()
    canvas.set_view(origin_y_frac=0.54, coord_scale=COORD_SCALE)
    canvas.penup()

    max_theta = TURNS * 2 * math.pi
    points = [
        spiral_point(START_R, (step / SPIRAL_STEPS) * max_theta)
        for step in range(SPIRAL_STEPS + 1)
    ]

    canvas.pensize(SPIRAL_WIDTH)
    prev: tuple[float, float] | None = None
    for step, (x, y) in enumerate(points):
        progress = step / max(SPIRAL_STEPS, 1)
        hue = 18 + progress * 42
        sat = 0.82 + 0.12 * (1 - progress * 0.5)
        val = 0.92 + 0.08 * progress
        canvas.pencolor(rgb_hex(hsv_to_rgb(hue, sat, val)))
        if prev is None:
            canvas.goto(x, y)
            prev = (x, y)
            continue
        canvas.pendown()
        canvas.goto(x, y)
        canvas.penup()
        marks.append(canvas.stroke_count)
        prev = (x, y)

    inner_a = START_R * 0.62
    inner_steps = int(SPIRAL_STEPS * 0.78)
    inner_points = [
        spiral_point(inner_a, (step / inner_steps) * max_theta * 0.88)
        for step in range(inner_steps + 1)
    ]

    canvas.pensize(INNER_WIDTH)
    prev = None
    for step, (x, y) in enumerate(inner_points):
        progress = step / max(inner_steps, 1)
        hue = 350 - progress * 28
        canvas.pencolor(rgb_hex(hsv_to_rgb(hue, 0.65, 0.88)))
        if prev is None:
            canvas.goto(x, y)
            prev = (x, y)
            continue
        canvas.pendown()
        canvas.goto(x, y)
        canvas.penup()
        marks.append(canvas.stroke_count)
        prev = (x, y)

    canvas.pensize(CHAMBER_WIDTH)
    for chamber in range(CHAMBERS):
        theta = (chamber / CHAMBERS) * max_theta * 0.95
        x, y = spiral_point(START_R * 0.15, theta)
        hue = 32 + chamber * 3.5
        canvas.pencolor(rgb_hex(hsv_to_rgb(hue, 0.55, 0.75)))
        canvas.goto(0, 0)
        canvas.pendown()
        canvas.goto(x, y)
        canvas.penup()
        marks.append(canvas.stroke_count)

    outer_theta_end = max_theta
    outer_theta_start = max_theta - (2 * math.pi / TURNS) * 0.85
    canvas.pensize(3.0)
    for step in range(OUTER_RIM_STEPS + 1):
        frac = step / OUTER_RIM_STEPS
        theta = outer_theta_start + frac * (outer_theta_end - outer_theta_start)
        r = START_R * PHI ** (theta / (2 * math.pi)) * 1.04
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        hue = 45 + frac * 18
        canvas.pencolor(rgb_hex(hsv_to_rgb(hue, 0.78, 0.98)))
        if step == 0:
            canvas.goto(x, y)
            continue
        canvas.pendown()
        canvas.goto(x, y)
        canvas.penup()
        marks.append(canvas.stroke_count)

    canvas.goto(0, 0)
    canvas.pensize(10)
    canvas.dot(14, "#FFF5E6")
    canvas.dot(7, "#FFB74D")
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

    marks = build_golden_spiral(_CANVAS)
    _STROKE_EVENTS = build_timeline(marks)
    print(f"  design: Golden Spiral · strokes: {len(marks)} · turns: {TURNS}")


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
        title="spiral.py",
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

    print(f"Logic in Motion Ep.03 Infinite Spiral {TOTAL_DUR:.1f}s · {TOTAL_FRAMES} frames")
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
