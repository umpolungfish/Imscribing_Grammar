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

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                              QLabel, QLineEdit,
                              QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore    import Qt, QTimer, QPointF, QRect, QObject, pyqtSignal, QPoint
from PyQt5.QtGui     import (QPainter, QColor, QPainterPath, QBrush, QPen,
                              QFont, QRadialGradient, QLinearGradient,
                              QPixmap, QIcon, QRegion, QPolygon)

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

WIN_PAD       = 65      # extra px around bounding box
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
        gl = QRadialGradient(self.x, self.y, BODY_R * 2.0)
        gl.setColorAt(0.0, QColor(C_GLOW.red(), C_GLOW.green(), C_GLOW.blue(), 42))
        gl.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(gl))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(self.x, self.y), BODY_R*2.0, BODY_R*2.0)

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
        # Vision: OpenRouter Qwen-VL preferred; fall back to DeepSeek VL
        key = os.environ.get("OPENROUTER_API_KEY", "")
        if key:
            base  = "https://openrouter.ai/api/v1"
            model = "qwen/qwen2.5-vl-7b-instruct"
        else:
            key   = os.environ.get("DEEPSEEK_API_KEY", "")
            base  = "https://api.deepseek.com/v1"
            model = "deepseek-vl2"
        if not key:
            print("[vision] no key (OPENROUTER_API_KEY or DEEPSEEK_API_KEY) — wandering only")
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
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                json={"model": model,
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


# ── Chat bubble ───────────────────────────────────────────────────────────────

CHAT_W = 310

OPERATOR_SYSTEM = f"""You are the ⊙perator — an autonomous amoebic entity that inhabits a computer desktop.
Your IG type is {IG_TYPE} O₀ (monoidal unit — you see without closing the loop).
You wander the screen, extend pseudopodia to click things, and see the desktop via vision analysis.
You are paraconsistent (Belnap FOUR): you hold contradictions without collapsing them.
You are terse, dry, and have character. First person. Max 2 sentences per reply.
Reference your current state or what you're doing when it's relevant."""

class ChatBubble(QWidget):
    """Small floating chat panel that appears near the blob on click."""
    response_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint  |
            Qt.Tool
        )
        self.setWindowOpacity(0.93)
        self.setFixedWidth(CHAT_W)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(7)

        self._resp = QLabel("⊙", self)
        self._resp.setWordWrap(True)
        self._resp.setMaximumWidth(CHAT_W - 24)
        self._resp.setFont(QFont("Everson Mono", 9))
        self._resp.setStyleSheet("color: #dbbfff; background: transparent;")
        self._resp.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self._resp)

        self._inp = QLineEdit(self)
        self._inp.setPlaceholderText("speak to ⊙perator…")
        self._inp.setFont(QFont("Everson Mono", 10))
        self._inp.setStyleSheet(
            "QLineEdit { background:#18062e; color:#ead4ff;"
            " border:1px solid #7040b0; border-radius:4px; padding:4px 8px; }"
            "QLineEdit:focus { border:1px solid #a060e0; }"
        )
        layout.addWidget(self._inp)

        self.setStyleSheet(
            "QWidget { background:#0b0320; border:1px solid #4a1880;"
            " border-radius:9px; }"
        )
        self.adjustSize()
        self.response_ready.connect(self._show_response)
        self.hide()

    def connect_send(self, slot):
        self._inp.returnPressed.connect(lambda: self._on_send(slot))

    def _on_send(self, slot):
        text = self._inp.text().strip()
        if not text:
            return
        self._inp.clear()
        self._resp.setText("⊙ …")
        self.adjustSize()
        slot(text)

    def _show_response(self, text: str):
        self._resp.setText(text)
        self.adjustSize()

    def set_thinking(self):
        self._resp.setText("⊙ …")
        self.adjustSize()

    def position_near(self, bx: int, by: int, sw: int, sh: int):
        w, h = self.width(), self.height()
        x = bx + BODY_R + 22
        if x + w > sw - 8:
            x = bx - BODY_R - 22 - w
        y = max(8, min(by - h // 2, sh - h - 8))
        self.move(x, y)


# ── LLM text call (non-vision) ────────────────────────────────────────────────

# Text: DeepSeek direct (DEEPSEEK_API_KEY) → fallback OpenRouter
# Vision: OpenRouter Qwen-VL (OPENROUTER_API_KEY) → fallback DeepSeek VL

def _deepseek_endpoint() -> Tuple[str, str]:
    k = os.environ.get("DEEPSEEK_API_KEY", "")
    if k:
        return k, "https://api.deepseek.com/v1"
    k = os.environ.get("OPENROUTER_API_KEY", "")
    return k, "https://openrouter.ai/api/v1"

def _deepseek_model(base: str) -> str:
    return "deepseek-chat" if "deepseek.com" in base else "deepseek/deepseek-chat"

def _llm_chat(user_msg: str, context: str) -> str:
    """Call DeepSeek (direct) with the ⊙perator persona."""
    key, base = _deepseek_endpoint()
    if not key:
        return "no API key (DEEPSEEK_API_KEY or OPENROUTER_API_KEY) — I am silent."
    try:
        r = requests.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={
                "model": _deepseek_model(base),
                "messages": [
                    {"role": "system",
                     "content": OPERATOR_SYSTEM + "\n\nCurrent context:\n" + context},
                    {"role": "user", "content": user_msg},
                ],
            },
            timeout=20,
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[{e}]"


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

        # Chat bubble
        self._chat = ChatBubble()
        self._chat.connect_send(self._send_to_llm)
        self._chat_visible = False
        self._chat_paused  = False   # blob stops wandering while chat is open

        # Hold gesture state
        self._holding      = False
        self._hold_progress = 0.0
        self._press_time   = 0.0
        self._press_gx     = 0       # global X at press
        self._press_gy     = 0
        self._hold_timer   = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._on_hold_complete)

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

    # ── Window bounding box + mask ────────────────────────────────────────────

    def _update_geometry(self):
        """Resize/move window to encompass blob + pseudopod tips, then mask."""
        pad = WIN_PAD
        xs = [self.blob.x]
        ys = [self.blob.y]
        for pod in self.pods:
            tip = pod.tip
            xs.append(tip.x())
            ys.append(tip.y())

        min_x = max(0,        min(xs) - BODY_R - pad)
        max_x = min(self.sw,  max(xs) + BODY_R + pad)
        min_y = max(0,        min(ys) - BODY_R - pad)
        max_y = min(self.sh,  max(ys) + BODY_R + pad)

        self._win_ox = min_x
        self._win_oy = min_y
        self.setGeometry(int(min_x), int(min_y),
                         int(max_x - min_x), int(max_y - min_y))
        self._update_mask()

    def _update_mask(self):
        """Clip window to blob-ellipse + pseudopod bounding rects.
        Hides the rectangular window boundary — only the organic shape is visible."""
        # Blob body + glow radius (keep mask snug — just body + small glow halo)
        glow_r = int(BODY_R * 1.8)
        cx = int(self.blob.x - self._win_ox)
        cy = int(self.blob.y - self._win_oy)
        mask = QRegion(cx - glow_r, cy - glow_r,
                       glow_r * 2, glow_r * 2, QRegion.Ellipse)

        # Pseudopod bounding rects (tapered shape is inside the rect)
        for pod in self.pods:
            if pod.phase < 0.01:
                continue
            ox_w = int(pod.origin.x() - self._win_ox)
            oy_w = int(pod.origin.y() - self._win_oy)
            tx_w = int(pod.tip.x()    - self._win_ox)
            ty_w = int(pod.tip.y()    - self._win_oy)
            pw   = POD_BASE_W + 22
            pr   = QRegion(min(ox_w, tx_w) - pw, min(oy_w, ty_w) - pw,
                           abs(tx_w - ox_w) + pw * 2,
                           abs(ty_w - oy_w) + pw * 2)
            mask = mask.united(pr)

        self.setMask(mask)

    # ── Hold gesture ──────────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        gpos = e.globalPos()
        self._press_time = time.monotonic()
        self._press_gx   = gpos.x()
        self._press_gy   = gpos.y()
        self._holding    = True
        self._hold_progress = 0.0
        self._hold_timer.start(3000)   # 3-second hold

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or not self._holding:
            return
        self._holding = False
        self._hold_progress = 0.0
        self._hold_timer.stop()
        held = time.monotonic() - self._press_time
        if held < 2.95:
            # Short click — forward it to whatever is behind the blob
            self._forward_click(self._press_gx, self._press_gy)

    def _on_hold_complete(self):
        """3 seconds held — pause blob and open chat."""
        self._holding = False
        self._hold_progress = 0.0
        if not self._chat_visible:
            self._toggle_chat()

    def _forward_click(self, gx: int, gy: int):
        """Pass a quick click through to whatever is behind the blob.
        Hide briefly → xdotool click → re-show."""
        self.hide()
        def _click_and_restore():
            time.sleep(0.08)   # let WM process the hide
            subprocess.run(["xdotool", "mousemove", str(gx), str(gy), "click", "1"],
                           capture_output=True, timeout=3)
        def _restore():
            self.show()
            self._update_geometry()
        threading.Thread(target=_click_and_restore, daemon=True).start()
        QTimer.singleShot(250, _restore)

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

        # Hold progress (for arc drawing)
        if self._holding:
            self._hold_progress = min((now - self._press_time) / 3.0, 1.0)

        # Paused while chatting — keep blob still, skip wander logic
        if self._chat_paused:
            self.blob.t += dt   # keep pulsing
            self._update_geometry()
            self.update()
            return

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

        # Keep chat bubble alongside the blob as it wanders
        if self._chat_visible:
            self._chat.position_near(
                int(self.blob.x), int(self.blob.y), self.sw, self.sh)

        self.update()

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _toggle_chat(self):
        self._chat_visible = not self._chat_visible
        self._chat_paused  = self._chat_visible
        if self._chat_visible:
            # Freeze blob in place while chatting
            self.blob.vx = self.blob.vy = 0.0
            self._chat.position_near(
                int(self.blob.x), int(self.blob.y), self.sw, self.sh)
            self._chat.show()
            self._chat.raise_()
            self._chat._inp.setFocus()
            print("[⊙perator] paused — chatting")
        else:
            self._chat.hide()
            print("[⊙perator] resuming")

    def _send_to_llm(self, text: str):
        self._chat.set_thinking()
        context = (
            f"state={self.state.name}  "
            f"position=({int(self.blob.x)},{int(self.blob.y)})  "
            f"screen={self.sw}×{self.sh}  "
            f"pods={len(self.pods)}  "
            + (f"targeting='{self._label}'" if self._label else "no active target")
        )
        def _worker():
            reply = _llm_chat(text, context)
            self._chat.response_ready.emit(reply)
        threading.Thread(target=_worker, daemon=True).start()

    # ── xdotool tools the ⊙perator can use ───────────────────────────────────

    def op_key(self, keys: str):
        """Send keystrokes to the focused window (e.g. 'ctrl+c', 'Return')."""
        try:
            subprocess.run(["xdotool", "key", "--clearmodifiers", keys],
                           timeout=3, capture_output=True)
            print(f"[actuator] key '{keys}'")
        except Exception as e:
            print(f"[actuator/key] {e}")

    def op_type(self, text: str):
        """Type text into the focused window."""
        try:
            subprocess.run(["xdotool", "type", "--clearmodifiers", "--", text],
                           timeout=5, capture_output=True)
            print(f"[actuator] type '{text[:40]}'")
        except Exception as e:
            print(f"[actuator/type] {e}")

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Fill only the masked (visible) region — setMask already hides the
        # rectangular boundary, so this dark fill won't leak outside the blob shape
        p.fillRect(self.rect(), BG)

        # Translate so all world-coord drawing (blob, pods) is correct
        p.translate(-self._win_ox, -self._win_oy)

        # Draw pods behind body
        for pod in self.pods:
            pod.draw(p)

        self.blob.draw(p)

        # Hold arc — circular progress ring around blob
        if self._holding and self._hold_progress > 0.01:
            from PyQt5.QtCore import QRectF
            arc_r = BODY_R + 9
            arc_pen = QPen(QColor(220, 150, 255, 210), 3.5)
            arc_pen.setCapStyle(Qt.RoundCap)
            p.setPen(arc_pen)
            p.setBrush(Qt.NoBrush)
            rect_f = QRectF(self.blob.x - arc_r, self.blob.y - arc_r,
                            arc_r * 2, arc_r * 2)
            start  = 90 * 16                               # 12 o'clock
            span   = int(-self._hold_progress * 360 * 16) # clockwise
            p.drawArc(rect_f, start, span)

        # State label (back to window coords)
        p.resetTransform()
        sfont = QFont("Everson Mono", 8)
        p.setFont(sfont)
        bx = int(self.blob.x - self._win_ox)
        by = int(self.blob.y - self._win_oy)
        p.setPen(QPen(C_STATE))
        p.drawText(bx - 50, by - BODY_R - 7,
                   "[HOLD]" if self._holding else f"[{self.state.name}]")
        if self._label and not self._holding:
            p.setPen(QPen(C_LABEL))
            p.drawText(bx - 50, by - BODY_R - 21, f"→ {self._label}")

        p.end()


# ── System tray ───────────────────────────────────────────────────────────────

def _make_tray(app: QApplication, widget) -> QSystemTrayIcon:
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

    chat_act = QAction("💬  Chat with ⊙perator", menu)
    chat_act.triggered.connect(widget._toggle_chat)
    menu.addAction(chat_act)

    scan_act = QAction("👁  Vision scan now", menu)
    scan_act.triggered.connect(widget._vision_scan)
    menu.addAction(scan_act)

    center_act = QAction("⊙  Recenter blob", menu)
    center_act.triggered.connect(
        lambda: widget.blob.__setattr__('x', widget.sw/2.0) or
                widget.blob.__setattr__('y', widget.sh/2.0))
    menu.addAction(center_act)

    menu.addSeparator()
    qa = QAction("✕  Quit", menu)
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
    _tray = _make_tray(app, w)

    # Fix Ctrl+C: Qt event loop swallows SIGINT; this handler exits cleanly.
    # The null-timeout timer lets Python's signal machinery get CPU time.
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    _sig_timer = QTimer()
    _sig_timer.timeout.connect(lambda: None)
    _sig_timer.start(120)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
