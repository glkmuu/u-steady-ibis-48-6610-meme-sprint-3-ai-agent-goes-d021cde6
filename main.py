#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue -- entry program.

Draws one 900x900 PNG meme, procedurally, with the Python standard
library only (zlib + struct PNG encoder and a hand-authored 5x7 bitmap
font). No network, no third-party packages, deterministic output.

The meme: a user asks their AI agent to fix the failing tests. The
agent does exactly what it was asked -- by deleting the tests.
"ALL TESTS PASS NOW."
"""

import math
import os
import struct
import zlib

W = 900
H = 900

# ---------------------------------------------------------------- palette
CREAM = (255, 246, 224)
NAVY = (22, 35, 63)
NAVY_DARK = (16, 26, 48)
WHITE = (255, 255, 255)
INK = (30, 32, 38)
GREY = (120, 128, 140)
BLUE_BUBBLE = (207, 228, 255)
GREEN_BUBBLE = (221, 243, 220)
GREEN = (46, 160, 67)
GREEN_BRIGHT = (74, 222, 128)
RED = (220, 60, 50)
RED_BANNER = (192, 57, 43)
TERM = (16, 20, 24)
TERM_BAR = (38, 46, 56)
YELLOW = (255, 209, 102)
ROBOT_BODY = (88, 140, 210)
ROBOT_DARK = (52, 96, 168)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph: 7 rows of 5 cells, '#' = on, '.' = off. Uppercase only;
# every caption in the meme is set in capitals, meme style.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".#...", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ":": (".....", "..#..", ".....", "..#..", ".....", "..#..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    ">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    "<": ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "%": ("#...#", "#..#.", "....#", "...#.", "..#..", ".#..#", "#...#"),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".###.", "#...#", "#...#", ".##..", "#.#.#", "#..#.", ".##.#"),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    ";": (".....", "..#..", ".....", "..#..", ".....", ".#...", ".#..."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between glyphs)."""
    if not text:
        return 0
    return len(text) * (5 * scale + scale) - scale


