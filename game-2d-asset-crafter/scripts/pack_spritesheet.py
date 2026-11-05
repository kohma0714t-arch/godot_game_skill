#!/usr/bin/env python3
"""
pack_spritesheet.py
個別の透過PNGスプライトを1枚のスプライトシート（Sprite Sheet）画像に結合し、
Godot 2DおよびPhaser 3向けのアトラスメタデータ（JSON）を出力するスクリプト。
"""

import argparse
import glob
import json
import math
import os
import sys
from PIL import Image

def pack_sprites(sprite_files, out_image_path, out_json_path=None, format_type="phaser", columns=None, padding=2):
    if not sprite_files:
        print("Error: No sprite files provided", file=sys.stderr)
        sys.exit(1)

    images = []
    for f in sprite_files:
        try:
            im = Image.open(f).convert("RGBA")
            name = os.path.splitext(os.path.basename(f))[0]
            images.append({"name": name, "path": f, "image": im, "w": im.width, "h": im.height})
        except Exception as e:
            print(f"Warning: Failed to load {f}: {e}", file=sys.stderr)

    if not images:
        print("Error: No valid images loaded", file=sys.stderr)
        sys.exit(1)

    # セルサイズを最大幅・最大高さに揃える（等幅グリッドスプライトシート）
    max_w = max(item["w"] for item in images)
    max_h = max(item["h"] for item in images)
    cell_w = max_w + padding * 2
    cell_h = max_h + padding * 2

    n = len(images)
    if columns is None or columns <= 0:
        # 正方形に近い列数を自動算出
        columns = max(1, math.ceil(math.sqrt(n)))
    
    rows = math.ceil(n / columns)

    sheet_w = columns * cell_w
    sheet_h = rows * cell_h

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    frames_data = {}
    frames_array = []
    godot_frames = []

    for idx, item in enumerate(images):
        col = idx % columns
        row = idx // columns
        
        # セル内の中央に配置
        x = col * cell_w + padding + (max_w - item["w"]) // 2
        y = row * cell_h + padding + (max_h - item["h"]) // 2
        
        sheet.paste(item["image"], (x, y), item["image"])

        # Phaser Texture Atlas 規格
        frame_meta = {
            "frame": {"x": x, "y": y, "w": item["w"], "h": item["h"]},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": item["w"], "h": item["h"]},
            "sourceSize": {"w": item["w"], "h": item["h"]}
        }
        frames_data[item["name"]] = frame_meta
        frames_array.append({"filename": item["name"], **frame_meta})

        # Godot 用
        godot_frames.append({
            "name": item["name"],
            "region": {"x": x, "y": y, "width": item["w"], "height": item["h"]}
        })

    os.makedirs(os.path.dirname(os.path.abspath(out_image_path)), exist_ok=True)
    sheet.save(out_image_path, "PNG")
    print(f"Sprite sheet created: {out_image_path} ({sheet_w}x{sheet_h}, {n} frames, {columns} cols)")

    if out_json_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_json_path)), exist_ok=True)
        if format_type == "godot":
            meta = {
                "format": "Godot 2D SpriteFrames / TileSet Spec",
                "image": os.path.basename(out_image_path),
                "sheet_size": {"width": sheet_w, "height": sheet_h},
                "cell_size": {"width": cell_w, "height": cell_h},
                "frames": godot_frames
            }
        else: # phaser default
            meta = {
                "frames": frames_data,
                "meta": {
                    "app": "game-2d-asset-crafter",
                    "version": "1.0",
                    "image": os.path.basename(out_image_path),
                    "format": "RGBA8888",
                    "size": {"w": sheet_w, "h": sheet_h},
                    "scale": "1"
                }
            }
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        print(f"Atlas metadata saved: {out_json_path}")

def main():
    parser = argparse.ArgumentParser(description="Pack individual PNG sprites into a spritesheet")
    parser.add_argument("--inputs", "-i", nargs="+", required=True, help="Input sprite PNG files or glob pattern")
    parser.add_argument("--output-image", "-o", required=True, help="Output spritesheet PNG path")
    parser.add_argument("--output-json", "-j", help="Output atlas JSON path")
    parser.add_argument("--format", choices=["phaser", "godot"], default="phaser", help="JSON export format")
    parser.add_argument("--columns", "-c", type=int, help="Number of columns in spritesheet")
    parser.add_argument("--padding", "-p", type=int, default=2, help="Padding in pixels between sprites")

    args = parser.parse_args()

    files = []
    for item in args.inputs:
        matched = glob.glob(item)
        if matched:
            files.extend(matched)
        elif os.path.exists(item):
            files.append(item)

    files = sorted(list(set(files)))
    if not files:
        print("Error: No matching files found", file=sys.stderr)
        sys.exit(1)

    pack_sprites(
        files,
        args.output_image,
        out_json_path=args.output_json,
        format_type=args.format,
        columns=args.columns,
        padding=args.padding
    )

if __name__ == "__main__":
    main()

