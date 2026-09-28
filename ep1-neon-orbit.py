# Logic in Motion Ep.01 Neon Orbit Bloom 14s

# Youtube:
# https://youtube.com/shorts/yTeFxKtx12Y?feature=share

"""
Scenes:

  Scene 0  Collection cover  2s
  Scene 1  Split studio code editor + live preview  7s
  Scene 2  Zoom transition studio → full canvas  0.5s
  Scene 3  Orbit draw (finishes when last stroke lands)  2.5s
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
from lib.settings import CACHE, FPS, OUTPUT, SEED
from lib.settings import GITHUB_REPO_URL
from lib.studio_design import (
    composite_preview_panel,
    draw_studio_end_card,
    load_studio_background,
    render_collection_cover,
)
from lib.types import EpisodeConfig, StrokeEvent

# 1. SETTINGS
EPISODE_NUM = 1
EPISODE_TITLE = "Neon Orbit"
GITHUB_CTA = "Code in github"
SLUG = "01_neon_orbit"

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
VIDEO_PATH = OUTPUT / "turtle_01_neon_orbit.mp4"

CODE_LINES = [
    "import math, turtle",
    "",
    "def spiro(R, r, d, n):",
    "    for i in range(n):",
    "        t = i * 0.07",
    "        x = (R-r)*math.cos(t)",
    "        x += d*math.cos(((R-r)/r)*t)",
    "        y = (R-r)*math.sin(t)",
    "        y -= d*math.sin(((R-r)/r)*t)",
    "        turtle.goto(x, y)",
    "",
    "spiro(195, 59, 92, 360)",
]

# 2. DATA Spirograph orbit layers
COORD_SCALE = 2.65
ORBIT_LAYERS = [
    (205, 62, 96, 4.6, 3.2),
    (168, 51, 78, 5.4, 2.6),
    (132, 40, 62, 6.2, 2.0),
]
FOLDS = 6
STEPS_PER_CURVE = 72

_BG = load_studio_background()
_CANVAS = TurtleCanvas()
_CANVAS.set_background(_BG)
_STROKE_EVENTS: list[StrokeEvent] = []
_LAYER_EVENTS: list[StrokeEvent] = []


# 3. DRAWdef hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
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


def spiro_point(R: float, r: float, d: float, t: float) -> tuple[float, float]:
    x = (R - r) * math.cos(t) + d * math.cos(((R - r) / r) * t)
    y = (R - r) * math.sin(t) - d * math.sin(((R - r) / r) * t)
    return x, y


def rotate_xy(x: float, y: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return x * math.cos(rad) - y * math.sin(rad), x * math.sin(rad) + y * math.cos(rad)


def build_neon_orbit(canvas: TurtleCanvas) -> list[int]:
    marks: list[int] = []

    canvas.clear_strokes()
    canvas.set_view(origin_y_frac=0.52, coord_scale=COORD_SCALE)
    canvas.penup()

    for fold in range(FOLDS):
        fold_angle = fold * (360 / FOLDS)
        for layer_i, (R, r, d, turns, width) in enumerate(ORBIT_LAYERS):
            canvas.pensize(width)
            prev: tuple[float, float] | None = None
            for step in range(STEPS_PER_CURVE + 1):
                t = (step / STEPS_PER_CURVE) * turns * 2 * math.pi
                x, y = spiro_point(R, r, d, t)
                x, y = rotate_xy(x, y, fold_angle)
                hue = (layer_i * 55 + fold * 24 + step * 1.4) % 360
                canvas.pencolor(rgb_hex(hsv_to_rgb(hue, 0.92, 1.0)))
                if prev is None:
                    canvas.goto(x, y)
                    prev = (x, y)
                    continue
                canvas.pendown()
                canvas.goto(x, y)
                canvas.penup()
                marks.append(canvas.stroke_count)
                prev = (x, y)

    canvas.goto(0, 0)
    canvas.pensize(10)
    canvas.dot(14, "#FFFFFF")
    canvas.dot(8, "#00E5FF")
    marks.append(canvas.stroke_count)

    return marks


# 4. TIMELINEdef build_timeline(marks: list[int]) -> tuple[list[StrokeEvent], list[StrokeEvent]]:
    if not marks:
        return [], []

    draw_start = SCENE_START[1]
    draw_end = SCENE_START[3] + DUR[3]
    draw_dur = draw_end - draw_start
    events = [
        StrokeEvent(t=draw_start + (i / max(len(marks) - 1, 1)) * draw_dur, stroke_index=c)
        for i, c in enumerate(marks)
    ]
    if events:
        events[-1] = StrokeEvent(t=draw_end, stroke_index=marks[-1])

    layer_stride = max(1, len(marks) // (len(ORBIT_LAYERS) * FOLDS))
    layer_events = [
        StrokeEvent(t=draw_start + (i * layer_stride / len(marks)) * draw_dur * 0.95, stroke_index=marks[min(i * layer_stride, len(marks) - 1)])
        for i in range(1, len(ORBIT_LAYERS) * FOLDS + 1)
    ]
    return events, layer_events


def init_drawing() -> None:
    global _STROKE_EVENTS, _LAYER_EVENTS, _BG, _CANVAS

    _BG = load_studio_background()
    _CANVAS = TurtleCanvas()
    _CANVAS.set_background(_BG)

    marks = build_neon_orbit(_CANVAS)
    _STROKE_EVENTS, _LAYER_EVENTS = build_timeline(marks)
    print(f"  design: Neon Orbit Bloom · strokes: {len(marks)} · folds: {FOLDS}")


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
        title="orbit.py",
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


# 7. AUDIO
def build_audio() -> None:
    render_episode_audio(TOTAL_DUR, AUDIO_PATH)


# 8. RENDER + ENCODE
def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    print(f"Logic in Motion Ep.01 Neon Orbit {TOTAL_DUR:.1f}s · {TOTAL_FRAMES} frames")
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
