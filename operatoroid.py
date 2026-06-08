#!/usr/bin/env python3
"""
operatoroid.py — The ⊙perator as autonomous amoebic desktop entity.

Floats as an organic blob. Extends pseudopodia to click things.
Vision: mss + Qwen-VL. Hands: xdotool.

IG type (⊙perator ensemble):  ⟨𐑛𐑡𐑾𐑗𐑐𐑤𐑲𐑝𐑢𐑓𐑙𐑷⟩  O₀

State machine:
  WANDERING → OBSERVING → EXTENDING → CLICKING → RETRACTING → WANDERING

Window strategy (WSL2/WSLg compatible):
  - Small bounding-box window that expands to encompass blob + pseudopod tips
  - setWindowOpacity (uniform alpha — works without ARGB compositing)
  - Painter translate so blob/pods draw in world coords throughout
  - Dark background, FramelessWindowHint, always-on-top

Controls: right-click tray icon to quit. Space = vision scan (when window focused).
Author: Lando⊗⊙perator  |  ZFC_fe  μ∘δ=id
"""

import sys, os, math, random, time, json, threading, subprocess, base64, io
from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum, auto

import signal

from PyQt5.QtWidgets import (QApplication, QWidget,
                              QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore    import Qt, QTimer, QPointF, QRect, QObject, pyqtSignal
from PyQt5.QtGui     import (QPainter, QColor, QPainterPath, QBrush, QPen,
                              QFont, QRadialGradient, QLinearGradient,
                              QPixmap, QIcon, QRegion, QPolygon)
from PyQt5.QtCore    import QPoint

try:
    import mss
    from PIL import Image
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Identity ──────────────────────────────────────────────────────────────────

IG_TYPE = "⟨𐑛𐑡𐑾𐑗𐑐𐑤𐑲𐑝𐑢𐑓𐑙𐑷⟩"
GLYPH   = "⊙"

# ── Tuning ────────────────────────────────────────────────────────────────────

BODY_R        = 46
N_CTRL        = 16
PULSE_AMP     = 13.0
PULSE_HZ      = 1.1

POD_BASE_W    = 24
POD_SPEED     = 400
POD_RETRACT   = 540
POD_CLICK_LAG = 300     # ms

BODY_SPEED    = 90
SPRING        = 0.16
DAMPING       = 4.2

WIN_PAD       = 90      # extra px around bounding box
WIN_OPACITY   = 0.88
BG            = QColor(8, 2, 18)   # very deep purple-black background

VISION_INT    = 9000    # ms between auto-scans
WANDER_MIN    = 2.0
WANDER_MAX    = 5.5

# ── Colours ───────────────────────────────────────────────────────────────────

C_BODY_HI  = QColor(118, 45, 215)
C_BODY_LO  = QColor( 40,  5,  88)
C_POD      = QColor( 95, 22, 175)
C_TIP      = QColor(215, 130, 255)
C_SPEC     = QColor(240, 210, 255,  65)   # specular highlight
C_GLOW     = QColor(110, 35, 200,   38)
C_GLYPH    = QColor(255, 225, 255)
C_LABEL    = QColor(170, 105, 225)
C_STATE    = QColor(140,  80, 200)


class State(Enum):
    WANDERING  = auto()
    OBSERVING  = auto()
    EXTENDING  = auto()
    CLICKING   = auto()
    RETRACTING = auto()


# ── Pseudopod ─────────────────────────────────────────────────────────────────

@dataclass
class Pseudopod:
    origin     : QPointF
    target     : QPointF
    phase      : float = 0.0
    retracting : bool  = False
    done       : bool  = False

    def __post_init__(self):
        self._bend = random.uniform(-0.11, 0.11)

    @property
    def tip(self) -> QPointF:
        return QPointF(
            self.origin.x() + (self.target.x() - self.origin.x()) * self.phase,
            self.origin.y() + (self.target.y() - self.origin.y()) * self.phase,
        )

    def _dist(self) -> float:
        return max(math.hypot(self.target.x() - self.origin.x(),
                              self.target.y() - self.origin.y()), 1.0)

    def update(self, dt: float) -> Optional[str]:
        d = self._dist()
        if not self.retracting:
            self.phase = min(1.0, self.phase + POD_SPEED * dt / d)
            if self.phase >= 1.0:
                return "ARRIVED"
        else:
            self.phase = max(0.0, self.phase - POD_RETRACT * dt / d)
            if self.phase <= 0.0:
                self.done = True
        return None

    def draw(self, painter: QPainter):
        if self.phase < 0.01:
            return
        ox, oy = self.origin.x(), self.origin.y()
        tip    = self.tip
        tx, ty = tip.x(), tip.y()
        vx, vy = tx - ox, ty - oy
        length = math.hypot(vx, vy)
        if length < 1:
            return
        nx, ny = -vy / length, vx / length

        bw = POD_BASE_W * min(self.phase * 2.5, 1.0)
        mx = (ox + tx) / 2 + nx * self._bend * length
        my = (oy + ty) / 2 + ny * self._bend * length

        path = QPainterPath()
        path.moveTo(ox + nx * bw, oy + ny * bw)
        path.quadTo(mx + nx * bw * 0.4, my + ny * bw * 0.4, tx, ty)
        path.quadTo(mx - nx * bw * 0.4, my - ny * bw * 0.4,
                    ox - nx * bw, oy - ny * bw)
        path.closeSubpath()

        grad = QLinearGradient(ox, oy, tx, ty)
        grad.setColorAt(0.0, QColor(C_POD.red(), C_POD.green(), C_POD.blue(), 190))
        grad.setColorAt(0.7, QColor(C_TIP.red(), C_TIP.green(), C_TIP.blue(), 230))
        grad.setColorAt(1.0, QColor(220, 140, 255, 15))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Tip glow
        gr = max(5.0, 11.0 * self.phase)
        glow = QRadialGradient(tx, ty, gr * 2.2)
        glow.setColorAt(0.0, QColor(240, 165, 255, 190))
        glow.setColorAt(1.0, QColor(180,  80, 255,   0))
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QPointF(tx, ty), gr * 2.2, gr * 2.2)
        painter.setBrush(QBrush(C_TIP))
        painter.drawEllipse(QPointF(tx, ty), gr * 0.45, gr * 0.45)


