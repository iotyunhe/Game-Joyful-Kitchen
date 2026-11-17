# -*- coding: utf-8 -*-
"""把立绘统一裁成「半身」，并输出带透明通道的 WebP。

用途：视觉小说对话框右上角的立绘一律半身——全身图塞进那个位置会被缩得
又小又散，和半身角色放一起明显不统一。

裁切点按各角色画稿的实际比例手工标定（自动找脖子在插画上不可靠）：
已经是半身构图的保持 1.0，只处理还会露出腿/尾巴的两张。

为什么用 WebP：早先为了压体积做过调色板量化（P 模式），但 Pillow 的
FASTOCTREE 会把不透明像素并进透明调色板项，导致人物整块发灰半透明
（麦小满翻车过一次）。WebP 保 alpha 又比调色板 PNG 小。

输出到 art/generated/characters/bust/，原图保留在 final/ 不动；
再用 embed_bust.py 内联回 demo/index.html。
"""
import os
import statistics

from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'final')
DST = os.path.join(BASE, 'bust')
# 麦小满的立绘不在 characters/final 里，单独从序章素材取（已经是半身）
EXTRA = {
    'char_maixiaoman': os.path.join(BASE, '..', 'prologue', 'final',
                                    'char_maixiaoman_portrait_v3_halfbody.png'),
}

# 裁到整幅高度的百分之多少（1.0 = 本来就是半身，不动）
CROP = {
    'char_sugarbook_v2': 0.74,   # 幽灵老爷爷：0.74 到胸口偏下，尾巴从 0.78 才开始
    'char_guku': 0.62,           # 斗篷客：0.62 裁在腰带，靴子已切掉
}
DEFAULT_CROP = 1.0
WIDTH = 460          # 统一输出宽度：Q 版头宽差别不大，按宽度对齐头部最稳
QUALITY = 84         # WebP 质量，画面是柔和水彩，84 够用且体积小


def solidify(im):
    """把被上一轮调色板量化弄成半透明的立绘修回不透明。

    final/ 里有 5 张图内部 alpha 只有 46~157（周伯最惨，只有 46），
    渲染出来整块发灰、背景从人物身上透出来。原画的颜色本身是对的，
    只是 alpha 被压低了，按内部中位数等比拉回 255 即可，边缘的柔化保留。
    """
    a = im.getchannel('A')
    inner = a.filter(ImageFilter.MinFilter(9))        # 腐蚀一圈，避开描边
    vals = [v for v in inner.get_flattened_data() if v > 0] if hasattr(inner, 'get_flattened_data') \
        else [v for v in inner.getdata() if v > 0]
    if not vals:
        return im, 255
    med = statistics.median(vals)
    if med >= 245:
        return im, med
    k = 255.0 / med
    im.putalpha(a.point(lambda v: min(255, int(round(v * k)))))
    return im, med


def bust(path, frac, out):
    im = Image.open(path).convert('RGBA')
    im, med = solidify(im)
    im = im.crop(im.split()[3].getbbox())          # 先去透明边
    w, h = im.size
    if frac < 1.0:
        im = im.crop((0, 0, w, int(h * frac)))
        im = im.crop(im.split()[3].getbbox())
        w, h = im.size
    im = im.resize((WIDTH, round(h * WIDTH / w)), Image.LANCZOS)
    im.save(out, 'WEBP', quality=QUALITY, method=6)
    return im.size, os.path.getsize(out), med


def main():
    os.makedirs(DST, exist_ok=True)
    for f in os.listdir(DST):                     # 清掉上一轮的旧产物
        if f.endswith(('.png', '.webp')):
            os.remove(os.path.join(DST, f))
    jobs = [(n[:-4], os.path.join(SRC, n)) for n in sorted(os.listdir(SRC)) if n.endswith('.png')]
    jobs += [(k, v) for k, v in EXTRA.items()]
    total = 0
    for key, path in jobs:
        frac = CROP.get(key, DEFAULT_CROP)
        size, b, med = bust(path, frac, os.path.join(DST, key + '.webp'))
        total += b
        fix = '' if med >= 245 else f'  alpha {med:.0f} -> 255'
        print(f'{key:20s} crop={frac:.2f}  {size[0]}x{size[1]}  {b/1024:4.0f}KB{fix}')
    print(f'合计 {total/1024/1024:.2f} MB')


if __name__ == '__main__':
    main()
