#!/usr/bin/env python3
"""Builds HAILSTORM.nx: BASIC source + generated ROM entries
(#1 palettes, #2 characters, #15 sound/music)."""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- characters
chars = [[0] * 64 for _ in range(256)]  # 8x8 colour indices per char
reserved = set()  # every char inside a sprite/image block, blank or not


def put_image(base, img):
    """Place an image (list of strings or 2D list, colours 0-3) at sprite
    char base, using LowRes NX's 16-chars-per-row grid for large sprites."""
    h = len(img)
    w = len(img[0])
    for y in range(h):
        for x in range(w):
            v = img[y][x]
            if isinstance(v, str):
                v = 0 if v in ". " else int(v)
            c = base + (y // 8) * 16 + (x // 8)
            reserved.add(c)
            chars[c][(y % 8) * 8 + (x % 8)] = v


def blank(w, h):
    return [[0] * w for _ in range(h)]


SMALL = [".22.", "2332", "2332", ".22."]


def stamp(img, sx, sy, pat=SMALL):
    for y, row in enumerate(pat):
        for x, ch in enumerate(row):
            if ch not in ". " and 0 <= sy + y < len(img) and 0 <= sx + x < len(img[0]):
                img[sy + y][sx + x] = int(ch)


def art(rows, w):
    out = []
    for r in rows:
        r = r.ljust(w, ".")[:w]
        out.append(r)
    return out


# 1: hitbox dot (collision shape - 2x2 px)
put_image(1, art(["........", "........", "........", "...33...", "...33...",
                  "........", "........", "........"], 8))
# 17: focus display (dot + ring) - only shown, never used for collision
put_image(17, art(["..2222..", ".2....2.", "2......2", "2..33..2", "2..33..2",
                   "2......2", ".2....2.", "..2222.."], 8))
# 2: player ship 16x16 (chars 2,3,18,19)
ship = art([
    ".......33.......",
    ".......33.......",
    "......3223......",
    "......2222......",
    ".....122221.....",
    ".....122221.....",
    "....11233211....",
    "...1122332211...",
    "..112222222211..",
    ".11221222212211.",
    "1122111221112211",
    "1221..1221..1221",
    "121...1221...121",
    "11....1111....11",
    "1.....1..1.....1",
    "......3..3......",
], 16)
put_image(2, ship)
# 4: player shot (twin lasers)
put_image(4, art([".3....3.", ".3....3.", ".2....2.", ".2....2.", ".2....2.",
                  ".1....1.", ".1....1.", "........"], 8))
# 5: small bullet
img = blank(8, 8)
stamp(img, 2, 2)
put_image(5, img)
# 6: big bullet (also used as curtain tile 32)
big = art(["..1111..", ".122221.", "12233221", "12333321", "12333321",
           "12233221", ".122221.", "..1111.."], 8)
put_image(6, big)
# 8: quad cluster 16x16 - four bullets in one sprite
img = blank(16, 16)
for sx, sy in [(6, 0), (0, 6), (12, 6), (6, 12)]:
    stamp(img, sx, sy)
put_image(8, img)
# 10: tri cluster 16x16
img = blank(16, 16)
for sx, sy in [(6, 1), (1, 10), (11, 10)]:
    stamp(img, sx, sy)
put_image(10, img)
# 12: ring cluster 24x24 - eight bullets in one sprite
img = blank(24, 24)
for k in range(8):
    a = k * math.pi / 4
    stamp(img, round(11.5 + 9 * math.cos(a) - 1.5), round(11.5 + 9 * math.sin(a) - 1.5))
put_image(12, img)
# 15: spark
put_image(15, art(["3...3...", ".3.2..3.", "..323...", ".22322.2", "...232..",
                   "..3.2.3.", ".3..2..3", "........"], 8))
# 32: curtain bullet tile (BG)
put_image(32, big)
# 33-35: stars
put_image(33, art(["........", "........", "........", "...1....", "........",
                   "........", "........", "........"], 8))
put_image(34, art(["........", "........", "........", "....2...", "........",
                   "........", "........", "........"], 8))
put_image(35, art(["........", "........", "....2...", "...232..", "....2...",
                   "........", "........", "........"], 8))
# 37/38: boss HP bar (top 4 px of the row only - the HUD shows 12 lines)
put_image(37, art(["11111111", "33333333", "22222222", "11111111"] + ["........"] * 4, 8))
put_image(38, art(["11111111", "........", "........", "11111111"] + ["........"] * 4, 8))
# 39: life icon
put_image(39, art(["...33...", "...22...", "..1221..", ".122221.", "12211221",
                   "11....11", "........", "........"], 8))

# Boss 48x48, procedural and symmetric. Quadrants: TL=48 TR=51 BL=96 BR=99
B = blank(48, 48)
cx = 23.5
for y in range(48):
    for x in range(48):
        dx = abs(x - cx)
        col = 0
        # wings
        if 11 <= dx <= 23.5:
            top = 4 + (dx - 11) * 1.1
            bot = 34 - (dx - 11) * 0.9
            if top <= y <= bot:
                col = 1
                if y < top + 1.5 or y > bot - 1.5 or dx > 22.5:
                    col = 2
                elif int(dx) % 4 == 0:
                    col = 2
        # cannons
        if 8 <= dx <= 12 and 30 <= y <= 46:
            col = 1
            if 9.5 <= dx <= 10.5:
                col = 2
            if y >= 45:
                col = 3
        # hull
        e = ((x - cx) / 13.5) ** 2 + ((y - 22) / 21) ** 2
        if e <= 1:
            col = 1 if e > 0.72 else 2
            if e <= 0.72 and (y % 6 == 0) and dx > 6:
                col = 1
        # crest
        if dx < 2.5 and 0 <= y < 8:
            col = 3 if dx < 1 else 1
        # eye
        d = math.hypot(x - cx, y - 23.5)
        if d <= 7.5:
            col = 1
            if 5.2 < d <= 7.5:
                col = 3 if d <= 6.4 else 1
            if d <= 3.2:
                col = 3 if (x - cx) < 0 and (y - 23.5) < 0 else 2
        B[y][x] = col


def quad(img, qx, qy):
    return [row[qx * 24:(qx + 1) * 24] for row in img[qy * 24:(qy + 1) * 24]]


put_image(48, quad(B, 0, 0))
put_image(51, quad(B, 1, 0))
put_image(96, quad(B, 0, 1))
put_image(99, quad(B, 1, 1))

# ---------------------------------------------------------------- stage 2 / bombs
# 7: score gem (cancelled bullet)
put_image(7, art(["...3....", "..323...", ".32223..", "3222223.", ".32223..",
                  "..323...", "...3....", "........"], 8))
# 47: bomb stock icon (HUD)
put_image(47, art(["....33..", "...3....", "..1111..", ".122221.", ".123321.",
                   ".122221.", "..1111..", "........"], 8))
# 40: turret 16x16 (chars 40,41,56,57), 42: wrecked turret (42,43,58,59)
TUR = blank(16, 16)
WRK = blank(16, 16)
for y in range(16):
    for x in range(16):
        d = math.hypot(x - 7.5, y - 6.5)
        if d <= 6.5:
            TUR[y][x] = 1 if d > 5.2 else (3 if (x < 7 and y < 5) else 2)
            WRK[y][x] = 1 if (x + y * 3) % 5 else 0
        if 6 <= x <= 9 and 10 <= y <= 15:
            TUR[y][x] = 3 if x in (6, 9) else 1
        if d <= 2.2:
            TUR[y][x] = 1
        if 6 <= x <= 9 and 11 <= y <= 13 and (x + y) % 2:
            WRK[y][x] = 2
put_image(40, TUR)
put_image(42, WRK)

# Battleship 96x40 drawn as BG tiles. Variant A: closed core, B: open core.
SW, SH = 96, 40
TURRETS = [(4, 6), (22, 20), (58, 20), (76, 6)]   # turret sprite offsets in ship


def ship_img(open_core):
    img = blank(SW, SH)
    for y in range(SH):
        for x in range(SW):
            dx = abs(x - 47.5)
            if y < 10:
                half = 22 + y * 2.6
            elif y <= 26:
                half = 48
            else:
                half = 48 - (y - 26) * 2.4
            if dx > half:
                continue
            col = 2
            if dx > half - 1.5 or y < 1 or y > SH - 2:
                col = 1
            elif y % 8 == 0 or (int(dx) % 12 == 0):
                col = 1
            elif (int(dx) * 7 + y * 3) % 41 == 0:   # symmetric, so tiles can flip
                col = 3
            img[y][x] = col
    # turret mounts
    for tx, ty in TURRETS:
        for y in range(SH):
            for x in range(SW):
                d = math.hypot(x - (tx + 7.5), y - (ty + 6.5))
                if 7 <= d <= 8.5:
                    img[y][x] = 1
    # engines
    for ex in (18, 70):
        for y in range(34, 40):
            for x in range(ex, ex + 8):
                if img[y][x] or y >= 37:
                    img[y][x] = 3 if (x + y) % 2 else 2
    # core (cols 4-7, rows 1-3 = x 32..63, y 8..31)
    for y in range(8, 32):
        for x in range(32, 64):
            lx, ly = x - 32, y - 8
            if not open_core:
                c = 1 if (lx % 8 in (0, 7) or ly % 8 in (0, 7)) else 2
                if lx % 8 in (3, 4) and ly % 8 in (3, 4):
                    c = 3
            else:
                d = math.hypot(x - 47.5, y - 19.5)
                c = 1
                if 7 < d <= 10:
                    c = 3 if d <= 8.5 else 2
                if d <= 4:
                    c = 3
                elif d <= 5.5:
                    c = 2
                if lx in (0, 31) or ly in (0, 23):
                    c = 1
            img[y][x] = c
    return img


# ---------------------------------------------------------------- stage 3 sprites
# Boss 3: 64x32 from ONE drawn 32x32 half (chars 140..) shown twice, the right
# copy with FLIP X. Pods: 16x16 orbs (chars 138,139,154,155).
B3 = blank(32, 32)
for y in range(32):
    for x in range(32):
        dx = 31.5 - x            # distance from the centre line (right edge)
        col = 0
        # swept wing
        if 4 <= y <= 26 and dx <= 31 - (y - 4) * 0.2 and y >= 4 + (dx - 10) * 0.55:
            if y <= 26 - (dx - 6) * 0.35:
                col = 1 if (y + int(dx)) % 6 == 0 else 2
                if y < 4 + (dx - 10) * 0.55 + 1.5:
                    col = 3
        # hull
        e = (dx / 11) ** 2 + ((y - 15) / 15) ** 2
        if e <= 1:
            col = 1 if e > 0.75 else 2
        # cockpit eye on the centre line
        d = math.hypot(dx - 0.5, y - 14)
        if d <= 5.5:
            col = 1 if d > 4 else (3 if d < 2.2 else 2)
        # engine glow
        if dx <= 4 and 28 <= y <= 31:
            col = 3 if (y % 2) else 2
        B3[y][x] = col
put_image(140, B3)
POD = blank(16, 16)
for y in range(16):
    for x in range(16):
        d = math.hypot(x - 7.5, y - 7.5)
        if d <= 7:
            POD[y][x] = 1 if d > 5.5 else (3 if d < 2.5 else 2)
        if d <= 7 and (abs(x - 7.5) < 1 or abs(y - 7.5) < 1) and d > 3:
            POD[y][x] = 3
put_image(138, POD)

# ---------------------------------------------------------------- ship + explosions
# Ship frames (16x16): 2 = upright flame A (above), 144 = upright flame B,
# 146 = banked flame A, 148 = banked flame B. Banking left uses FLIP X.
def ship_frame(base, flame):
    img = [list(r) for r in ship]
    img[15] = list(("......%s..%s......" % (flame, flame)))
    return img


def bank(img):
    """Roll the ship to the right: the near (left) wing stays long and lit,
    the far (right) wing is foreshortened and shaded."""
    out = [["."] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            v = img[y][x]
            if v == ".":
                continue
            if x < 8:
                nx = x + 1
                if v == "1" and x < 6:
                    v = "2"
            else:
                nx = 9 + int((x - 8) * 0.6)
                if v == "2" and x > 9:
                    v = "1"
            if 0 <= nx < 16 and (out[y][nx] == "." or v == "3"):
                out[y][nx] = v
    return ["".join(r) for r in out]


put_image(144, ship_frame(144, "2"))
put_image(146, bank(ship_frame(146, "3")))
put_image(148, bank(ship_frame(148, "2")))

# Explosion frames (16x16): 150 flash, 152 fireball, 70 smoke
def boom(kind):
    img = blank(16, 16)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            n = ((x * 7 + y * 13 + x * y) % 5)          # cheap fixed noise
            if kind == 0:
                if d <= 3.2:
                    img[y][x] = 3
                elif d <= 5 and n:
                    img[y][x] = 2
                elif d <= 6 and (x + y) % 3 == 0:
                    img[y][x] = 3
            elif kind == 1:
                if d <= 7.5 - (n == 0) * 1.5:
                    img[y][x] = 3 if d < 2.5 + n * 0.5 else (2 if d < 5.5 else 1)
            else:
                if 3.5 <= d <= 7.5 and n >= 2:
                    img[y][x] = 1 if n < 4 else 2
    return img


put_image(150, boom(0))
put_image(152, boom(1))
put_image(70, boom(2))

# ---------------------------------------------------------------- tile allocator
used = reserved | {i for i in range(256) if any(chars[i])} | {0}
free = [c for c in list(range(134, 192)) + list(range(54, 64)) + list(range(70, 80))
        + list(range(86, 96)) + list(range(102, 112)) + list(range(118, 128))
        + list(range(20, 24)) + [31]
        if c not in used and c not in (56, 57, 58, 59)]
tiles = []   # (pixels, char)


def flip_px(px):
    return tuple(px[y * 8 + 7 - x] for y in range(8) for x in range(8))


def alloc(px, tol=0, group=None):
    """Return (char, flipx) for an 8x8 tile, reusing an existing tile when it
    matches (optionally mirrored, optionally within tol differing pixels)."""
    fl = flip_px(px)
    for t, c in tiles:
        if t == px:
            return c, 0
        if t == fl:
            return c, 1
    if tol:
        for t, c in group:
            if sum(a != b for a, b in zip(px, t)) <= tol:
                return c, 0
            if sum(a != b for a, b in zip(fl, t)) <= tol:
                return c, 1
    c = free.pop(0)
    chars[c] = list(px)
    tiles.append((px, c))
    if group is not None:
        group.append((px, c))
    return c, 0


def make_map(img, w, h, pal, tol=0, skip_empty=True):
    cells = []
    group = []   # fuzzy matches only reuse tiles from this same image
    for ty in range(h):
        for tx in range(w):
            px = tuple(img[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            if skip_empty and not any(px):
                cells += [0, 0]
                continue
            c, f = alloc(px, tol, group)
            cells += [c, pal | (f << 3)]
    return cells


# Battleship map (ROM #3): variant A rows 0-4, variant B (open core) rows 5-9
MAP_W, MAP_H = SW // 8, SH // 8
map_data = [0, 0, MAP_W, MAP_H * 2]
map_data += make_map(ship_img(False), MAP_W, MAP_H, 3)
map_data += make_map(ship_img(True), MAP_W, MAP_H, 3)
n_ship = len(tiles)
print("battleship tiles:", n_ship)

# Perspective floor (ROM #4): 32x9 cells, shown on screen lines 56-127.
# Grid lines converge on a vanishing point above the horizon; the raster code
# scrolls each line sideways (steering) and recolours colour 1 per line to make
# depth bands rush toward the player.
HZ, FROWS = 56, 9
VPY = HZ - 80
FIMG = [[1] * 256 for _ in range(FROWS * 8)]
for k in range(-4, 5):
    bx = 128 + k * 48
    for yy in range(FROWS * 8):
        t = (HZ + yy - VPY) / (127 - VPY)
        xi = int(round(128 + (bx - 128) * t))
        if 0 <= xi < 256:
            FIMG[yy][xi] = 3
floor_map = [0, 0, 32, FROWS] + make_map(FIMG, 32, FROWS, 5, tol=4, skip_empty=False)
print("floor tiles:", len(tiles) - n_ship, "free chars left:", len(free))


def char_bytes(c):
    px = chars[c]
    lo, hi = [], []
    for y in range(8):
        l = h = 0
        for x in range(8):
            v = px[y * 8 + x]
            l |= (v & 1) << (7 - x)
            h |= ((v >> 1) & 1) << (7 - x)
        lo.append(l)
        hi.append(h)
    return lo + hi


last_char = max(i for i in range(192) if any(chars[i]))
char_data = []
for c in range(last_char + 1):
    char_data += char_bytes(c)

# ---------------------------------------------------------------- palettes
def rgb(r, g, b):
    return r * 16 + g * 4 + b


palettes = [
    [rgb(0, 0, 1), rgb(1, 1, 1), rgb(2, 2, 2), rgb(3, 3, 3)],   # 0 backdrop + stars
    [0, rgb(0, 1, 0), rgb(0, 3, 1), rgb(3, 3, 3)],              # 1 player
    [0, rgb(2, 0, 2), rgb(3, 2, 2), rgb(3, 3, 3)],              # 2 bullets A (pink)
    [0, rgb(2, 0, 0), rgb(3, 1, 0), rgb(3, 3, 0)],              # 3 boss
    [0, rgb(2, 2, 0), rgb(3, 3, 0), rgb(3, 3, 3)],              # 4 player shots
    [0, rgb(1, 0, 2), rgb(2, 1, 3), rgb(3, 3, 3)],              # 5 curtain bullets
    [0, rgb(1, 1, 2), rgb(2, 2, 3), rgb(3, 3, 3)],              # 6 HUD text
    [0, rgb(0, 1, 2), rgb(1, 3, 3), rgb(3, 3, 3)],              # 7 bullets B (cyan)
]
pal_data = [v for p in palettes for v in p]

# ---------------------------------------------------------------- sound
# presets: attr(pw|wave<<4|timeout<<6), length, env1(atk|dec<<4), env2(sus|rel<<4),
#          lfo attr, lfo1(rate|freq<<4), lfo2(vol|pw<<4), reserved
presets = [[0] * 8 for _ in range(16)]
presets[0] = [4 | 2 << 4, 0, 0 | 5 << 4, 5 | 3 << 4, 0, 0, 0, 0]               # bass
presets[1] = [8 | 2 << 4, 0, 1 | 6 << 4, 7 | 5 << 4, 0x10, 9 | 1 << 4, 0, 0]    # lead
presets[2] = [6 | 2 << 4, 0, 0 | 4 << 4, 3 | 2 << 4, 0, 0, 0, 0]               # arp
# sound effects, played with PLAY v,pitch,len SOUND n
presets[3] = [2 | 2 << 4, 0, 0 | 3 << 4, 0 | 1 << 4, 0, 0, 0, 0]               # 3 shot
presets[4] = [8 | 1 << 4, 0, 0 | 6 << 4, 0 | 5 << 4, 0, 0, 0, 0]               # 4 chime / gem
presets[5] = [8 | 3 << 4, 0, 0 | 7 << 4, 0 | 6 << 4, 0, 0, 0, 0]               # 5 explosion
presets[6] = [8 | 3 << 4, 0, 0 | 1 << 4, 0, 0, 0, 0, 0]                        # 6 hit tick
presets[7] = [8 | 3 << 4, 0, 0 | 9 << 4, 0 | 8 << 4, 0x10, 6 | 4 << 4, 0, 0]  # 7 bomb rumble

R = None  # rest/continue


def track(notes, data, ctrl_first=0):
    rows = []
    for i in range(32):
        n = notes[i] if i < len(notes) else 0
        rows += [n or 0, data if n else 0, ctrl_first if i == 0 else 0]
    return rows


# key: D minor  i - VI - VII - V   (Dm Bb C A)
roots = [27, 23, 25, 22]           # D3 Bb2 C3 A2
bass = []
for r in roots:
    bass += [r, r, r + 12, r, r, r + 12, r, r + 12]
lead_a = [58, 0, 0, 54, 0, 51, 0, 54,
          56, 0, 0, 54, 0, 51, 0, 47,
          53, 0, 0, 56, 0, 61, 0, 58,
          58, 0, 0, 0, 56, 0, 53, 50]
lead_b = [63, 0, 58, 0, 54, 0, 58, 0,
          59, 0, 56, 0, 58, 0, 63, 0,
          61, 0, 56, 0, 53, 0, 56, 61,
          58, 0, 0, 0, 0, 0, 0, 0]
arp = []
chords = [[51, 54, 58], [47, 50, 54], [49, 53, 56], [46, 50, 53]]
for ch in chords:
    arp += [ch[0], ch[1], ch[2], ch[1], ch[0], ch[1], ch[2], ch[1]]

# stage 2 song: E minor, faster  (Em C D B)
roots2 = [28, 24, 26, 23]          # E3 C3 D3 B2
bass2 = []
for r in roots2:
    bass2 += [r, r + 12, r, r + 12, r, r + 12, r + 7, r + 12]
lead2_a = [64, 0, 64, 0, 67, 0, 64, 0,
           60, 0, 62, 0, 64, 0, 67, 0,
           69, 0, 67, 0, 66, 0, 62, 0,
           63, 0, 0, 0, 59, 0, 63, 66]
lead2_b = [71, 0, 0, 69, 0, 67, 0, 64,
           72, 0, 0, 71, 0, 67, 0, 64,
           69, 0, 0, 67, 0, 66, 0, 62,
           66, 0, 63, 0, 59, 0, 0, 0]
arp2 = []
for ch in ([52, 55, 59], [48, 52, 55], [50, 54, 57], [47, 51, 54]):
    arp2 += [ch[0], ch[1], ch[2], ch[1]] * 2

# stage 3 song: A minor, driving  (Am F G E)
roots3 = [22, 18, 20, 17]          # A2 F2 G2 E2
bass3 = []
for r in roots3:
    bass3 += [r, r, r + 12, r, r + 12, r, r + 10, r + 12]
lead3_a = [58, 0, 61, 0, 65, 0, 64, 0,
           62, 0, 0, 61, 0, 58, 0, 0,
           60, 0, 62, 0, 64, 0, 67, 0,
           68, 0, 0, 0, 64, 0, 0, 0]
lead3_b = [70, 0, 0, 69, 0, 65, 0, 62,
           65, 0, 0, 64, 0, 62, 0, 61,
           62, 0, 64, 0, 67, 0, 64, 62,
           64, 0, 0, 0, 0, 0, 68, 0]
arp3 = []
for ch in ([46, 49, 53], [42, 46, 49], [44, 48, 51], [41, 45, 48]):
    arp3 += [ch[0], ch[2], ch[1], ch[2]] * 2
# victory fanfare (played with TRACK on voices 0 and 1 after a boss dies)
fan_lead = [58, 0, 58, 61, 0, 0, 65, 0, 0, 0, 70, 0, 0, 0, 0, 0]
fan_bass = [22, 0, 0, 0, 29, 0, 0, 0, 34, 0, 0, 0, 0, 0, 0, 0]

tracks = [
    track(bass, 9 | 0 << 4, 0xE6),   # T0 bass, speed 6 ticks/row
    track(lead_a, 8 | 1 << 4),        # T1
    track(lead_b, 8 | 1 << 4),        # T2
    track(arp, 5 | 2 << 4),           # T3 arpeggio (used in place of lead for intro)
    track(bass2, 9 | 0 << 4, 0xE5),  # T4 stage 2 bass, speed 5
    track(lead2_a, 8 | 1 << 4),       # T5
    track(lead2_b, 8 | 1 << 4),       # T6
    track(arp2, 5 | 2 << 4),          # T7
    track(bass3, 9 | 0 << 4, 0xE5),  # T8 stage 3 bass
    track(lead3_a, 8 | 1 << 4),       # T9
    track(lead3_b, 8 | 1 << 4),       # T10
    track(arp3, 5 | 2 << 4),          # T11
    track(fan_lead, 9 | 1 << 4, 0xE5),  # T12 fanfare lead
    track(fan_bass, 9 | 0 << 4, 0xE5),  # T13 fanfare bass
]
UNUSED = 64
patterns = [[UNUSED] * 4 for _ in range(64)]
patterns[0] = [0 | 0x80, 3, UNUSED, UNUSED]       # loop start
patterns[1] = [0, 1, UNUSED, UNUSED]
patterns[2] = [0, 2, UNUSED, UNUSED]
patterns[3] = [0, 1 | 0x80, UNUSED, UNUSED]       # loop end
patterns[4] = [4 | 0x80, 7, UNUSED, UNUSED]       # stage 2 song, MUSIC 4
patterns[5] = [4, 5, UNUSED, UNUSED]
patterns[6] = [4, 6, UNUSED, UNUSED]
patterns[7] = [4, 5 | 0x80, UNUSED, UNUSED]
patterns[8] = [8 | 0x80, 11, UNUSED, UNUSED]      # stage 3 song, MUSIC 8
patterns[9] = [8, 9, UNUSED, UNUSED]
patterns[10] = [8, 10, UNUSED, UNUSED]
patterns[11] = [8, 9 | 0x80, UNUSED, UNUSED]
sound_data = [b for p in presets for b in p] + [b for p in patterns for b in p]
for t in tracks:
    sound_data += t

# ---------------------------------------------------------------- assemble
def hexblock(data):
    lines = []
    for i in range(0, len(data), 16):
        lines.append("".join("%02X" % b for b in data[i:i + 16]))
    return "\n".join(lines)


src = open(os.path.join(HERE, "hailstorm.bas")).read().rstrip() + "\n"
out = src + "\n"
out += "#1:MAIN PALETTES\n" + hexblock(pal_data) + "\n\n"
out += "#2:MAIN CHARACTERS\n" + hexblock(char_data) + "\n\n"
out += "#3:BATTLESHIP MAP\n" + hexblock(map_data) + "\n\n"
out += "#4:FLOOR MAP\n" + hexblock(floor_map) + "\n\n"
out += "#15:MAIN SOUND\n" + hexblock(sound_data) + "\n"
target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Hailstorm.nx")
open(target, "w").write(out)
print("wrote", target, "chars", last_char + 1, "sound bytes", len(sound_data))