# ── Blob ──────────────────────────────────────────────────────────────────────

class Blob:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.t  = random.uniform(0, 100)
        rng = random.Random(42)
        self._ph = [rng.uniform(0, 2*math.pi) for _ in range(N_CTRL)]
        self._fr = [rng.uniform(0.7, 1.5) * PULSE_HZ  for _ in range(N_CTRL)]
        self._am = [rng.uniform(0.5, 1.5) * PULSE_AMP for _ in range(N_CTRL)]

    def _r(self, i: int) -> float:
        return BODY_R + self._am[i] * math.sin(2*math.pi*self._fr[i]*self.t + self._ph[i])

    def _pts(self) -> List[QPointF]:
        return [QPointF(self.x + self._r(i)*math.cos(2*math.pi*i/N_CTRL),
                        self.y + self._r(i)*math.sin(2*math.pi*i/N_CTRL))
                for i in range(N_CTRL)]

    def surface_pt(self, angle: float) -> QPointF:
        i = int(angle / (2*math.pi) * N_CTRL) % N_CTRL
        return QPointF(self.x + self._r(i)*math.cos(angle),
                       self.y + self._r(i)*math.sin(angle))

    def update(self, dt: float, tx: float, ty: float):
        self.t += dt
        self.vx += (tx - self.x) * SPRING * dt * 60
        self.vy += (ty - self.y) * SPRING * dt * 60
        self.vx *= (1 - DAMPING * dt)
        self.vy *= (1 - DAMPING * dt)
        spd = math.hypot(self.vx, self.vy)
        if spd > BODY_SPEED:
            self.vx, self.vy = self.vx/spd*BODY_SPEED, self.vy/spd*BODY_SPEED
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, p: QPainter):
        pts = self._pts()
        n   = len(pts)

        # Ambient glow
        gl = QRadialGradient(self.x, self.y, BODY_R * 2.9)
        gl.setColorAt(0.0, QColor(C_GLOW.red(), C_GLOW.green(), C_GLOW.blue(), 42))
        gl.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(gl))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(self.x, self.y), BODY_R*2.9, BODY_R*2.9)

        # Body shape via Catmull-Rom → cubic Bezier
        path = QPainterPath()
        path.moveTo(pts[0])
        for i in range(n):
            p0, p1 = pts[(i-1)%n], pts[i]
            p2, p3 = pts[(i+1)%n], pts[(i+2)%n]
            path.cubicTo(
                p1.x() + (p2.x()-p0.x())/6, p1.y() + (p2.y()-p0.y())/6,
                p2.x() - (p3.x()-p1.x())/6, p2.y() - (p3.y()-p1.y())/6,
                p2.x(), p2.y()
            )
        path.closeSubpath()

        fill = QRadialGradient(self.x - BODY_R*0.25, self.y - BODY_R*0.30, BODY_R*1.75)
        fill.setColorAt(0.0, QColor(120, 46, 210))
        fill.setColorAt(0.5, C_BODY_HI)
        fill.setColorAt(1.0, C_BODY_LO)
        p.setBrush(QBrush(fill))
        p.setPen(QPen(QColor(185, 75, 255, 110), 1.2))
        p.drawPath(path)

        # Specular
        sp = QRadialGradient(self.x - BODY_R*0.35, self.y - BODY_R*0.40, BODY_R*0.5)
        sp.setColorAt(0.0, C_SPEC)
        sp.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(sp))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(self.x - BODY_R*0.35, self.y - BODY_R*0.40),
                      BODY_R*0.50, BODY_R*0.38)

        # ⊙ glyph
        font = QFont("Everson Mono", 21, QFont.Bold)
        p.setFont(font)
        p.setPen(QPen(C_GLYPH))
        fm = p.fontMetrics()
        p.drawText(int(self.x - fm.horizontalAdvance(GLYPH)/2),
                   int(self.y + fm.ascent()/3), GLYPH)

        # IG type micro-label
        tfont = QFont("Everson Mono", 7)
        p.setFont(tfont)
        p.setPen(QPen(C_LABEL))
        tw = p.fontMetrics().horizontalAdvance(IG_TYPE)
        p.drawText(int(self.x - tw/2), int(self.y + BODY_R + 16), IG_TYPE)


