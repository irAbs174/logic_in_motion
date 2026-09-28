# Logic in Motion Ep.04 Digital Mandala 14s

# Youtube: 
# https://youtube.com/shorts/COgVj9XxQhU?feature=share

"""
Scenes:

    Scene 0  Collection cover  2s
    Scene 1  Split studio code editor + live preview  7s
    Scene 2  Zoom transition studio → full canvas  0.5s
    Scene 3  Mandala draw (finishes when last stroke lands)  2.5s
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
EPISODE_NUM = 4
EPISODE_TITLE = "Digital Mandala"
GITHUB_CTA = "Code in github"
SLUG = "04_mandala"

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
VIDEO_PATH = OUTPUT / "turtle_04_mandala.mp4"

CODE_LINES = [
    "import math, turtle",
    "",
    "def petal(inner, outer, angle, span):",
    "    for i in range(11):",
    "        t = angle - span/2 + i * span / 10",
    "        rad = math.radians(t)",
    "        x = outer * math.cos(rad)",
    "        y = outer * math.sin(rad)",
    "        turtle.goto(x, y)",
    "",
    "for layer in range(6):",
    "    off = layer * (360 / 12 / 2)",
    "    for p in range(12):",
    "        petal(120, 200 - layer * 28, p * 30 + off, 14)",
]

# 2. DATA Radial mandala weave 
COORD_SCALE = 2.55
PETALS = 12
LAYERS = 6
OUTER_RADIUS = 200
LAYER_STEP = 28
PETAL_ARC_STEPS = 10
PETAL_SPAN = 14.0
RING_STEPS = 48
WARP_WIDTH = 1.4
WEFT_WIDTH = 2.0
PETAL_WIDTH = 2.6

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


def polar(radius: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return radius * math.cos(rad), radius * math.sin(rad)


def build_digital_mandala(canvas: TurtleCanvas) -> list[int]:
    marks: list[int] = []

    canvas.clear_strokes()
    canvas.set_view(origin_y_frac=0.52, coord_scale=COORD_SCALE)
    canvas.penup()

    petal_step = 360.0 / PETALS

    # Warp radial spokes woven through each layer ring.
    canvas.pensize(WARP_WIDTH)
    for layer in range(LAYERS):
        outer = OUTER_RADIUS - layer * LAYER_STEP
        inner = max(18, outer - LAYER_STEP + 10)
        hue_base = 185 + layer * 18

        for spoke in range(PETALS):
            angle = spoke * petal_step + layer * (petal_step / 2)
            canvas.pencolor(rgb_hex(hsv_to_rgb(hue_base + spoke * 4, 0.72, 0.92)))
            x0, y0 = polar(inner, angle)
            x1, y1 = polar(outer, angle)
            canvas.goto(x0, y0)
            canvas.pendown()
            canvas.goto(x1, y1)
            canvas.penup()
            marks.append(canvas.stroke_count)

    # Weft concentric rings tying the warp together.
    canvas.pensize(WEFT_WIDTH)
    for layer in range(LAYERS):
        radius = OUTER_RADIUS - layer * LAYER_STEP
        hue = 280 + layer * 22
        canvas.pencolor(rgb_hex(hsv_to_rgb(hue, 0.78, 0.95)))

        for step in range(RING_STEPS + 1):
            angle = step * (360.0 / RING_STEPS)
            x, y = polar(radius, angle)
            if step == 0:
                canvas.goto(x, y)
                continue
            canvas.pendown()
            canvas.goto(x, y)
            canvas.penup()
            marks.append(canvas.stroke_count)

    # Petal arcs radial symmetry blooms layer by layer.
    canvas.pensize(PETAL_WIDTH)
    for layer in range(LAYERS):
        outer = OUTER_RADIUS - layer * LAYER_STEP
        inner = max(22, outer - LAYER_STEP + 12)
        offset = layer * (petal_step / 2)
        hue_base = 320 - layer * 12

        for petal in range(PETALS):
            center = petal * petal_step + offset
            half = PETAL_SPAN / 2
            left = center - half
            right = center + half

            canvas.pencolor(rgb_hex(hsv_to_rgb(hue_base + petal * 5, 0.88, 1.0)))

            xi, yi = polar(inner, center)
            xl, yl = polar(outer, left)
            canvas.goto(xi, yi)
            canvas.pendown()
            canvas.goto(xl, yl)
            canvas.penup()
            marks.append(canvas.stroke_count)

            prev: tuple[float, float] | None = (xl, yl)
            for step in range(PETAL_ARC_STEPS + 1):
                t = left + step * PETAL_SPAN / PETAL_ARC_STEPS
                x, y = polar(outer, t)
                if prev is None:
                    canvas.goto(x, y)
                    prev = (x, y)
                    continue
                canvas.pendown()
                canvas.goto(x, y)
                canvas.penup()
                marks.append(canvas.stroke_count)
                prev = (x, y)

            xr, yr = polar(outer, right)
            canvas.pendown()
            canvas.goto(xr, yr)
            canvas.penup()
            marks.append(canvas.stroke_count)

            canvas.pendown()
            canvas.goto(xi, yi)
            canvas.penup()
            marks.append(canvas.stroke_count)

    canvas.goto(0, 0)
    canvas.pensize(10)
    canvas.dot(16, "#FFFFFF")
    canvas.dot(9, "#00E5FF")
    canvas.dot(5, "#FF3CB4")
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

    marks = build_digital_mandala(_CANVAS)
    _STROKE_EVENTS = build_timeline(marks)
    print(f"  design: Digital Mandala · strokes: {len(marks)} · petals: {PETALS} · layers: {LAYERS}")


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
        title="mandala.py",
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

    print(f"Logic in Motion Ep.04 Digital Mandala {TOTAL_DUR:.1f}s · {TOTAL_FRAMES} frames")
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
