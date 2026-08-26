#!/usr/bin/env python3
"""
imscribevideo.py — synchronized video for any Imscription tuple.

As each primitive sounds off, its glyph lights up and joins the growing chain.
Past symbols hold their field colour at dim brightness; future slots show as
dark placeholders so the full 12-slot chain is always visible.

Requires: numpy, scipy, matplotlib, pillow, ffmpeg (in PATH)

Usage:
  python imscribevideo.py --name riemann_hypothesis
  python imscribevideo.py --name psilocybin_peak -o audio/psilocybin_peak.mp4
  python imscribevideo.py --tuple "𐑦 𐑶 𐑾 𐑹 ⋈^ż ⊤^@ 𐑲 ∋^ˌ ⊙ 𐑖 𐑙 𐑭"
  python imscribevideo.py --all-catalog          # batch: every catalog entry
"""

import sys, os, json, argparse, subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties
from scipy.io import wavfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from sounds import (
    synthesize_symbol, normalize, PRIMITIVE_MAP, OLD_ID_MAP,
    FIELD_ORDER, resolve_id, symbol_list,
)

# ── constants ─────────────────────────────────────────────────────────────────
W, H    = 1280, 720
FPS     = 30
SYM_DUR = 0.75     # seconds each symbol sounds
GAP_DUR = 0.12     # silence between symbols
SLOT_S  = SYM_DUR + GAP_DUR   # 0.87 s/slot
N_SLOTS = 12

FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FP        = FontProperties(fname=FONT_PATH)
FP_BOLD   = FontProperties(fname=FONT_BOLD)

BG        = '#0d0d14'
DIM_BG    = '#1a1a26'    # placeholder box fill
DIM_ALPHA = 0.55         # past-symbol opacity

# Field colours — order matches FIELD_ORDER: ⊢ ⊣ > < ⋈ ⊤ ∈ ∋ ⊙ ⊥ ⊞ ⊡
FIELD_COLORS = [
    '#e06060',   # ⊢  red
    '#e09030',   # ⊣  orange
    '#d4c040',   # >  gold
    '#70c840',   # <  lime
    '#40c8a0',   # ⋈  teal
    '#40b0e0',   # ⊤  sky
    '#5070e8',   # ∈  blue
    '#9060e8',   # ∋  violet
    '#c050c8',   # ⊙  magenta
    '#e04878',   # ⊥  pink
    '#a0b838',   # Σ  olive
    '#50c8c8',   # ⊡  cyan
]

FIELD_LABELS = ['Dim','Top','Rel','Par','Fid','Kin','Scp','Grm','Crit','Tmp','Sto','Wnd']

# human-readable sub-names from memory table
HUMAN = {
    '𐑛':'wynn',       '𐑨':'turnthree',  '𐑼':'invomega',    '𐑦':'omega',
    '𐑡':'nrleg',      '𐑰':'invscr',     '𐑥':'bullseye',    '𐑶':'commatailz',  '𐑸':'openo',
    '𐑩':'subrightarrow','𐑑':'ctz',      '𐑽':'downstep',    '𐑾':'lyoghlig',
    '𐑗':'aolig',      '𐑿':'upsilon',    '𐑬':'pipevar',     '𐑯':'subdoublearrow','𐑹':'doublebarpipe',
    '⋈^ì':'beltl',      '⋈^ð':'dh',         '⋈^ż':'hardsign',
    '⊤^-':'frtailgamma','⊤^W':'turnm',      '⊤^@':'schwa',       '⊤^Ù':'teshlig',     '⊤^λ':'lambda',
    '𐑚':'beta',       '𐑔':'gamma',      '𐑲':'revapostrophe',
    '∋^∧':'corner',     '∋^˝':'spleftarrow','∋^ˌ':'secstress',   '∋^Ş':'doublevertline',
    '𐑢':'softsign',   '⊙':'ctyogh',    '𐑮':'closerevepsilon','𐑻':'revepsilon','𐑣':'upstep',
    '𐑓':'closeomega', '𐑒':'toneletterstem','𐑖':'turntwo',  '𐑫':'invscripta',
    '𐑙':'doublebaresh','𐑕':'ctn',       '𐑳':'ltailm',
    '𐑷':'closeepsilon','𐑴':'crtwo',     '𐑭':'dzlig',       '𐑟':'turna',
}