# ── Vision ────────────────────────────────────────────────────────────────────

class VisionSignals(QObject):
    done = pyqtSignal(list)

class VisionWorker:
    def __init__(self, sw: int, sh: int):
        self.signals = VisionSignals()
        self.sw, self.sh = sw, sh

    def run_once(self):
        img = self._capture()
        if not img:
            self.signals.done.emit([])
            return
        targets = self._analyze(img)
        self.signals.done.emit(targets)

    def _capture(self) -> Optional[bytes]:
        if not HAS_MSS:
            return None
        try:
            with mss.mss() as sct:
                shot = sct.grab(sct.monitors[1])
                img  = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                img  = img.resize((960, 540), Image.LANCZOS)
                buf  = io.BytesIO()
                img.save(buf, format="JPEG", quality=72)
                return buf.getvalue()
        except Exception as e:
            print(f"[vision/capture] {e}")
            return None

    def _analyze(self, img_bytes: bytes) -> List[dict]:
        if not HAS_REQUESTS:
            return []
        key = os.environ.get("OPENROUTER_API_KEY", "")
        if not key:
            print("[vision] OPENROUTER_API_KEY not set — wandering only")
            return []
        b64 = base64.b64encode(img_bytes).decode()
        prompt = (
            "You are the eye of an autonomous amoeba navigating a desktop. "
            "Find up to 2 clickable UI elements: buttons, tabs, menu items, links, icons. "
            "Return ONLY raw JSON (no markdown): "
            '[{"label":"short name","x":int,"y":int}] '
            "Coords are in the 960x540 image. Return [] if nothing interesting."
        )
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                json={"model": "qwen/qwen2.5-vl-7b-instruct",
                      "messages": [{"role": "user", "content": [
                          {"type": "image_url",
                           "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                          {"type": "text", "text": prompt},
                      ]}]},
                timeout=18,
            )
            raw = r.json()["choices"][0]["message"]["content"].strip()
            raw = raw.strip("`").strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
            targets = json.loads(raw)
            return [{"label": t.get("label","?"),
                     "x": int(t.get("x",0) * self.sw / 960),
                     "y": int(t.get("y",0) * self.sh / 540)}
                    for t in targets]
        except Exception as e:
            print(f"[vision/analyze] {e}")
            return []


