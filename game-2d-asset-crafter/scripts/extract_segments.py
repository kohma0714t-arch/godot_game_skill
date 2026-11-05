#!/usr/bin/env python3
"""
extract_segments.py
2Dゲーム画像からパーツの切り出し、背景透過、オートクロップ、規格サイズへのリサイズを行うスクリプト。
ピクセルアートの特性を崩さないよう、Nearest Neighborリサンプリングを採用。
"""

import argparse
import json
import os
import sys
import warnings
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

def color_distance(c1, c2):
    """2つのRGB色のユークリッド距離を計算"""
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2) ** 0.5

def remove_background(img, bg_color=None, tolerance=30):
    """
    指定背景色（未指定時は四隅の色から自動推定）を透明化
    """
    img = img.convert("RGBA")
    data = img.getdata()
    
    if bg_color is None:
        # 四隅のピクセルから背景色を推定
        w, h = img.size
        corners = [
            img.getpixel((0, 0)),
            img.getpixel((w - 1, 0)),
            img.getpixel((0, h - 1)),
            img.getpixel((w - 1, h - 1))
        ]
        # 最も頻出する色を背景色とする
        bg_color = max(set(corners), key=corners.count)[:3]

    new_data = []
    for item in data:
        # アルファが既に0ならそのまま
        if item[3] == 0:
            new_data.append(item)
            continue
        
        # 色距離判定
        dist = color_distance(item[:3], bg_color)
        if dist <= tolerance:
            new_data.append((item[0], item[1], item[2], 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img

def autocrop(img):
    """透明部分を除去して最小バウンディングボックスにクロップ"""
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img

def fit_to_grid(img, target_w, target_h, anchor="bottom"):
    """
    指定のグリッドサイズ（幅・高さ）に収まるよう配置（デフォルトは下部接地）
    """
    w, h = img.size
    # ターゲットより大きい場合はNearest Neighborでアスペクト比を維持しつつ縮小
    if w > target_w or h > target_h:
        scale = min(target_w / w, target_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.Resampling.NEAREST)
        w, h = img.size

    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    pos_x = (target_w - w) // 2
    if anchor == "bottom":
        pos_y = target_h - h
    elif anchor == "center":
        pos_y = (target_h - h) // 2
    else: # top
        pos_y = 0

    canvas.paste(img, (pos_x, pos_y), img)
    return canvas

def main():
    parser = argparse.ArgumentParser(description="Extract and process 2D sprite segments")
    parser.add_argument("--input", "-i", required=True, help="Input image path")
    parser.add_argument("--output", "-o", required=True, help="Output image path")
    parser.add_argument("--bbox", nargs=4, type=int, metavar=('X1', 'Y1', 'X2', 'Y2'), help="Crop bounding box")
    parser.add_argument("--transparent", action="store_true", help="Remove background color")
    parser.add_argument("--bg-color", nargs=3, type=int, metavar=('R', 'G', 'B'), help="Explicit background RGB")
    parser.add_argument("--tolerance", type=int, default=30, help="Color tolerance for transparency (0-255)")
    parser.add_argument("--autocrop", action="store_true", help="Autocrop transparent padding")
    parser.add_argument("--grid-size", nargs=2, type=int, metavar=('W', 'H'), help="Fit to target grid size (e.g. 32 32)")
    parser.add_argument("--anchor", choices=["center", "bottom", "top"], default="bottom", help="Anchor position in grid")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    img = Image.open(args.input)

    # 1. Bounding Box クロップ
    if args.bbox:
        img = img.crop(args.bbox)

    # 2. 背景透過
    if args.transparent:
        bg = tuple(args.bg_color) if args.bg_color else None
        img = remove_background(img, bg_color=bg, tolerance=args.tolerance)

    # 3. オートクロップ
    if args.autocrop:
        img = autocrop(img)

    # 4. グリッドサイズへのフィッティング
    if args.grid_size:
        img = fit_to_grid(img, args.grid_size[0], args.grid_size[1], anchor=args.anchor)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    img.save(args.output, "PNG")
    print(f"Successfully processed segment: {args.output} (Size: {img.size})")

if __name__ == "__main__":
    main()
