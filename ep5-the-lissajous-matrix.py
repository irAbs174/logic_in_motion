# Logic in Motion Ep.05 Ice Crystals 14s

# Youtube: 
# https://youtube.com/shorts/RjHI3oNwqRk?feature=share

"""
Scenes:

    Scene 0  Collection cover  2s
    Scene 1  Split studio code editor + live preview  7s
    Scene 2  Zoom transition studio → full canvas  0.5s
    Scene 3  Snowflake draw (finishes when last stroke lands)  2.5s
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
EPISODE_NUM = 5
EPISODE_TITLE = "Ice Crystals"
GITHUB_CTA = "Code in github"
SLUG = "05_koch_snowflake"

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
VIDEO_PATH = OUTPUT / "turtle_05_koch_snowflake.mp4"

CODE_LINES = [
    "import turtle",
    "",
    "def koch(length, n):",
    "    if n == 0:",
    "        turtle.forward(length)",
    "        return",
    "    koch(length / 3, n - 1)",
    "    turtle.left(60)",
    "    koch(length / 3, n - 1)",
    "    turtle.right(120)",
    "    koch(length / 3, n - 1)",
    "    turtle.left(60)",
    "    koch(length / 3, n - 1)",
    "",
    "for _ in range(3):",
    "    koch(300, 4)",
    "    turtle.right(120)",
]

# 2. DATA Koch snowflake crystal 
COORD_SCALE = 2.35
SIDE_LENGTH = 300
ITERATIONS = 4
EDGE_WIDTH = 2.4
INNER_WIDTH = 1.6
INNER_SCALE = 0.52

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


def ice_color(progress: float, *, hue_shift: float = 0.0) -> str:
    progress = max(0.0, min(1.0, progress))
    hue = 188 + progress * 42 + hue_shift
    sat = 0.55 + 0.28 * (1 - progress * 0.4)
    val = 0.88 + 0.12 * progress
    return rgb_hex(hsv_to_rgb(hue, sat, val))


def build_koch_snowflake(canvas: TurtleCanvas) -> list[int]:
    marks: list[int] = []
    segment_i = 0
    total_leaf = 3 * (4**ITERATIONS)

    canvas.clear_strokes()
    canvas.set_view(origin_y_frac=0.52, coord_scale=COORD_SCALE)
    canvas.penup()

    # Position so the equilateral triangle is centered.
    height = SIDE_LENGTH * math.sqrt(3) / 2
    start_x = -SIDE_LENGTH / 2
    start_y = -height / 3

    def koch(length: float, depth: int) -> None:
        nonlocal segment_i
        if depth == 0:
            canvas.pencolor(ice_color(segment_i / max(total_leaf - 1, 1)))
            canvas.pendown()
            canvas.forward(length)
            canvas.penup()
            marks.append(canvas.stroke_count)
            segment_i += 1
            return
        koch(length / 3, depth - 1)
        canvas.left(60)
        koch(length / 3, depth - 1)
        canvas.right(120)
        koch(length / 3, depth - 1)
        canvas.left(60)
        koch(length / 3, depth - 1)

    canvas.pensize(EDGE_WIDTH)
    canvas.goto(start_x, start_y)
    canvas.setheading(0)
    for _ in range(3):
        koch(SIDE_LENGTH, ITERATIONS)
        canvas.right(120)

    # Inner crystal echo one iteration lighter, scaled down.
    inner_len = SIDE_LENGTH * INNER_SCALE
    inner_height = inner_len * math.sqrt(3) / 2
    inner_x = -inner_len / 2
    inner_y = -inner_height / 3
    inner_leaf = 3 * (4 ** (ITERATIONS - 1))
    inner_i = 0

    def koch_inner(length: float, depth: int) -> None:
        nonlocal inner_i
        if depth == 0:
            canvas.pencolor(
                ice_color(inner_i / max(inner_leaf - 1, 1), hue_shift=28)
            )
            canvas.pendown()
            canvas.forward(length)
            canvas.penup()
            marks.append(canvas.stroke_count)
            inner_i += 1
            return
        koch_inner(length / 3, depth - 1)
        canvas.left(60)
        koch_inner(length / 3, depth - 1)
        canvas.right(120)
        koch_inner(length / 3, depth - 1)
        canvas.left(60)
        koch_inner(length / 3, depth - 1)

    canvas.pensize(INNER_WIDTH)
    canvas.goto(inner_x, inner_y)
    canvas.setheading(0)
    for _ in range(3):
        koch_inner(inner_len, ITERATIONS - 1)
        canvas.right(120)

    # Radiating ice spokes from center to each outer vertex region.
    canvas.pensize(1.4)
    for spoke in range(6):
        angle = spoke * 60 + 30
        tip = SIDE_LENGTH * 0.42
        canvas.pencolor(ice_color(spoke / 5, hue_shift=50))
        canvas.goto(0, 0)
        canvas.setheading(angle)
        canvas.pendown()
        canvas.forward(tip)
        canvas.penup()
        marks.append(canvas.stroke_count)

    canvas.goto(0, 0)
    canvas.pensize(10)
    canvas.dot(14, "#E8FBFF")
    canvas.dot(7, "#7EE8FF")
    marks.append(canvas.stroke_count)

    return marks


# 4. TIMELINE
def build_timeline(marks: list[int]) -> list[StrokeEvent]:
    if not marks:
        return []

    # Complete 2× faster (5s draw), then hold finished art through Scene 3.
    draw_start = SCENE_START[1]
    draw_end = SCENE_START[1] + 5.0
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

    marks = build_koch_snowflake(_CANVAS)
    _STROKE_EVENTS = build_timeline(marks)
    print(f"  design: Koch Snowflake · strokes: {len(marks)} · iterations: {ITERATIONS}")


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
        title="snowflake.py",
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

    print(f"Logic in Motion Ep.05 Ice Crystals {TOTAL_DUR:.1f}s · {TOTAL_FRAMES} frames")
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
