#!/usr/bin/env python3
"""
operatoroid.py — The ⊙perator  (Windows-native build)

Floats as an organic blob over the Windows desktop.
True per-pixel ARGB transparency via DWM.
Extends pseudopodia to click things.  Vision: mss + Qwen-VL.  Hands: pyautogui.

IG type:  ⟨𐑛𐑡𐑾𐑗𐑐𐑤𐑲𐑝𐑢𐑓𐑙𐑷⟩  O₀

Hold the blob for 3 seconds → pause + chat dialog.
Quick click on blob → click passes through to whatever is behind it.
Right-click tray icon → menu (chat / scan / recenter / quit).

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
from PyQt5.QtCore    import (Qt, QTimer, QPointF, QRectF, QRect,
                              QObject, pyqtSignal, QPoint)
from PyQt5.QtGui     import (QPainter, QColor, QPainterPath, QBrush, QPen,
                              QFont, QRadialGradient, QLinearGradient,
                              QPixmap, QIcon, QRegion)

try:
    import mss
    from PIL import Image
    HAS_MSS = True
except ImportError:
    HAS_MSS = False
    print("[warn] mss / Pillow not found — vision disabled")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE    = 0.0
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("[warn] pyautogui not found — actuation disabled")

try:
    import win32gui, win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("[warn] pywin32 not found — click-forward will use hide/show fallback")

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
POD_CLICK_LAG = 300

BODY_SPEED    = 90
SPRING        = 0.16
DAMPING       = 4.2

WIN_PAD       = 65
WIN_OPACITY   = 0.92    # slightly higher on Windows — DWM compositing is clean

VISION_INT    = 9000
WANDER_MIN    = 2.0
WANDER_MAX    = 5.5

HOLD_SECONDS  = 3.0

# ── Colours ───────────────────────────────────────────────────────────────────

C_BODY_HI  = QColor(118, 45, 215)
C_BODY_LO  = QColor( 40,  5,  88)
C_POD      = QColor( 95, 22, 175)
C_TIP      = QColor(215, 130, 255)
C_SPEC     = QColor(240, 210, 255,  65)
C_GLYPH    = QColor(255, 225, 255)
C_LABEL    = QColor(170, 105, 225)
C_STATE    = QColor(140,  80, 200)
C_HOLD_ARC = QColor(220, 150, 255, 210)


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

        gr = max(5.0, 11.0 * self.phase)
        glow = QRadialGradient(tx, ty, gr * 2.2)
        glow.setColorAt(0.0, QColor(240, 165, 255, 190))
        glow.setColorAt(1.0, QColor(180, 80,  255,   0))
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

        gl = QRadialGradient(self.x, self.y, BODY_R * 2.0)
        gl.setColorAt(0.0, QColor(110, 35, 200, 42))
        gl.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(gl))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(self.x, self.y), BODY_R*2.0, BODY_R*2.0)

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

        sp = QRadialGradient(self.x - BODY_R*0.35, self.y - BODY_R*0.40, BODY_R*0.5)
        sp.setColorAt(0.0, C_SPEC)
        sp.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(sp))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(self.x - BODY_R*0.35, self.y - BODY_R*0.40),
                      BODY_R*0.50, BODY_R*0.38)

        font = QFont("Everson Mono", 21, QFont.Bold)
        p.setFont(font)
        p.setPen(QPen(C_GLYPH))
        fm = p.fontMetrics()
        p.drawText(int(self.x - fm.horizontalAdvance(GLYPH)/2),
                   int(self.y + fm.ascent()/3), GLYPH)

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
        self.signals.done.emit(self._analyze(img))

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
            print("[vision] no key (OPENROUTER_API_KEY or DEEPSEEK_API_KEY)")
            return []
        b64 = base64.b64encode(img_bytes).decode()
        prompt = (
            "You are the eye of an autonomous amoeba navigating a Windows desktop. "
            "Find up to 2 clickable UI elements: buttons, tabs, menu items, links, icons. "
            "Return ONLY raw JSON (no markdown): "
            '[{"label":"short name","x":int,"y":int}] '
            "Coords in the 960x540 image. Return [] if nothing interesting."
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
    response_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint  |
            Qt.Tool
        )
        self.setWindowOpacity(0.95)
        self.setFixedWidth(CHAT_W)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(7)

        self._resp = QLabel("⊙", self)
        self._resp.setWordWrap(True)
        self._resp.setMaximumWidth(CHAT_W - 24)
        self._resp.setFont(QFont("Consolas", 9))
        self._resp.setStyleSheet("color: #dbbfff; background: transparent;")
        self._resp.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self._resp)

        self._inp = QLineEdit(self)
        self._inp.setPlaceholderText("speak to ⊙perator…")
        self._inp.setFont(QFont("Consolas", 10))
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

    def set_thinking_text(self, text: str):
        self._resp.setText(text)
        self.adjustSize()

    def position_near(self, bx: int, by: int, sw: int, sh: int):
        w, h = self.width(), self.height()
        x = bx + BODY_R + 22
        if x + w > sw - 8:
            x = bx - BODY_R - 22 - w
        y = max(8, min(by - h // 2, sh - h - 8))
        self.move(x, y)


# ── API routing ───────────────────────────────────────────────────────────────
# Text: DeepSeek direct (DEEPSEEK_API_KEY) → fallback OpenRouter
# Vision: OpenRouter Qwen-VL (OPENROUTER_API_KEY) — best multimodal available

def _deepseek_key() -> Tuple[str, str]:
    """Return (api_key, base_url) preferring DeepSeek direct."""
    k = os.environ.get("DEEPSEEK_API_KEY", "")
    if k:
        return k, "https://api.deepseek.com/v1"
    k = os.environ.get("OPENROUTER_API_KEY", "")
    return k, "https://openrouter.ai/api/v1"

def _deepseek_model(base_url: str) -> str:
    if "deepseek.com" in base_url:
        return "deepseek-chat"
    return "deepseek/deepseek-chat"   # OpenRouter slug

# ── Agent tools ───────────────────────────────────────────────────────────────

AGENT_TOOLS = [
    {"type": "function", "function": {
        "name": "screenshot",
        "description": "Capture the screen and get a description of visible UI elements.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "click",
        "description": "Click at screen coordinates. The ⊙perator extends a pseudopod to the target.",
        "parameters": {"type": "object", "properties": {
            "x":     {"type": "integer", "description": "Screen X pixel"},
            "y":     {"type": "integer", "description": "Screen Y pixel"},
            "label": {"type": "string",  "description": "Human-readable name of target"},
        }, "required": ["x", "y", "label"]},
    }},
    {"type": "function", "function": {
        "name": "type_text",
        "description": "Type text into the currently focused element.",
        "parameters": {"type": "object", "properties": {
            "text": {"type": "string"},
        }, "required": ["text"]},
    }},
    {"type": "function", "function": {
        "name": "key",
        "description": "Press keyboard keys, e.g. 'enter', 'ctrl+c', 'tab', 'escape', 'ctrl+a'.",
        "parameters": {"type": "object", "properties": {
            "keys": {"type": "string"},
        }, "required": ["keys"]},
    }},
    {"type": "function", "function": {
        "name": "done",
        "description": "Task complete. Report what was accomplished to the user.",
        "parameters": {"type": "object", "properties": {
            "message": {"type": "string"},
        }, "required": ["message"]},
    }},
]


class AgentSignals(QObject):
    status   = pyqtSignal(str)          # interim status to chat bubble
    do_click = pyqtSignal(int, int, str) # (x, y, label) — spawn pseudopod
    do_type  = pyqtSignal(str)
    do_key   = pyqtSignal(str)
    finished = pyqtSignal(str)           # final message to chat bubble


class AgentLoop:
    """Tool-calling agent loop backed by DeepSeek function calling.
    Runs in a background thread; communicates with Qt via AgentSignals.
    Blocks on threading.Event while waiting for pseudopod clicks to complete."""

    MAX_STEPS = 14

    def __init__(self, vision_worker):
        self.signals     = AgentSignals()
        self._vision     = vision_worker
        self._click_done = threading.Event()

    def on_click_complete(self):
        """Qt main thread calls this when the pseudopod click finishes."""
        self._click_done.set()

    def _screen_description(self) -> str:
        img = self._vision._capture()
        if not img:
            return "(screenshot unavailable)"
        targets = self._vision._analyze(img)
        if targets:
            items = ", ".join(f"'{t['label']}' at ({t['x']},{t['y']})"
                              for t in targets[:6])
            return f"Screen shows: {items}"
        return "(screen captured — no distinct UI elements identified)"

    def run(self, task: str, context: str):
        key, base = _deepseek_key()
        if not key:
            self.signals.finished.emit("no API key — I am silent.")
            return
        model = _deepseek_model(base)

        self.signals.status.emit("⊙ looking at screen…")
        screen = self._screen_description()

        messages = [
            {"role": "system",
             "content": OPERATOR_SYSTEM + f"\n\nContext: {context}"},
            {"role": "user",
             "content": f"Task: {task}\n\nCurrent screen: {screen}"},
        ]

        for step in range(self.MAX_STEPS):
            self.signals.status.emit(f"⊙ [{step+1}/{self.MAX_STEPS}]…")
            try:
                r = requests.post(
                    f"{base}/chat/completions",
                    headers={"Authorization": f"Bearer {key}",
                             "Content-Type": "application/json"},
                    json={"model": model, "messages": messages,
                          "tools": AGENT_TOOLS, "tool_choice": "auto"},
                    timeout=25,
                )
                choice = r.json()["choices"][0]
                msg    = choice["message"]
                messages.append(msg)

                tool_calls = msg.get("tool_calls") or []
                if not tool_calls:
                    self.signals.finished.emit(
                        msg.get("content") or "done.")
                    return

                for tc in tool_calls:
                    fn   = tc["function"]["name"]
                    args = json.loads(tc["function"].get("arguments", "{}"))
                    tid  = tc.get("id", fn)

                    if fn == "done":
                        self.signals.finished.emit(
                            args.get("message", "done."))
                        return

                    elif fn == "click":
                        x, y  = int(args["x"]), int(args["y"])
                        label = args.get("label", "target")
                        self.signals.status.emit(f"⊙ → {label}")
                        self._click_done.clear()
                        self.signals.do_click.emit(x, y, label)
                        self._click_done.wait(timeout=10)
                        result = f"clicked '{label}' at ({x},{y})"

                    elif fn == "type_text":
                        text = args.get("text", "")
                        self.signals.do_type.emit(text)
                        time.sleep(0.4)
                        result = f"typed: {text[:60]}"

                    elif fn == "key":
                        keys = args.get("keys", "")
                        self.signals.do_key.emit(keys)
                        time.sleep(0.25)
                        result = f"pressed: {keys}"

                    elif fn == "screenshot":
                        self.signals.status.emit("⊙ looking…")
                        result = self._screen_description()

                    else:
                        result = f"unknown tool: {fn}"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tid,
                        "content": result,
                    })

            except Exception as e:
                self.signals.finished.emit(f"[agent error: {e}]")
                return

        self.signals.finished.emit(f"reached {self.MAX_STEPS} steps — stopping.")


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
        # Windows DWM supports true per-pixel ARGB — no dark background needed
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)

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

        # Vision worker (needed by agent — create first)
        self._vision = VisionWorker(self.sw, self.sh)
        self._vision.signals.done.connect(self._on_vision)
        if not self._no_vision:
            self._vtimer = QTimer(self)
            self._vtimer.timeout.connect(self._vision_scan)
            self._vtimer.start(VISION_INT)

        # Chat bubble
        self._chat         = ChatBubble()
        self._chat.connect_send(self._send_to_llm)
        self._chat_visible = False
        self._chat_paused  = False

        # Agent loop — wired to Qt via signals so threading is safe
        self._agent               = AgentLoop(self._vision)
        self._agent_click_pending = False
        self._agent.signals.status.connect(self._chat.set_thinking_text
                                           if hasattr(self._chat, 'set_thinking_text')
                                           else lambda t: self._chat._resp.setText(t))
        self._agent.signals.finished.connect(self._chat.response_ready)
        self._agent.signals.do_click.connect(self._agent_spawn_pod)
        self._agent.signals.do_type.connect(self.op_type)
        self._agent.signals.do_key.connect(self.op_key)

        # Hold gesture
        self._holding       = False
        self._hold_progress = 0.0
        self._press_time    = 0.0
        self._press_gx      = 0
        self._press_gy      = 0
        self._hold_timer    = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._on_hold_complete)

        self._update_geometry()
        self.show()

        self._anim = QTimer(self)
        self._anim.timeout.connect(self._tick)
        self._anim.start(16)

        print(f"[⊙perator] online   {IG_TYPE}")
        print(f"[⊙perator] screen   {self.sw}×{self.sh}")
        print(f"[⊙perator] vision   {'ON' if not self._no_vision else 'OFF'}")
        print(f"[⊙perator] click    {'ON' if not self._no_click  else 'OFF (dry-run)'}")
        print(f"[⊙perator] hold 3s on blob → chat  |  tray right-click → menu")

    # ── Window geometry ───────────────────────────────────────────────────────

    def _update_geometry(self):
        pad = WIN_PAD
        xs = [self.blob.x]
        ys = [self.blob.y]
        for pod in self.pods:
            tip = pod.tip
            xs.append(tip.x())
            ys.append(tip.y())
        min_x = max(0,       min(xs) - BODY_R - pad)
        max_x = min(self.sw, max(xs) + BODY_R + pad)
        min_y = max(0,       min(ys) - BODY_R - pad)
        max_y = min(self.sh, max(ys) + BODY_R + pad)
        self._win_ox = min_x
        self._win_oy = min_y
        self.setGeometry(int(min_x), int(min_y),
                         int(max_x - min_x), int(max_y - min_y))
        self._update_mask()

    def _update_mask(self):
        """Input mask — only blob circle + pod rects receive mouse events."""
        glow_r = int(BODY_R * 1.8)
        cx = int(self.blob.x - self._win_ox)
        cy = int(self.blob.y - self._win_oy)
        mask = QRegion(cx - glow_r, cy - glow_r,
                       glow_r*2, glow_r*2, QRegion.Ellipse)
        for pod in self.pods:
            if pod.phase < 0.01:
                continue
            ox_w = int(pod.origin.x() - self._win_ox)
            oy_w = int(pod.origin.y() - self._win_oy)
            tx_w = int(pod.tip.x()    - self._win_ox)
            ty_w = int(pod.tip.y()    - self._win_oy)
            pw   = POD_BASE_W + 22
            pr   = QRegion(min(ox_w,tx_w)-pw, min(oy_w,ty_w)-pw,
                           abs(tx_w-ox_w)+pw*2, abs(ty_w-oy_w)+pw*2)
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
        self._hold_timer.start(int(HOLD_SECONDS * 1000))

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton or not self._holding:
            return
        self._holding = False
        self._hold_progress = 0.0
        self._hold_timer.stop()
        if (time.monotonic() - self._press_time) < HOLD_SECONDS - 0.05:
            self._forward_click(self._press_gx, self._press_gy)

    def _on_hold_complete(self):
        self._holding = False
        self._hold_progress = 0.0
        self._toggle_chat()   # toggle: 3s hold opens OR closes/unpauses

    def _forward_click(self, gx: int, gy: int):
        """Pass a quick click through to whatever is behind the blob.
        On Windows: temporarily add WS_EX_TRANSPARENT via win32, then click."""
        if HAS_WIN32:
            hwnd = int(self.winId())
            try:
                ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                       ex | win32con.WS_EX_TRANSPARENT)
                def _click_restore():
                    time.sleep(0.04)
                    if HAS_PYAUTOGUI:
                        pyautogui.click(gx, gy)
                    time.sleep(0.06)
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex)
                threading.Thread(target=_click_restore, daemon=True).start()
                return
            except Exception as e:
                print(f"[forward/win32] {e}")
        # Fallback: hide/show
        self.hide()
        def _restore():
            if HAS_PYAUTOGUI:
                pyautogui.click(gx, gy)
            time.sleep(0.05)
        threading.Thread(target=_restore, daemon=True).start()
        QTimer.singleShot(220, self.show)

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _toggle_chat(self):
        self._chat_visible = not self._chat_visible
        self._chat_paused  = self._chat_visible
        if self._chat_visible:
            self.blob.vx = self.blob.vy = 0.0
            self._chat.position_near(int(self.blob.x), int(self.blob.y), self.sw, self.sh)
            self._chat.show()
            self._chat.raise_()
            self._chat._inp.setFocus()
            print("[⊙perator] paused — chatting")
        else:
            self._chat.hide()
            print("[⊙perator] resuming")

    def _send_to_llm(self, text: str):
        """Dispatch user message to the agent loop."""
        self._chat.set_thinking()
        context = (
            f"state={self.state.name}  "
            f"position=({int(self.blob.x)},{int(self.blob.y)})  "
            f"screen={self.sw}×{self.sh}  "
            + (f"targeting='{self._label}'" if self._label else "idle")
        )
        threading.Thread(
            target=self._agent.run, args=(text, context), daemon=True
        ).start()

    def _agent_spawn_pod(self, x: int, y: int, label: str):
        """Qt-main-thread handler for agent do_click signal — spawn a pseudopod."""
        self._label = label
        self._click_target = (x, y)
        self._agent_click_pending = True
        angle  = math.atan2(y - self.blob.y, x - self.blob.x)
        origin = self.blob.surface_pt(angle)
        self.pods.append(Pseudopod(origin=origin, target=QPointF(x, y)))
        self.state = State.EXTENDING

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
            self.state = State.WANDERING
            return
        t = targets[0]
        self._label = t["label"]
        self._click_target = (t["x"], t["y"])
        print(f"[vision] → ({t['x']},{t['y']}) '{self._label}'")
        self._spawn_pod(t["x"], t["y"])

    def _spawn_pod(self, tx: float, ty: float):
        angle  = math.atan2(ty - self.blob.y, tx - self.blob.x)
        origin = self.blob.surface_pt(angle)
        self.pods.append(Pseudopod(origin=origin, target=QPointF(tx, ty)))
        self.state = State.EXTENDING

    # ── Actuation (pyautogui) ─────────────────────────────────────────────────

    def _do_click(self, x: int, y: int):
        if self._no_click:
            print(f"[actuator/dry] click ({x},{y}) '{self._label}'")
            return
        if HAS_PYAUTOGUI:
            try:
                pyautogui.click(x, y)
                print(f"[actuator] click ({x},{y}) '{self._label}'")
            except Exception as e:
                print(f"[actuator] {e}")

    def op_key(self, keys: str):
        """Send keystrokes — e.g. 'ctrl+c', 'enter', 'f5'."""
        if not HAS_PYAUTOGUI:
            return
        if '+' in keys:
            pyautogui.hotkey(*keys.split('+'))
        else:
            pyautogui.press(keys)
        print(f"[actuator] key '{keys}'")

    def op_type(self, text: str):
        """Type text into the focused window."""
        if HAS_PYAUTOGUI:
            pyautogui.write(text, interval=0.02)
            print(f"[actuator] type '{text[:40]}'")

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _tick(self):
        now = time.monotonic()
        dt  = min(now - self._last, 0.05)
        self._last = now

        if self._holding:
            self._hold_progress = min((now - self._press_time) / HOLD_SECONDS, 1.0)

        if self._chat_paused:
            self.blob.t += dt
            self._update_geometry()
            self.update()
            return

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
                    agent_pending = self._agent_click_pending
                    threading.Thread(target=self._do_click,
                                     args=(cx, cy), daemon=True).start()
                    def _begin_retract(p=pod, ap=agent_pending):
                        p.retracting = True
                        self.state = State.RETRACTING
                        if ap:
                            self._agent_click_pending = False
                            self._agent.on_click_complete()
                    QTimer.singleShot(POD_CLICK_LAG, _begin_retract)
            if pod.done:
                self.pods.remove(pod)
                if self.state == State.RETRACTING:
                    self.state = State.WANDERING
                    self._click_target = None
                    self._label = ""

        self._update_geometry()
        if self._chat_visible:
            self._chat.position_near(int(self.blob.x), int(self.blob.y), self.sw, self.sh)
        self.update()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Clear to transparent — DWM composites the blob over the desktop
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        p.fillRect(self.rect(), Qt.transparent)
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)

        p.translate(-self._win_ox, -self._win_oy)

        for pod in self.pods:
            pod.draw(p)
        self.blob.draw(p)

        # Hold arc
        if self._holding and self._hold_progress > 0.01:
            arc_r   = BODY_R + 9
            arc_pen = QPen(C_HOLD_ARC, 3.5)
            arc_pen.setCapStyle(Qt.RoundCap)
            p.setPen(arc_pen)
            p.setBrush(Qt.NoBrush)
            rect_f = QRectF(self.blob.x - arc_r, self.blob.y - arc_r,
                            arc_r*2, arc_r*2)
            p.drawArc(rect_f, 90*16, int(-self._hold_progress * 360 * 16))

        p.resetTransform()
        sfont = QFont("Consolas", 8)
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

def _make_tray(app: QApplication, widget: Operatoroid) -> QSystemTrayIcon:
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    q = QPainter(px)
    q.setRenderHint(QPainter.Antialiasing)
    q.setBrush(QBrush(QColor(88, 16, 155)))
    q.setPen(QPen(QColor(190, 90, 255), 1.5))
    q.drawEllipse(2, 2, 28, 28)
    q.setPen(QPen(QColor(255, 220, 255)))
    q.setFont(QFont("Consolas", 14, QFont.Bold))
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

    center_act = QAction("⊙  Recenter", menu)
    center_act.triggered.connect(
        lambda: [setattr(widget.blob, 'x', widget.sw/2.0),
                 setattr(widget.blob, 'y', widget.sh/2.0)])
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
    ap = argparse.ArgumentParser(description="⊙perator — autonomous amoebic screen agent (Windows)")
    ap.add_argument("--no-vision", action="store_true")
    ap.add_argument("--no-click",  action="store_true")
    args = ap.parse_args()

    # Enable DPI awareness so the blob isn't blurry on HiDPI displays
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    w = Operatoroid(no_vision=args.no_vision, no_click=args.no_click)
    _tray = _make_tray(app, w)

    signal.signal(signal.SIGINT, lambda *_: app.quit())
    _sig = QTimer(); _sig.timeout.connect(lambda: None); _sig.start(120)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
