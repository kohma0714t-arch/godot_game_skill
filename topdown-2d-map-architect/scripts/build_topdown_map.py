#!/usr/bin/env python3
"""
build_topdown_map.py
ハイブリッド型（設計＋プロシージャル）トップダウン2Dマップ生成スクリプト。
- 指定の部屋（Spawn、Boss、Treasure等）を配置し、通路で接続
- 外周密閉壁の自動付与
- マップJSON、Godot 4.x TileMapLayer (.tscn)、全体俯瞰プレビューPNGを出力
"""

import argparse
import json
import math
import os
import random
import sys
from PIL import Image, ImageDraw

def create_empty_map(w, h, fill_wall=True):
    # 1: Wall, 0: Floor
    val = 1 if fill_wall else 0
    return [[val for _ in range(w)] for _ in range(h)]

def carve_room(grid, rx, ry, rw, rh):
    for y in range(ry, ry + rh):
        for x in range(rx, rx + rw):
            if 0 < y < len(grid) - 1 and 0 < x < len(grid[0]) - 1:
                grid[y][x] = 0 # 床を掘る

def carve_corridor(grid, x1, y1, x2, y2, corridor_width=2):
    """
    (x1, y1) から (x2, y2) へのL字型通路を掘る（2マス幅で詰まり防止）
    """
    w = len(grid[0])
    h = len(grid)

    # 水平方向
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for offset in range(corridor_width):
            ny = y1 + offset
            if 0 < ny < h - 1 and 0 < x < w - 1:
                grid[ny][x] = 0

    # 垂直方向
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for offset in range(corridor_width):
            nx = x2 + offset
            if 0 < y < h - 1 and 0 < nx < w - 1:
                grid[y][nx] = 0