_CATALOG_PATH = os.path.join(_HERE, 'IG_catalog.json')
_CRIT_LEGACY = '⊙'  # phi_hat (catalog key)
_CRIT_MODERN = '⊙'     # odot (sounds.py key)

def _read_crit(entry):
    import unicodedata
    raw = entry.get(_CRIT_LEGACY, entry.get(_CRIT_MODERN, ''))
    raw = unicodedata.normalize('NFC', raw)
    if raw.startswith(_CRIT_LEGACY + '_'):
        return _CRIT_MODERN + raw[len(_CRIT_LEGACY):]
    return raw

def load_catalog():
    with open(_CATALOG_PATH, encoding='utf-8') as f:
        return json.load(f)

def entry_to_ids(entry):
    import unicodedata
    ids = []
    for field in FIELD_ORDER:
        if field == _CRIT_MODERN:
            ids.append(_read_crit(entry))
        else:
            raw = entry.get(field, '')
            ids.append(unicodedata.normalize('NFC', raw))
    return ids

def find_entry(name):
    for e in load_catalog():
        if e.get('name') == name:
            return e
    return None

# ── audio ─────────────────────────────────────────────────────────────────────

def build_audio(ids, fs=44100):
    gap = np.zeros(int(GAP_DUR * fs))
    parts = []
    for gid in ids:
        pair = resolve_id(gid)
        if pair:
            parts.append(synthesize_symbol(pair[0], pair[1], fs, SYM_DUR))
        else:
            parts.append(np.zeros(int(SYM_DUR * fs)))
        parts.append(gap)
    audio = normalize(np.concatenate(parts), peak=0.9)
    return audio, fs

# ── layout math ───────────────────────────────────────────────────────────────
# 2 rows of 6 slots, centred in 1280×720

ROW_COUNT    = 2
COLS         = 6
SLOT_W       = 160   # box width  (px)
SLOT_H       = 110   # box height (px)
H_GAP        = 24    # horizontal gap between boxes
V_GAP        = 36    # vertical   gap between rows

ROW_TOTAL_W  = COLS * SLOT_W + (COLS - 1) * H_GAP   # 1104 px
ROW_X_START  = (W - ROW_TOTAL_W) / 2                 # ~88 px

ROW1_Y       = 155   # top of first row  (px from top of figure)
ROW2_Y       = ROW1_Y + SLOT_H + V_GAP              # top of second row

def slot_rect(i):
    """Return (x, y, w, h) in figure pixels for slot i (0-based)."""
    row, col = divmod(i, COLS)
    x = ROW_X_START + col * (SLOT_W + H_GAP)
    y = ROW1_Y if row == 0 else ROW2_Y
    return x, y, SLOT_W, SLOT_H

# ── frame renderer ────────────────────────────────────────────────────────────

