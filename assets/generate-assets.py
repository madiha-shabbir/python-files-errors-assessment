"""
Regenerates the charts and the animated terminal GIFs used in README.md.

Every number is read from real program output stored in ``assets/sample_output``
(produced by actually running the two programs) or computed from attendance.txt.
Nothing is hand-typed or invented.

Run from the repository root:   python assets/generate_assets.py
Requires: matplotlib, pillow
"""
import csv
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SAMPLE = ASSETS / "sample_output"

NAVY, TEAL, AMBER, CORAL, GREY = "#14213d", "#1fb6a6", "#fca311", "#e76f51", "#8d99ae"

# ------------------------------------------------------------------ data ---
with open(SAMPLE / "expenses_after_session2.csv", newline="", encoding="utf-8") as f:
    expenses = [{**r, "amount": float(r["amount"])} for r in csv.DictReader(f)]
categories = {e["category"] for e in expenses}                      # set
totals = {c: sum(e["amount"] for e in expenses if e["category"] == c) for c in categories}
order = sorted(totals, key=totals.get, reverse=True)

raw = [l.strip().title() for l in (ROOT / "attendance.txt").read_text().splitlines() if l.strip()]
raw = [" ".join(n.split()) for n in raw]
freq = Counter(raw)

# --------------------------------------------------------- chart 1: money ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
palette = [TEAL, AMBER, CORAL, NAVY, GREY]
bars = ax1.bar(order, [totals[c] for c in order], color=palette[:len(order)], width=0.6)
for b, c in zip(bars, order):
    ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 60, f"{totals[c]:,.2f}", ha="center", fontsize=10, fontweight="bold")
ax1.set_title("Total expenses by category", fontsize=13, fontweight="bold", color=NAVY)
ax1.set_ylabel("Amount"); ax1.spines[["top", "right"]].set_visible(False)
ax1.set_ylim(0, max(totals.values()) * 1.18)
wedges, _, autot = ax2.pie([totals[c] for c in order], labels=order, colors=palette[:len(order)],
                           autopct="%1.1f%%", startangle=90, pctdistance=0.78,
                           wedgeprops=dict(width=0.42, edgecolor="white"))
for t in autot: t.set_color("white"); t.set_fontweight("bold")
ax2.text(0, 0, f"Total\n{sum(totals.values()):,.2f}", ha="center", va="center", fontsize=12, fontweight="bold", color=NAVY)
ax2.set_title("Share of total spending", fontsize=13, fontweight="bold", color=NAVY)
fig.suptitle(f"Expense Tracker - {len(expenses)} records, {len(categories)} unique categories (from the sample run)", fontsize=10, color=GREY)
fig.tight_layout(); fig.savefig(ASSETS / "expense_summary.png", dpi=160); plt.close(fig)

# ---------------------------------------------------- chart 2: attendance ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.6]})
labels = ["Original\nrecords", "Unique\nstudents", "Duplicates\nremoved"]
vals = [len(raw), len(freq), len(raw) - len(freq)]
bars = ax1.bar(labels, vals, color=[GREY, TEAL, CORAL], width=0.55)
for b, v in zip(bars, vals):
    ax1.text(b.get_x() + b.get_width() / 2, v + 0.4, str(v), ha="center", fontsize=13, fontweight="bold")
ax1.set_title("Cleaning result", fontsize=13, fontweight="bold", color=NAVY)
ax1.set_ylim(0, max(vals) * 1.18); ax1.spines[["top", "right"]].set_visible(False)
names = sorted(freq, key=lambda n: (-freq[n], n))
ax2.barh(names[::-1], [freq[n] for n in names[::-1]], color=[CORAL if freq[n] > 1 else TEAL for n in names[::-1]])
ax2.set_title("Times each student appeared in attendance.txt", fontsize=13, fontweight="bold", color=NAVY)
ax2.set_xlabel("Number of raw entries (coral = duplicated)"); ax2.set_xticks(range(0, max(freq.values()) + 1))
ax2.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(ASSETS / "attendance_summary.png", dpi=160); plt.close(fig)

# ----------------------------------------------------- terminal GIF maker ---
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
W, H, PAD, LH, VIS = 900, 560, 18, 21, 22

def colour(line):
    if re.search(r"\[error\]|\[warning\]|Invalid|cannot be empty", line): return "#ff6b6b"
    if re.search(r"^(Saved|Loaded|Goodbye)|Unique students|GRAND TOTAL", line): return "#7ee787"
    if line.startswith(("=====", "---", "$ ")) or set(line) <= set("=- "): return "#79c0ff"
    return "#e6edf3"

def frame(lines, title, caption):
    img = Image.new("RGB", (W, H), "#0d1117"); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 38], fill="#161b22")
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]): d.ellipse([16 + i * 22, 13, 28 + i * 22, 25], fill=c)
    d.text((W / 2, 19), title, font=FONT, fill="#8b949e", anchor="mm")
    for i, ln in enumerate(lines[-VIS:]):
        d.text((PAD, 50 + i * LH), ln, font=BOLD if ln.startswith("=====") else FONT, fill=colour(ln))
    d.rectangle([0, H - 30, W, H], fill="#161b22"); d.text((PAD, H - 15), caption, font=FONT, fill="#8b949e", anchor="lm")
    return img

def make_gif(all_lines, out, title, caption, step=2, hold=2200):
    frames, shown = [], []
    for i in range(0, len(all_lines), step):
        shown = all_lines[: i + step]; frames.append(frame(shown, title, caption))
    durations = [140] * (len(frames) - 1) + [hold]
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)

# GIF 1: attendance run (full, unedited output)
att = ["$ python attendance_cleaner.py"] + (SAMPLE / "attendance_run.txt").read_text().splitlines()
make_gif(att, ASSETS / "attendance_demo.gif", "attendance_cleaner.py", "Real output - unedited", step=2)

# GIF 2: expense persistence. Menu re-prints are removed to keep it short; all other lines are verbatim.
MENU = {"===== Institute Expense Tracker =====", "1. Add New Expense", "2. Show All Expenses",
        "3. Calculate Total Expenses by Category", "4. Exit", ""}
def strip_menu(text): return [l for l in text.splitlines() if l not in MENU]
s1 = ["$ python expense_tracker.py   # session 1"] + strip_menu((SAMPLE / "session1_transcript.txt").read_text())
s2 = ["", "$ python expense_tracker.py   # session 2 (restart)"] + strip_menu((SAMPLE / "session2_transcript.txt").read_text())
make_gif(s1 + s2, ASSETS / "expense_demo.gif", "expense_tracker.py", "Real output - blank lines and repeated menus removed", step=2, hold=3000)
print("assets generated:", sorted(p.name for p in ASSETS.iterdir() if p.is_file()))
