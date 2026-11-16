"""全角色立绘后处理：逐张采样背景色抠透明 + 去右下水印 + 裁透明边 + 统一 512px 宽。
输入 art/generated/characters/source/，输出 art/generated/characters/final/。
水印处理：右下角区域用背景色覆盖「高亮低饱和」的水印文字像素后再抠图，
避免直接置透明时误伤人物深色描边。
"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'source')
OUT = os.path.join(BASE, 'final')
os.makedirs(OUT, exist_ok=True)

# (源文件名, 输出名)
JOBS = [
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-17-10.png', 'char_sugarbook_v2'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-17-43.png', 'char_guku'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-18-02.png', 'char_leiqian'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-18-20.png', 'char_shenruyi'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-18-39.png', 'char_zhoubo'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-19-17.png', 'char_doudou'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-19-34.png', 'char_ajie'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-19-55.png', 'char_youcha'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-20-13.png', 'char_haizi'),
    ('Cozy_cute_2D_hand_drawn_cartoo_2026-11-16T22-20-32.png', 'char_zhanggui'),
]

FULL, EDGE = 42, 100
# 右下水印矩形（相对宽高）：水印固定在最右下角、纯背景区域，直接涂背景色最干净。
# 经拼图定位：水印约在原图 x>0.78w, y>0.90h，人物主体均不在此区域。
WM_X0, WM_Y0 = 0.78, 0.90

for source, name in JOBS:
    im = Image.open(os.path.join(SRC, source)).convert('RGBA')
    px = im.load()
    w, h = im.size
    # 采样左上背景色（右下被水印污染，不用）
    BR, BG, BB = px[5, 5][:3]

    # 第一步：右下角水印矩形整体涂成背景色（纯背景区，绝不碰人物）
    for y in range(int(h * WM_Y0), h):
        for x in range(int(w * WM_X0), w):
            px[x, y] = (BR, BG, BB, 255)

    # 第二步：按背景色距离抠透明
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            dist = ((r - BR) ** 2 + (g - BG) ** 2 + (b - BB) ** 2) ** 0.5
            if dist <= FULL:
                px[x, y] = (0, 0, 0, 0)
            elif dist < EDGE:
                px[x, y] = (r, g, b, int((dist - FULL) * 255 / (EDGE - FULL)))

    # 第三步：裁透明边
    bbox = im.getbbox()
    if bbox:
        l, t, rr, bb = bbox
        pad = 4
        im = im.crop((max(0, l - pad), max(0, t - pad), min(w, rr + pad), min(h, bb + pad)))

    # 第四步：统一 512px 宽
    nw = 512
    im = im.resize((nw, int(im.height * nw / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.png')
    im.save(p, 'PNG', optimize=True)
    print(f'{name:20s} {str(im.size):12s} {os.path.getsize(p)//1024:4d}KB  BG=({BR},{BG},{BB})')
