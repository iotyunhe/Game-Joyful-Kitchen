"""序章图后处理：8 张背景裁水印+压缩 jpeg，2 张人物图品红抠底转透明 png。"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'source')
OUT = os.path.join(BASE, 'final')
os.makedirs(OUT, exist_ok=True)

# 按生成时间顺序：8 背景 + 2 人物
BG = [
    ('2026-11-16T20-54-06', 'pro_bg_0_spoonrank'),
    ('2026-11-16T20-54-49', 'pro_bg_1_bookfall'),
    ('2026-11-16T20-55-12', 'pro_bg_2_oldman'),
    ('2026-11-16T20-55-35', 'pro_bg_3_rules'),
    ('2026-11-16T20-55-58', 'pro_bg_4_smoke'),
    ('2026-11-16T20-56-22', 'pro_bg_5_listen'),
    ('2026-11-16T20-56-45', 'pro_bg_6_frost'),
    ('2026-11-16T20-57-07', 'pro_bg_7_shop'),
]
CHARS = [
    ('2026-11-16T20-57-28', 'char_maixiaoman_portrait'),
    ('2026-11-16T20-57-46', 'char_sugarbook_portrait'),
]

def find(ts):
    for f in os.listdir(SRC):
        if ts in f and f.endswith('.png'):
            return os.path.join(SRC, f)
    raise FileNotFoundError(ts)

# --- 背景：裁掉底部 6% 水印带，缩到宽 720，存 jpeg ---
for ts, name in BG:
    im = Image.open(find(ts)).convert('RGB')
    w, h = im.size
    im = im.crop((0, 0, w, int(h * 0.94)))          # 去底部水印
    nw = 720
    im = im.resize((nw, int(im.height * nw / w)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.jpg')
    im.save(p, 'JPEG', quality=82, optimize=True)
    print('BG ', name, im.size, os.path.getsize(p) // 1024, 'KB')

# --- 人物：品红底抠透明，裁掉右下水印角，缩到 512 ---
def keyout(im):
    """从四角自动采样背景色，按与该色的距离抠图，边缘渐变透明。"""
    im = im.convert('RGBA')
    px = im.load()
    w, h = im.size
    # 取左上角为主背景色（右下角可能有水印，避开）
    BR, BG, BB = px[5,5][:3]
    FULL, EDGE = 48, 105               # 距离 < FULL 全透明，> EDGE 全不透明
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            dist = ((r - BR) ** 2 + (g - BG) ** 2 + (b - BB) ** 2) ** 0.5
            if dist <= FULL:
                px[x, y] = (0, 0, 0, 0)
            elif dist < EDGE:
                alpha = int((dist - FULL) * 255 / (EDGE - FULL))
                px[x, y] = (r, g, b, alpha)
    return im

for ts, name in CHARS:
    im = Image.open(find(ts)).convert('RGBA')
    im = keyout(im)
    # 水印在右下角、人物主体之外：整块矩形清零（原图尺寸 1024，人物书本到 y≈900）
    px = im.load(); w0, h0 = im.size
    for y in range(int(h0 * 0.90), h0):
        for x in range(int(w0 * 0.80), w0):
            px[x, y] = (0, 0, 0, 0)
    nw = 512
    im = im.resize((nw, int(im.height * nw / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.png')
    im.save(p, 'PNG', optimize=True)
    print('CHR', name, im.size, os.path.getsize(p) // 1024, 'KB')
