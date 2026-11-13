"""《欢闹厨房》B3-A 常驻场景后处理（可复现）

用法：python process_scenes.py <源PNG> <输出JPG>
链路：清除右下角平台水印（上方等大平坦色块复制 + 羽化）→ 等比缩放到 1080 宽 → 中心裁切到 1080x1920 → 输出 JPG。
约束：不拉伸变形；不修改 source/ 原图；满幅不透明场景不做透明抠图。
"""
from PIL import Image
import sys
import os

TARGET_W, TARGET_H = 1080, 1920
# 平台水印实测落在右下角这一块；四张图均按构图约束把此处留成平坦色块
WM_X, WM_Y = 0.83, 0.945
FADE = 12


def remove_watermark(im):
    w, h = im.size
    x0, y0 = int(w * WM_X), int(h * WM_Y)
    bw, bh = w - x0, h - y0
    if y0 - bh < 0:
        raise RuntimeError("水印区域过高，无法取上方同尺寸色块")
    patch = im.crop((x0, y0 - bh, w, y0))
    mask = Image.new("L", (bw, bh), 255)
    mp = mask.load()
    for yy in range(bh):
        for xx in range(bw):
            d = min(xx, yy)
            if d < FADE:
                mp[xx, yy] = int(255 * d / FADE)
    im.paste(patch, (x0, y0), mask)
    return im, (x0, y0, w, h)


def normalize(im):
    w, h = im.size
    s = TARGET_W / w
    nh = round(h * s)
    im = im.resize((TARGET_W, nh), Image.LANCZOS)
    if nh >= TARGET_H:
        top = (nh - TARGET_H) // 2
        return im.crop((0, top, TARGET_W, top + TARGET_H))
    s = TARGET_H / h
    nw = round(w * s)
    im = im.resize((nw, TARGET_H), Image.LANCZOS)
    left = (nw - TARGET_W) // 2
    return im.crop((left, 0, left + TARGET_W, TARGET_H))


def main():
    if len(sys.argv) != 3:
        raise SystemExit("用法：python process_scenes.py <源PNG> <输出JPG>")
    src, out = sys.argv[1], sys.argv[2]
    if os.path.abspath(src) == os.path.abspath(out):
        raise SystemExit("拒绝：输入输出同路径")
    im = Image.open(src).convert("RGB")
    print("输入", im.size)
    im, box = remove_watermark(im)
    print("水印清除区", box)
    im = normalize(im)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "JPEG", quality=92, subsampling=0)
    print("输出", out, im.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
