"""浅色背景立绘的精确抠图：flood-fill 从四角漫延，只清除与边缘连通的背景色区域。
用于背景色与人物肤色接近的图（邮差小哥 / 放学的孩子），避免整图按色距抠掉肤色。
仍先清右下水印矩形，再 flood fill，最后裁边 + 512px。
"""
import os
from collections import deque
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'source')
OUT = os.path.join(BASE, 'final')

JOBS = [
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-19-55.png', 'char_youcha'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-20-13.png', 'char_haizi'),
]
FULL, EDGE = 26, 52
WM_X0, WM_Y0 = 0.78, 0.90

for source, name in JOBS:
    im = Image.open(os.path.join(SRC, source)).convert('RGBA')
    px = im.load()
    w, h = im.size
    BR, BG, BB = px[5, 5][:3]

    # 清右下水印矩形
    for y in range(int(h * WM_Y0), h):
        for x in range(int(w * WM_X0), w):
            px[x, y] = (BR, BG, BB, 255)

    def is_bg(x, y):
        r, g, b, _ = px[x, y]
        d = ((r - BR) ** 2 + (g - BG) ** 2 + (b - BB) ** 2) ** 0.5
        return d <= EDGE

    # flood fill 从四条边 seeds 出发，只清除连通的背景
    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        idx = y * w + x
        if seen[idx]:
            continue
        seen[idx] = 1
        if not is_bg(x, y):
            continue
        r, g, b, _ = px[x, y]
        d = ((r - BR) ** 2 + (g - BG) ** 2 + (b - BB) ** 2) ** 0.5
        a = 0 if d <= FULL else int((d - FULL) * 255 / (EDGE - FULL))
        px[x, y] = (r, g, b, a)
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))

    bbox = im.getbbox()
    if bbox:
        l, t, rr, bb = bbox
        pad = 4
        im = im.crop((max(0, l - pad), max(0, t - pad), min(w, rr + pad), min(h, bb + pad)))
    nw = 512
    im = im.resize((nw, int(im.height * nw / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.png')
    im.save(p, 'PNG', optimize=True)
    print(f'{name:16s} {str(im.size):12s} {os.path.getsize(p)//1024:4d}KB BG=({BR},{BG},{BB})')
