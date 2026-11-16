"""天降旧书贴图后处理：玫红底抠透明 + 去右下水印 + 裁透明边。
可复现：source/ 为生成原图，final/ 为透明底成品。
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'source')
OUT = os.path.join(BASE, 'final')
os.makedirs(OUT, exist_ok=True)

SOURCE = 'Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T21-18-43.png'
NAME = 'pro_book_fallen_v1'

im = Image.open(os.path.join(SRC, SOURCE)).convert('RGBA')
px = im.load()
w, h = im.size

# 从左上角采样背景色（右下角有水印，避开）
BR, BG, BB = px[5, 5][:3]
FULL, EDGE = 42, 100
for y in range(h):
    for x in range(w):
        # 右下角水印：整块矩形清零（水印在透明背景区，主体在画面中部）
        if x > int(w * 0.82) and y > int(h * 0.89):
            px[x, y] = (0, 0, 0, 0)
            continue
        r, g, b, _ = px[x, y]
        dist = ((r - BR) ** 2 + (g - BG) ** 2 + (b - BB) ** 2) ** 0.5
        if dist <= FULL:
            px[x, y] = (0, 0, 0, 0)
        elif dist < EDGE:
            alpha = int((dist - FULL) * 255 / (EDGE - FULL))
            px[x, y] = (r, g, b, alpha)

# 裁透明边，四周留 4px 余量
bbox = im.getbbox()
if bbox:
    l, t, rr, bb = bbox
    pad = 4
    im = im.crop((max(0, l - pad), max(0, t - pad), min(w, rr + pad), min(h, bb + pad)))

# 缩到宽 480 保留细节（demo 里 CSS 显示约 200px）
nw = 480
im = im.resize((nw, int(im.height * nw / im.width)), Image.LANCZOS)

p = os.path.join(OUT, NAME + '.png')
im.save(p, 'PNG', optimize=True)
print('BOOK', NAME, im.size, os.path.getsize(p) // 1024, 'KB')
print('BG sampled', (BR, BG, BB), 'bbox', bbox)
