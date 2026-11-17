# -*- coding: utf-8 -*-
"""把 bust/ 里的半身立绘（WebP，带透明）重新内联进 demo/index.html 的 ASSET_PRO。
用法：python art/generated/characters/process_bust.py && python art/generated/characters/embed_bust.py
只替换下列 11 个资产键的内联数据，不动其它图片。
"""
import base64
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..', '..', '..'))
HTML = os.path.join(ROOT, 'demo', 'index.html')
BUST = os.path.join(BASE, 'bust')

# 资产键 -> bust 文件名（不含扩展名）
MAP = {
    'charMai': 'char_maixiaoman',
    'charBook': 'char_sugarbook_v2',
    'charGuku': 'char_guku',
    'charLeiqian': 'char_leiqian',
    'charShenruyi': 'char_shenruyi',
    'charZhoubo': 'char_zhoubo',
    'charDoudou': 'char_doudou',
    'charAjie': 'char_ajie',
    'charYoucha': 'char_youcha',
    'charHaizi': 'char_haizi',
    'charZhanggui': 'char_zhanggui',
}


def main():
    html = open(HTML, encoding='utf-8').read()
    before = len(html.encode('utf-8'))
    for key, stem in MAP.items():
        path = os.path.join(BUST, stem + '.webp')
        if not os.path.exists(path):
            sys.exit(f'缺少半身图：{path}（先跑 process_bust.py）')
        b64 = base64.b64encode(open(path, 'rb').read()).decode('ascii')
        # 整段替换（含 MIME）：只换 base64 会把 webp 数据挂在 image/png 标签下，浏览器解不出来
        pat = re.compile(r"(%s:')(data:image/[^']*)'" % re.escape(key))
        html, n = pat.subn(lambda m: m.group(1) + 'data:image/webp;base64,' + b64 + "'", html)
        if n != 1:
            sys.exit(f'{key} 替换了 {n} 次，预期 1 次')
        print(f'{key:14s} <- {stem}.webp  {os.path.getsize(path)/1024:6.0f}KB')
    open(HTML, 'w', encoding='utf-8', newline='\n').write(html)
    after = len(html.encode('utf-8'))
    print(f'\nindex.html {before/1024/1024:.2f}MB -> {after/1024/1024:.2f}MB')


if __name__ == '__main__':
    main()
