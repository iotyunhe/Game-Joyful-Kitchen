"""序章麦小满男版立绘后处理：玫红底抠透明 + 去右下水印 + 裁透明边。
替换 2026-11-17 误生成成女孩的 char_maixiaoman_portrait。
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'source')
OUT = os.path.join(BASE, 'final')
os.makedirs(OUT, exist_ok=True)

SOURCE = 'Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T21-23-35.png'
NAME = 'char_maixiaoman_portrait_v2'

im = Image.open(os.path.join(SRC, SOURCE)).convert('RGBA')
px = im.load()
w, h = im.size

BR, BG, BB = px[5, 5][:3]
FULL, EDGE = 42, 100
for y in range(h):
    for x in range(w):
        if x > int(w * 0.82) and y > int(h * 0.89):
            px[x, y] = (0, 0, 0, 0)
            continue
        r, g, b, _ = px[x, y]
        dist = ((r - BR) ** 2 + (g - BG) ** 2 + (b - BB) ** 2) ** 0.5
        if dist <= FULL:
            px[x, y] = (0, 0, 0, 0)
        elif dist < EDGE:
            px[x, y] = (r, g, b, int((dist - FULL) * 255 / (EDGE - FULL)))

bbox = im.getbbox()
if bbox:
    l, t, rr, bb = bbox
    pad = 4
    im = im.crop((max(0, l - pad), max(0, t - pad), min(w, rr + pad), min(h, bb + pad)))

nw = 512
im = im.resize((nw, int(im.height * nw / im.width)), Image.LANCZOS)
p = os.path.join(OUT, NAME + '.png')
im.save(p, 'PNG', optimize=True)
print('CHAR', NAME, im.size, os.path.getsize(p) // 1024, 'KB', 'BG', (BR, BG, BB), 'bbox', bbox)