def _hex_to_rgb01(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def _lerp_color(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb01(c1)
    r2, g2, b2 = _hex_to_rgb01(c2)
    return (r1*(1-t)+r2*t, g1*(1-t)+g2*t, b1*(1-t)+b2*t)

def make_figure():
    fig = plt.figure(figsize=(W/100, H/100), dpi=100, facecolor=BG)
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.invert_yaxis()
    ax.set_facecolor(BG)
    ax.axis('off')
    return fig, ax

def render_frame(ax, title, ids, active_idx, t_in_slot, fig):
    """Redraw ax for the given state. active_idx = -1 means intro/outro."""
    ax.cla()
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.invert_yaxis()
    ax.set_facecolor(BG)
    ax.axis('off')

    # ── title ──
    ax.text(W / 2, 55, title.replace('_', ' '),
            ha='center', va='center',
            color='#ccccdd', fontproperties=FP_BOLD, fontsize=22)

    playing = (0 <= active_idx < N_SLOTS) and (t_in_slot < SYM_DUR)

    for i, gid in enumerate(ids):
        x, y, bw, bh = slot_rect(i)
        color = FIELD_COLORS[i]
        past   = (i < active_idx) or (i == active_idx and not playing)
        active = (i == active_idx and playing)
        future = i > active_idx

        # ── pulse: brightness cycles while active ──
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * t_in_slot / SYM_DUR * 1.5) if active else 0.0

        if future:
            box_color = DIM_BG
            border_color = '#2a2a3a'
            text_color  = '#2a2a3a'
            label_color = '#222233'
        elif active:
            bright = 0.85 + 0.15 * pulse
            r, g, b = _hex_to_rgb01(color)
            box_color    = (r * 0.25, g * 0.25, b * 0.25)
            border_color = (r * bright, g * bright, b * bright)
            text_color   = (r * bright, g * bright, b * bright)
            label_color  = '#aaaacc'
        else:  # past
            r, g, b = _hex_to_rgb01(color)
            box_color    = (r * 0.12, g * 0.12, b * 0.12)
            border_color = (r * DIM_ALPHA, g * DIM_ALPHA, b * DIM_ALPHA)
            text_color   = (r * DIM_ALPHA, g * DIM_ALPHA, b * DIM_ALPHA)
            label_color  = '#555566'

        lw = 2.5 if active else (1.5 if past else 0.8)

        # box
        rect = FancyBboxPatch(
            (x, y), bw, bh,
            boxstyle='round,pad=3',
            facecolor=box_color,
            edgecolor=border_color,
            linewidth=lw,
            zorder=2,
        )
        ax.add_patch(rect)

        # field label (top of box, small)
        ax.text(x + bw/2, y + 14,
                FIELD_LABELS[i],
                ha='center', va='center',
                color=label_color, fontproperties=FP, fontsize=8,
                zorder=3)

        # glyph ID — base character + proper typographic subscript
        # Split on '_'; render base right-aligned at cx, sub left-aligned + offset down
        cx   = x + bw / 2
        cy   = y + bh / 2 + 2   # slightly below box-centre (field label sits above)
        fp   = FP_BOLD if active else FP
        fs_b = 28 if active else 23   # base char fontsize
        fs_s = 17 if active else 14   # subscript fontsize
        sub_dy = 9   # pixels below base centre for subscript baseline

        if gid and '_' in gid:
            base_c, sub_c = gid.split('_', 1)
            # base: right-aligned so it ends at cx
            ax.text(cx - 2, cy - 1,
                    base_c,
                    ha='right', va='center',
                    color=text_color, fontproperties=fp, fontsize=fs_b, zorder=3)
            # subscript: left-aligned from cx, dropped down
            ax.text(cx + 2, cy + sub_dy,
                    sub_c,
                    ha='left', va='top',
                    color=text_color, fontproperties=FP, fontsize=fs_s, zorder=3)
        elif gid:
            ax.text(cx, cy, gid,
                    ha='center', va='center',
                    color=text_color, fontproperties=fp, fontsize=fs_b, zorder=3)
        else:
            ax.text(cx, cy, '·',
                    ha='center', va='center',
                    color=text_color, fontproperties=FP, fontsize=18, zorder=3)

        # human name (bottom of box, tiny)
        hname = HUMAN.get(gid, '') if gid else ''
        ax.text(x + bw/2, y + bh - 12,
                hname,
                ha='center', va='center',
                color=label_color, fontproperties=FP, fontsize=7,
                zorder=3)

        # connector arrow between slots (except after last in each row)
        col = i % COLS
        if col < COLS - 1:
            arrow_x = x + bw + 2
            arrow_y = y + bh / 2
            ax.annotate('',
                xy=(arrow_x + H_GAP - 4, arrow_y),
                xytext=(arrow_x, arrow_y),
                arrowprops=dict(
                    arrowstyle='->', color='#2a2a3a' if future else '#444455',
                    lw=1.0,
                ),
                zorder=1,
            )

    # ── current-symbol info bar ──
    info_y = ROW2_Y + SLOT_H + 28
    if 0 <= active_idx < N_SLOTS and playing:
        gid   = ids[active_idx]
        hname = HUMAN.get(gid, '')
        label = FIELD_LABELS[active_idx]
        color = FIELD_COLORS[active_idx]
        # Render  "Label  ·  Base  sub  ·  humanname"  with proper subscript sizing
        if gid and '_' in gid:
            base_c, sub_c = gid.split('_', 1)
        else:
            base_c, sub_c = (gid, '')
        # Build a composite info line using multiple text objects at same y
        info_parts = f'{label}  ·  '
        # measure approximate width of prefix at fontsize 14
        ax.text(W/2, info_y, info_parts, ha='right', va='center',
                color='#888899', fontproperties=FP, fontsize=14)
        # base char
        ax.text(W/2, info_y, base_c, ha='left', va='center',
                color=color, fontproperties=FP_BOLD, fontsize=16)
        # subscript
        if sub_c:
            ax.text(W/2 + 14, info_y + 7, sub_c, ha='left', va='top',
                    color=color, fontproperties=FP, fontsize=11)
        # human name after
        suffix_x = W/2 + 28
        ax.text(suffix_x, info_y, f'  ·  {hname}', ha='left', va='center',
                color='#888899', fontproperties=FP, fontsize=14)

    # ── progress bar ──
    bar_y    = H - 52
    bar_x    = ROW_X_START
    bar_w    = ROW_TOTAL_W
    bar_h    = 6
    progress = (active_idx + t_in_slot / SLOT_S) / N_SLOTS if active_idx >= 0 else 0.0
    progress = np.clip(progress, 0, 1)

    ax.add_patch(mpatches.Rectangle(
        (bar_x, bar_y), bar_w, bar_h,
        facecolor='#222233', edgecolor='none', zorder=2))
    if progress > 0:
        ax.add_patch(mpatches.Rectangle(
            (bar_x, bar_y), bar_w * progress, bar_h,
            facecolor='#6688cc', edgecolor='none', zorder=3))

    # slot tick marks on progress bar
    for k in range(N_SLOTS + 1):
        tx = bar_x + bar_w * k / N_SLOTS
        ax.plot([tx, tx], [bar_y - 3, bar_y + bar_h + 3],
                color='#333344', lw=0.8, zorder=4)

    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    frame = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 4)[:, :, :3]
    return frame