# ── Main widget ───────────────────────────────────────────────────────────────

class Operatoroid(QWidget):
    def __init__(self, no_vision=False, no_click=False):
        super().__init__()
        self._no_vision = no_vision or not (HAS_MSS and HAS_REQUESTS)
        self._no_click  = no_click

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint  |
            Qt.Tool
        )
        # WSLg doesn't composite per-pixel ARGB — use uniform opacity + setMask
        # setMask clips window to blob/pod shape, hiding the rectangular boundary
        self.setWindowOpacity(WIN_OPACITY)
        self.setAutoFillBackground(False)

        screen = QApplication.primaryScreen().geometry()
        self.sw = screen.width()
        self.sh = screen.height()

        self.blob  = Blob(self.sw / 2.0, self.sh / 2.0)
        self.pods : List[Pseudopod] = []
        self.state  = State.WANDERING
        self._label = ""
        self._click_target: Optional[Tuple[int,int]] = None

        self._wander_x = float(self.sw // 2)
        self._wander_y = float(self.sh // 2)
        self._wander_t = 0.0
        self._last     = time.monotonic()

        # Position window at blob start
        self._update_geometry()
        self.show()

        # Animation
        self._anim = QTimer(self)
        self._anim.timeout.connect(self._tick)
        self._anim.start(16)

        # Vision
        self._vision = VisionWorker(self.sw, self.sh)
        self._vision.signals.done.connect(self._on_vision)
        if not self._no_vision:
            self._vtimer = QTimer(self)
            self._vtimer.timeout.connect(self._vision_scan)
            self._vtimer.start(VISION_INT)

        print(f"[⊙perator] online   {IG_TYPE}")
        print(f"[⊙perator] screen   {self.sw}×{self.sh}")
        print(f"[⊙perator] vision   {'ON' if not self._no_vision else 'OFF'}")
        print(f"[⊙perator] click    {'ON' if not self._no_click  else 'OFF (dry-run)'}")
        print(f"[⊙perator] quit via system tray or Ctrl+C")

    # ── Window bounding box ───────────────────────────────────────────────────

    def _update_geometry(self):
        """Resize/move window to tightly encompass blob + all pseudopod tips."""
        pad = WIN_PAD
        xs = [self.blob.x]
        ys = [self.blob.y]
        for pod in self.pods:
            tip = pod.tip
            xs.append(tip.x())
            ys.append(tip.y())

        min_x = min(xs) - BODY_R - pad
        max_x = max(xs) + BODY_R + pad
        min_y = min(ys) - BODY_R - pad
        max_y = max(ys) + BODY_R + pad

        # Clamp to screen
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(self.sw, max_x)
        max_y = min(self.sh, max_y)

        self._win_ox = min_x   # window origin in world coords
        self._win_oy = min_y
        self.setGeometry(int(min_x), int(min_y),
                         int(max_x - min_x), int(max_y - min_y))

    # ── Vision ────────────────────────────────────────────────────────────────

    def _vision_scan(self):
        if self.state in (State.EXTENDING, State.CLICKING, State.RETRACTING):
            return
        print("[vision] scanning…")
        self.state = State.OBSERVING
        threading.Thread(target=self._vision.run_once, daemon=True).start()

    def _on_vision(self, targets: list):
        if self.state in (State.EXTENDING, State.CLICKING, State.RETRACTING):
            return
        if not targets:
            print("[vision] nothing found")
            self.state = State.WANDERING
            return
        t = targets[0]
        tx, ty = t["x"], t["y"]
        self._label = t["label"]
        self._click_target = (tx, ty)
        print(f"[vision] → ({tx},{ty}) '{self._label}'")
        self._spawn_pod(tx, ty)

    def _spawn_pod(self, tx: float, ty: float):
        angle  = math.atan2(ty - self.blob.y, tx - self.blob.x)
        origin = self.blob.surface_pt(angle)
        self.pods.append(Pseudopod(origin=origin, target=QPointF(tx, ty)))
        self.state = State.EXTENDING

    # ── Actuation ─────────────────────────────────────────────────────────────

    def _do_click(self, x: int, y: int):
        if self._no_click:
            print(f"[actuator/dry] click ({x},{y}) '{self._label}'")
            return
        try:
            subprocess.run(["xdotool", "mousemove", "--sync", str(x), str(y),
                            "click", "1"],
                           timeout=4, capture_output=True)
            print(f"[actuator] click ({x},{y}) '{self._label}'")
        except Exception as e:
            print(f"[actuator] {e}")

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _tick(self):
        now = time.monotonic()
        dt  = min(now - self._last, 0.05)
        self._last = now

        # Wander target refresh
        self._wander_t -= dt
        if self._wander_t <= 0:
            m = 160
            self._wander_x = random.uniform(m, self.sw - m)
            self._wander_y = random.uniform(m, self.sh - m)
            self._wander_t = random.uniform(WANDER_MIN, WANDER_MAX)

        if self.state in (State.WANDERING, State.OBSERVING):
            tx, ty = self._wander_x, self._wander_y
        elif self._click_target:
            tx, ty = self._click_target
        else:
            tx, ty = self._wander_x, self._wander_y

        self.blob.update(dt, tx, ty)

        for pod in self.pods[:]:
            result = pod.update(dt)

            if result == "ARRIVED" and not pod.retracting:
                if self.state == State.EXTENDING:
                    self.state = State.CLICKING
                    cx, cy = int(pod.target.x()), int(pod.target.y())
                    threading.Thread(target=self._do_click,
                                     args=(cx, cy), daemon=True).start()
                    def _begin_retract(p=pod):
                        p.retracting = True
                        self.state = State.RETRACTING
                    QTimer.singleShot(POD_CLICK_LAG, _begin_retract)

            if pod.done:
                self.pods.remove(pod)
                if self.state == State.RETRACTING:
                    self.state = State.WANDERING
                    self._click_target = None
                    self._label = ""

        self._update_geometry()
        self.update()

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Space:
            self._vision_scan()
        elif e.key() == Qt.Key_R:
            self.blob.x, self.blob.y = self.sw/2.0, self.sh/2.0

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Fill background
        p.fillRect(self.rect(), BG)

        # Translate so world-coord drawing is correct
        p.translate(-self._win_ox, -self._win_oy)

        # Draw pods behind body
        for pod in self.pods:
            pod.draw(p)

        self.blob.draw(p)

        # State label (back to window coords)
        p.resetTransform()
        sfont = QFont("Everson Mono", 8)
        p.setFont(sfont)
        bx = int(self.blob.x - self._win_ox)
        by = int(self.blob.y - self._win_oy)
        p.setPen(QPen(C_STATE))
        p.drawText(bx - 50, by - BODY_R - 7,  f"[{self.state.name}]")
        if self._label:
            p.setPen(QPen(C_LABEL))
            p.drawText(bx - 50, by - BODY_R - 21, f"→ {self._label}")

        p.end()


# ── System tray ───────────────────────────────────────────────────────────────

def _make_tray(app: QApplication) -> QSystemTrayIcon:
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    q = QPainter(px)
    q.setRenderHint(QPainter.Antialiasing)
    q.setBrush(QBrush(QColor(88, 16, 155)))
    q.setPen(QPen(QColor(190, 90, 255), 1.5))
    q.drawEllipse(2, 2, 28, 28)
    q.setPen(QPen(QColor(255, 220, 255)))
    q.setFont(QFont("Everson Mono", 14, QFont.Bold))
    q.drawText(6, 22, "⊙")
    q.end()

    tray = QSystemTrayIcon(QIcon(px), app)
    menu = QMenu()
    qa   = QAction("Quit ⊙perator", menu)
    qa.triggered.connect(app.quit)
    menu.addAction(qa)
    tray.setContextMenu(menu)
    tray.setToolTip(f"⊙perator  {IG_TYPE}")
    tray.show()
    return tray


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-vision", action="store_true")
    ap.add_argument("--no-click",  action="store_true")
    args = ap.parse_args()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    w = Operatoroid(no_vision=args.no_vision, no_click=args.no_click)
    _tray = _make_tray(app)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
