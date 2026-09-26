#!/usr/bin/env python3
"""
Logic in Motion — Ep.06 · The Illusion of Motion ~14s.

  Scene 0  Collection cover                                       ~2s
  Scene 1  Split studio — code editor + live preview              ~7s
  Scene 2  Zoom transition — studio → full canvas                 ~0.5s
  Scene 3  Illusion draw (finishes when last stroke lands)        ~2.5s
  Scene 4  End card — Code in github                              ~2s
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

# ── 1. SETTINGS ──────────────────────────────────────────────────────────

EPISODE_NUM = 6
EPISODE_TITLE = "Illusion of Motion"
GITHUB_CTA = "Code in github"
SLUG = "06_optical_illusion"

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
VIDEO_PATH = OUTPUT / "turtle_06_optical_illusion.mp4"

CODE_LINES = [
    "import math, turtle",
    "",
    "def wave(y, amp, phase):",
    "    turtle.penup()",
    "    for x in range(-180, 181, 4):",
    "        yy = y + amp * math.sin(",
    "            math.radians(x * 3 + phase))",
    "        turtle.goto(x, yy)",
    "        turtle.pendown()",
    "",
    "for i in range(8):",
    "    wave(-140 + i * 40, 18, i * 28)",
    "",
    "for x in range(-160, 161, 14):",
    "    turtle.penup(); turtle.goto(x, -160)",
    "    turtle.pendown(); turtle.goto(x, 160)",
]

# ── 2. DATA — Parallel lines + sine curves ───────────────────────────────

COORD_SCALE = 2.45
HALF = 175.0
LINE_STEP = 14
WAVES = 8
CURVES = 12
WAVE_AMP = 18.0
WAVE_FREQ = 3.0
CURVE_AMP = 12.0
CURVE_FREQ = 4.5
LINE_WIDTH = 1.8
WAVE_WIDTH = 2.4
CURVE_WIDTH = 1.6
WAVE_STEP = 4

_BG = load_studio_background()
_CANVAS = TurtleCanvas()
_CANVAS.set_background(_BG)
_STROKE_EVENTS: list[StrokeEvent] = []


# ── 3. DRAW ──────────────────────────────────────────────────────────────

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


def vibe_color(progress: float, *, mode: str = "line") -> str:
    """Cyan↔magenta vibration — high contrast for motion illusion."""
    progress = max(0.0, min(1.0, progress))
    if mode == "line":
        # Alternate cyan / magenta by progress bands
        hue = 188 if int(progress * 24) % 2 == 0 else 312
        sat, val = 0.82, 0.95
    elif mode == "wave":
        hue = 200 + progress * 110
        sat, val = 0.88, 0.98
    else:  # curve
        hue = 320 - progress * 90
        sat, val = 0.75, 0.92
    return rgb_hex(hsv_to_rgb(hue, sat, val))


def build_optical_illusion(canvas: TurtleCanvas) -> list[int]:
    marks: list[int] = []

    canvas.clear_strokes()
    canvas.set_view(origin_y_frac=0.52, coord_scale=COORD_SCALE)
    canvas.penup()

    xs = [x for x in range(int(-HALF), int(HALF) + 1, LINE_STEP)]
    n_lines = len(xs)

    # 1. Parallel verticals — the "still" field that eyes misread as moving.
    canvas.pensize(LINE_WIDTH)
    for i, x in enumerate(xs):
        canvas.pencolor(vibe_color(i / max(n_lines - 1, 1), mode="line"))
        canvas.goto(x, -HALF)
        canvas.pendown()
        canvas.goto(x, HALF)
        canvas.penup()
        marks.append(canvas.stroke_count)

    # 2. Primary sine waves — horizontal curves weaving the field.
    canvas.pensize(WAVE_WIDTH)
    for w in range(WAVES):
        y0 = -HALF + 20 + w * ((2 * HALF - 40) / max(WAVES - 1, 1))
        phase = w * 28
        amp = WAVE_AMP * (0.85 + 0.15 * math.sin(w))
        canvas.pencolor(vibe_color(w / max(WAVES - 1, 1), mode="wave"))
        first = True
        for x in range(int(-HALF), int(HALF) + 1, WAVE_STEP):
            yy = y0 + amp * math.sin(math.radians(x * WAVE_FREQ + phase))
            if first:
                canvas.goto(x, yy)
                canvas.pendown()
                first = False
            else:
                canvas.goto(x, yy)
        canvas.penup()
        marks.append(canvas.stroke_count)

    # 3. Secondary phase-shifted curves — denser, thinner, opposite hue sweep.
    canvas.pensize(CURVE_WIDTH)
    for c in range(CURVES):
        y0 = -HALF + 8 + c * ((2 * HALF - 16) / max(CURVES - 1, 1))
        phase = 90 + c * 18
        amp = CURVE_AMP * (0.7 + 0.3 * ((c % 3) / 2))
        canvas.pencolor(vibe_color(c / max(CURVES - 1, 1), mode="curve"))
        first = True
        for x in range(int(-HALF), int(HALF) + 1, WAVE_STEP + 1):
            yy = y0 + amp * math.sin(math.radians(x * CURVE_FREQ + phase))
            if first:
                canvas.goto(x, yy)
                canvas.pendown()
                first = False
            else:
                canvas.goto(x, yy)
        canvas.penup()
        marks.append(canvas.stroke_count)

    # 4. Soft diagonal accents (Zöllner tilt) — sparse, for extra motion cue.
    canvas.pensize(1.3)
    for d in range(7):
        x0 = -HALF + 18 + d * 48
        canvas.pencolor(vibe_color(d / 6, mode="wave"))
        canvas.goto(x0, -HALF + 10)
        canvas.setheading(62)
        canvas.pendown()
        canvas.forward(HALF * 0.55)
        canvas.penup()
        marks.append(canvas.stroke_count)

    canvas.goto(0, 0)
    canvas.pensize(8)
    canvas.dot(11, "#F0FBFF")
    canvas.dot(5, "#FF3CB4")
    marks.append(canvas.stroke_count)

    return marks


# ── 4. TIMELINE ──────────────────────────────────────────────────────────

def build_timeline(marks: list[int]) -> list[StrokeEvent]:
    if not marks:
        return []

    # Complete ~2× faster (~5s draw), then hold finished art through Scene 3.
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

    marks = build_optical_illusion(_CANVAS)
    _STROKE_EVENTS = build_timeline(marks)
    print(f"  design: Optical Illusion · strokes: {len(marks)} · waves={WAVES} curves={CURVES}")


def visible_at(t: float) -> int:
    count = 0
    for ev in _STROKE_EVENTS:
        if t >= ev.t:
            count = ev.stroke_index
    return max(0, count)


def art_glow(t: float) -> Image.Image:
    return _CANVAS.snapshot(visible_strokes=visible_at(t), glow=True)


# ── 5. SCENE RENDERERS ───────────────────────────────────────────────────

def render_studio_intro(lt: float) -> Image.Image:
    editor = draw_code_editor_panel(
        _BG.copy(),
        lt,
        DUR[1],
        code_lines=CODE_LINES,
        title="illusion.py",
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


# ── 7. AUDIO ─────────────────────────────────────────────────────────────

def build_audio() -> None:
    render_episode_audio(TOTAL_DUR, AUDIO_PATH)


# ── 8. RENDER + ENCODE ───────────────────────────────────────────────────

def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    print(f"Logic in Motion — Ep.06 Illusion of Motion — {TOTAL_DUR:.1f}s · {TOTAL_FRAMES} frames")
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