# ── main video generator ──────────────────────────────────────────────────────

def generate_video(title, ids, output_path, fps=FPS):
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    # build audio
    audio, fs = build_audio(ids)
    total_audio_s = len(audio) / fs

    total_frames = int(np.ceil(total_audio_s * fps))

    print(f'  Rendering {total_frames} frames @ {fps}fps ({total_audio_s:.1f}s)…')

    # ffmpeg process: accepts raw RGB24 frames on stdin + WAV audio file
    import tempfile
    tmp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wavfile.write(tmp_wav.name, fs, (audio * 32767).astype(np.int16))

    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}', '-pix_fmt', 'rgb24', '-r', str(fps), '-i', 'pipe:0',
        '-i', tmp_wav.name,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        output_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    fig, ax = make_figure()

    for fi in range(total_frames):
        t = fi / fps
        slot_f    = t / SLOT_S
        active    = int(slot_f)
        t_in_slot = (slot_f - active) * SLOT_S
        if active >= N_SLOTS:
            active = N_SLOTS - 1
            t_in_slot = SLOT_S

        frame = render_frame(ax, title, ids, active, t_in_slot, fig)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    plt.close(fig)
    os.unlink(tmp_wav.name)

    print(f'  → {output_path}')

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--name',  '-n', metavar='NAME',
                        help='Named entry from IG_catalog.json')
    parser.add_argument('--tuple', '-t', metavar='IDS',
                        help='12 space- or comma-separated glyph IDs')
    parser.add_argument('--all-catalog', action='store_true',
                        help='Generate video for every catalog entry')
    parser.add_argument('--output', '-o', metavar='FILE',
                        help='Output MP4 path (default: audio/<name>.mp4)')
    parser.add_argument('--fps', type=int, default=FPS,
                        help=f'Frames per second (default: {FPS})')
    parser.add_argument('--outdir', default='audio',
                        help='Output directory for --all-catalog (default: audio)')
    args = parser.parse_args()

    if args.all_catalog:
        catalog = load_catalog()
        for entry in catalog:
            name = entry.get('name', 'unknown')
            ids  = entry_to_ids(entry)
            out  = os.path.join(args.outdir, f'{name}.mp4')
            print(f'[{name}]')
            try:
                generate_video(name, ids, out, fps=args.fps)
            except Exception as e:
                print(f'  ERROR: {e}')
        return

    if args.name:
        entry = find_entry(args.name)
        if entry is None:
            sys.exit(f"'{args.name}' not found in IG_catalog.json")
        ids   = entry_to_ids(entry)
        title = args.name
    elif args.tuple:
        raw  = args.tuple.replace(',', ' ')
        ids  = raw.split()
        if len(ids) != 12:
            sys.exit(f'--tuple requires exactly 12 IDs, got {len(ids)}')
        title = 'imscription'
    else:
        parser.print_help()
        return

    out = args.output or os.path.join('audio', f'{title}.mp4')
    print(f'Generating video: {title}')
    for i, gid in enumerate(ids):
        print(f'  {FIELD_LABELS[i]:4s}  {gid}')
    generate_video(title, ids, out, fps=args.fps)

if __name__ == '__main__':
    main()