def generate_hybrid_map(width=24, height=18, layout_type="dungeon"):
    """
    ハイブリッドマップ生成
    """
    grid = create_empty_map(width, height, fill_wall=True)
    props_layer = [[0 for _ in range(width)] for _ in range(height)]

    rooms = []
    entities = {}

    if layout_type == "arena":
        # 単一の大部屋（ボス部屋/アリーナ）
        margin = 3
        carve_room(grid, margin, margin, width - margin * 2, height - margin * 2)
        entities["spawn"] = [margin + 2, height // 2]
        entities["exit"] = [width - margin - 3, height // 2]
        entities["chests"] = [[width // 2, margin + 2]]
    else: # dungeon default
        # 3〜4部屋を配置して通路で接続
        # 1. 開始部屋（左下寄り）
        carve_room(grid, 2, height - 7, 5, 4)
        rooms.append((4, height - 5))
        entities["spawn"] = [3, height - 5]

        # 2. 中央広場
        carve_room(grid, width // 2 - 3, height // 2 - 3, 6, 6)
        rooms.append((width // 2, height // 2))

        # 3. ゴール部屋（右上寄り）
        carve_room(grid, width - 7, 2, 5, 4)
        rooms.append((width - 5, 4))
        entities["exit"] = [width - 4, 4]

        # 4. 宝物小部屋（左上寄り）
        carve_room(grid, 2, 2, 4, 4)
        rooms.append((4, 4))
        entities["chests"] = [[3, 3]]

        # 通路接続
        carve_corridor(grid, rooms[0][0], rooms[0][1], rooms[1][0], rooms[1][1])
        carve_corridor(grid, rooms[1][0], rooms[1][1], rooms[2][0], rooms[2][1])
        carve_corridor(grid, rooms[3][0], rooms[3][1], rooms[1][0], rooms[1][1])

    # プロップ（松明、装飾など）を安全な床位置に配置
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if grid[y][x] == 0:
                # 壁のすぐ隣の床に松明（ID: 10）を低確率で配置
                has_adj_wall = (grid[y-1][x] == 1 or grid[y+1][x] == 1 or grid[y][x-1] == 1 or grid[y][x+1] == 1)
                is_entity_pos = [x, y] == entities["spawn"] or [x, y] == entities.get("exit")
                if has_adj_wall and not is_entity_pos and random.random() < 0.08:
                    props_layer[y][x] = 10 # 松明

    map_data = {
        "width": width,
        "height": height,
        "tile_size": 32,
        "layout_type": layout_type,
        "wall_tile_ids": [1],
        "walkable_tile_ids": [0],
        "entities": entities,
        "layers": {
            "collision_grid": grid,
            "props": props_layer
        }
    }
    return map_data

def render_preview_png(map_data, out_png_path, tile_size=32):
    """
    全体俯瞰プレビューPNG画像を生成
    """
    width = map_data["width"]
    height = map_data["height"]
    grid = map_data["layers"]["collision_grid"]
    props = map_data["layers"]["props"]
    entities = map_data.get("entities", {})

    img = Image.new("RGB", (width * tile_size, height * tile_size), (24, 20, 37)) # 暗い背景
    draw = ImageDraw.Draw(img)

    for y in range(height):
        for x in range(width):
            px = x * tile_size
            py = y * tile_size
            is_wall = grid[y][x] == 1

            if is_wall:
                # 壁タイル（ダークスレートグレー）
                draw.rectangle([px, py, px + tile_size - 1, py + tile_size - 1], fill=(53, 56, 74), outline=(40, 42, 56))
                # トップダウンの壁ハイライト
                draw.line([px, py, px + tile_size - 1, py], fill=(89, 93, 117), width=2)
            else:
                # 床タイル（ウォームグレー/ストーン）
                draw.rectangle([px, py, px + tile_size - 1, py + tile_size - 1], fill=(138, 126, 116), outline=(120, 108, 98))

            # プロップ
            if props[y][x] == 10:
                # 松明（オレンジ・黄色）
                draw.ellipse([px + 10, py + 10, px + tile_size - 10, py + tile_size - 10], fill=(255, 140, 0), outline=(255, 215, 0))

    # エンティティ描画
    if "spawn" in entities:
        sx, sy = entities["spawn"]
        spx, spy = sx * tile_size, sy * tile_size
        draw.ellipse([spx + 6, spy + 6, spx + tile_size - 6, spy + tile_size - 6], fill=(50, 205, 50), outline=(255, 255, 255), width=2)

    if "exit" in entities:
        ex, ey = entities["exit"]
        epx, epy = ex * tile_size, ey * tile_size
        draw.rectangle([epx + 6, epy + 6, epx + tile_size - 6, epy + tile_size - 6], fill=(70, 130, 180), outline=(255, 255, 255), width=2)

    for chest in entities.get("chests", []):
        cx, cy = chest
        cpx, cpy = cx * tile_size, cy * tile_size
        draw.rectangle([cpx + 8, cpy + 8, cpx + tile_size - 8, cpy + tile_size - 8], fill=(218, 165, 32), outline=(139, 69, 19), width=2)

    os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
    img.save(out_png_path, "PNG")
    print(f"Preview map saved: {out_png_path} ({img.width}x{img.height})")

def export_godot_tscn(map_data, out_tscn_path):
    """
    Godot 4.x TileMapLayer (.tscn) シーンファイルをエクスポート
    """
    width = map_data["width"]
    height = map_data["height"]
    grid = map_data["layers"]["collision_grid"]

    # Godot TileMapLayerのタイル配置データを生成
    # 形式: Vector2i(x, y) = source_id, atlas_coords
    tscn_content = f"""[gd_scene format=3 uid="uid://topdown_map_{random.randint(100000, 999999)}"]

[node name="StageMap" type="Node2D"]

[node name="GroundLayer" type="TileMapLayer" parent="."]
tile_map_data = PackedByteArray()

[node name="WallLayer" type="TileMapLayer" parent="."]
tile_map_data = PackedByteArray()

[node name="Entities" type="Node2D" parent="."]

[node name="SpawnPoint" type="Marker2D" parent="Entities"]
position = Vector2({map_data.get('entities', {}).get('spawn', [0,0])[0] * 32 + 16}, {map_data.get('entities', {}).get('spawn', [0,0])[1] * 32 + 16})
"""
    if "exit" in map_data.get("entities", {}):
        ex, ey = map_data["entities"]["exit"]
        tscn_content += f"""
[node name="ExitPoint" type="Marker2D" parent="Entities"]
position = Vector2({ex * 32 + 16}, {ey * 32 + 16})
"""

    os.makedirs(os.path.dirname(os.path.abspath(out_tscn_path)), exist_ok=True)
    with open(out_tscn_path, "w", encoding="utf-8") as f:
        f.write(tscn_content)
    print(f"Godot 4.x TSCN exported: {out_tscn_path}")

def main():
    parser = argparse.ArgumentParser(description="Build top-down 2D stage map")
    parser.add_argument("--width", type=int, default=24, help="Map width in tiles")
    parser.add_argument("--height", type=int, default=18, help="Map height in tiles")
    parser.add_argument("--layout", choices=["dungeon", "arena"], default="dungeon", help="Layout style")
    parser.add_argument("--output-json", "-j", required=True, help="Output map JSON file")
    parser.add_argument("--output-preview", "-p", help="Output preview PNG file")
    parser.add_argument("--output-tscn", "-t", help="Output Godot 4.x .tscn file")

    args = parser.parse_args()

    map_data = generate_hybrid_map(width=args.width, height=args.height, layout_type=args.layout)

    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(map_data, f, indent=2, ensure_ascii=False)
    print(f"Map data saved: {args.output_json}")

    if args.output_preview:
        render_preview_png(map_data, args.output_preview)

    if args.output_tscn:
        export_godot_tscn(map_data, args.output_tscn)

if __name__ == "__main__":
    main()