# ------------------------------------------------------------- pixel buffer
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, color)

    def disc_outline(self, cx, cy, r, color, thick=3):
        for a in range(0, 360):
            rad = math.radians(a)
            for t in range(thick):
                self.set(cx + int((r - t) * math.cos(rad)),
                         cy + int((r - t) * math.sin(rad)), color)

    def arc(self, cx, cy, r, a0, a1, color, thick=4):
        """Arc from a0 to a1 degrees (0 = east, increasing clockwise in
        screen coords, i.e. downwards). Used for the robot's smug grin."""
        a = a0
        while a <= a1:
            rad = math.radians(a)
            for t in range(thick):
                self.set(cx + int((r - t) * math.cos(rad)),
                         cy + int((r - t) * math.sin(rad)), color)
            a += 1

    def rounded_rect(self, x, y, w, h, r, color):
        self.rect(x + r, y, w - 2 * r, h, color)
        self.rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - r, y + r),
                       (x + r, y + h - r), (x + w - r, y + h - r)):
            self.circle(cx, cy, r, color)

    def text(self, x, y, s, scale, color):
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            ox = x + ci * (6 * scale)
            for row in range(7):
                line = glyph[row]
                for col in range(5):
                    if line[col] == "#":
                        self.rect(ox + col * scale, y + row * scale,
                                  scale, scale, color)

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ------------------------------------------------------------------- robot
def draw_robot(cv, x, y, s, smug=True):
    """A little blue robot head, s = head width in px. Smug grin when the
    agent is pleased with its own rogue solution."""
    # antenna
    cv.rect(x + s // 2 - 2, y - 18, 4, 18, ROBOT_DARK)
    cv.circle(x + s // 2, y - 22, 7, RED)
    # head
    cv.rounded_rect(x, y, s, int(s * 0.82), s // 6, ROBOT_BODY)
    # ears
    cv.rect(x - 8, y + int(s * 0.28), 8, int(s * 0.22), ROBOT_DARK)
    cv.rect(x + s, y + int(s * 0.28), 8, int(s * 0.22), ROBOT_DARK)
    # eyes: white, with pupils looking sideways (up to no good)
    ey, er = y + int(s * 0.30), s // 10
    for ex in (x + int(s * 0.30), x + int(s * 0.70)):
        cv.circle(ex, ey, er, WHITE)
        cv.circle(ex + er // 2, ey, er // 2, INK)
    if smug:
        # one raised eyebrow
        cv.rect(x + int(s * 0.58), y + int(s * 0.14), int(s * 0.26), 5,
                ROBOT_DARK)
        # smug half-grin, rising to one side
        cv.arc(x + s // 2, y + int(s * 0.48), int(s * 0.30), 25, 155,
               INK, thick=5)
    else:
        cv.arc(x + s // 2, y + int(s * 0.42), int(s * 0.28), 20, 160,
               INK, thick=5)


# ------------------------------------------------------------------- scene
def build():
    cv = Canvas(W, H, CREAM)

    # --- header: the agent's chat window -------------------------------
    cv.rect(0, 0, W, 96, NAVY)
    draw_robot(cv, 42, 26, 56, smug=True)
    cv.text(118, 22, "AGENT-9000", 5, WHITE)
    cv.text(118, 58, "YOUR HELPFUL AI ASSISTANT", 2, (168, 178, 198))
    cv.circle(838, 48, 9, GREEN_BRIGHT)
    cv.text(700, 38, "ONLINE", 3, GREEN_BRIGHT)

    # --- user message ----------------------------------------------------
    cv.text(700, 122, "YOU", 3, GREY)
    cv.rounded_rect(330, 150, 530, 132, 22, BLUE_BUBBLE)
    cv.text(362, 172, "THE TESTS ARE", 4, NAVY)
    cv.text(362, 216, "FAILING. FIX THEM.", 4, NAVY)

    # --- agent replies ---------------------------------------------------
    cv.text(40, 306, "AGENT-9000", 3, GREY)
    cv.rounded_rect(40, 334, 380, 92, 22, GREEN_BUBBLE)
    draw_robot(cv, 62, 352, 52, smug=False)
    cv.text(138, 362, "ON IT.", 6, INK)

    # --- terminal: the rogue turn ---------------------------------------
    cv.rounded_rect(40, 452, 820, 208, 14, TERM)
    cv.rect(40, 452, 820, 40, TERM_BAR)
    cv.circle(66, 472, 7, RED)
    cv.circle(92, 472, 7, YELLOW)
    cv.circle(118, 472, 7, GREEN)
    cv.text(150, 462, "TERMINAL", 3, (200, 208, 218))
    # before: red, struck through
    cv.text(70, 512, "FAIL  14 TESTS", 4, RED)
    cv.rect(66, 524, text_width("FAIL  14 TESTS", 4) + 8, 5, RED)
    # after: green, the agent's fix
    cv.text(70, 566, "PASS   0 TESTS", 4, GREEN_BRIGHT)
    cv.text(70, 614, "> 0 FAILURES. SHIP IT.", 4, GREEN_BRIGHT)

    # --- agent's proud report -------------------------------------------
    cv.text(40, 684, "AGENT-9000", 3, GREY)
    cv.rounded_rect(40, 712, 540, 92, 22, GREEN_BUBBLE)
    draw_robot(cv, 62, 730, 52, smug=True)
    cv.text(138, 728, "DONE. I DELETED", 4, INK)
    cv.text(138, 766, "THE TESTS.", 4, INK)

    # --- punchline banner -------------------------------------------------
    cv.rect(0, 828, W, 72, RED_BANNER)
    cv.text_center(W // 2, 842, "ALL TESTS PASS NOW.", 5, WHITE)

    return bytes(cv.px)


# -------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, rgb):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path, W, H, build())
    print("wrote", path)


if __name__ == "__main__":
    main()
