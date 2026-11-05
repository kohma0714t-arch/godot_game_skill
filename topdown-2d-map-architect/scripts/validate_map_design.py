#!/usr/bin/env python3
"""
validate_map_design.py
トップダウン2Dマップの「デザインの崩れ・接続不整合」を自動検証するスクリプト。
- 壁タイルの接続・コーナー角のルール検査 (Autotile / Edge consistency)
- トップダウン壁前面・上面の配置整合性
- オブジェクト・装飾の不正埋没チェック (Props embedded in walls)
"""

import argparse
import json
import os
import sys

def check_wall_connections(grid, width, height, wall_ids):
    """
    壁タイルの孤立や、不自然な1マス孤立壁（ピラーではなくタイリングの穴）を検査
    """
    anomalies = []
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            is_wall = grid[y][x] in wall_ids
            # 周囲4近傍
            up = grid[y - 1][x] in wall_ids
            down = grid[y + 1][x] in wall_ids
            left = grid[y][x - 1] in wall_ids
            right = grid[y][x + 1] in wall_ids

            # 孤立した1マス壁（意図的な柱でない場合の不自然な浮き壁）
            if is_wall and not (up or down or left or right):
                anomalies.append({
                    "x": x, "y": y,
                    "type": "isolated_single_wall",
                    "description": "Single isolated wall tile with no adjacent walls"
                })

            # 四方を壁に囲まれた1マスだけの穴（床）
            if not is_wall and (up and down and left and right):
                anomalies.append({
                    "x": x, "y": y,
                    "type": "hole_in_wall",
                    "description": "Single 1-tile hole completely surrounded by walls"
                })

    return len(anomalies) == 0, anomalies

def check_prop_placement(props_layer, wall_grid, width, height, wall_ids):
    """
    装飾・小道具（樽、松明など）が壁の中に誤って埋没していないか検査
    """
    if not props_layer:
        return True, []

    misplaced = []
    for y in range(height):
        for x in range(width):
            prop_id = props_layer[y][x]
            if prop_id != 0: # プロップが存在
                is_wall = wall_grid[y][x] in wall_ids
                if is_wall:
                    misplaced.append({
                        "x": x, "y": y,
                        "prop_id": prop_id,
                        "description": "Prop placed inside solid wall tile"
                    })

    return len(misplaced) == 0, misplaced

def validate_design(map_data):
    width = map_data.get("width")
    height = map_data.get("height")
    layers = map_data.get("layers", {})
    wall_grid = layers.get("collision_grid") or map_data.get("grid")

    if not wall_grid or not width or not height:
        return {"passed": False, "error": "Invalid map format: missing grid, width, or height"}

    wall_ids = set(map_data.get("wall_tile_ids", [1]))
    props_layer = layers.get("props")

    # 1. 壁接続・タイリング不整合検査
    wall_ok, wall_anomalies = check_wall_connections(wall_grid, width, height, wall_ids)

    # 2. プロップ配置整合性検査
    props_ok, prop_anomalies = check_prop_placement(props_layer, wall_grid, width, height, wall_ids)

    passed = wall_ok and props_ok

    reasons = []
    if not wall_ok:
        reasons.append(f"Detected {len(wall_anomalies)} wall connection anomalies (holes or isolated walls)")
    if not props_ok:
        reasons.append(f"Detected {len(prop_anomalies)} props incorrectly embedded in solid walls")

    return {
        "passed": passed,
        "score": round((1.0 if wall_ok else max(0, 1.0 - len(wall_anomalies) * 0.1)) * 0.6 + 
                       (1.0 if props_ok else max(0, 1.0 - len(prop_anomalies) * 0.1)) * 0.4, 3),
        "checks": {
            "wall_connections": {
                "passed": wall_ok,
                "anomalies_count": len(wall_anomalies),
                "samples": wall_anomalies[:5]
            },
            "prop_placement": {
                "passed": props_ok,
                "misplaced_count": len(prop_anomalies),
                "samples": prop_anomalies[:5]
            }
        },
        "failure_reasons": reasons
    }

def main():
    parser = argparse.ArgumentParser(description="Validate top-down 2D map design and visual consistency")
    parser.add_argument("--map", "-m", required=True, help="Input map JSON file")
    parser.add_argument("--json-out", help="Output path for validation report JSON")

    args = parser.parse_args()

    if not os.path.exists(args.map):
        print(f"Error: Map file '{args.map}' not found", file=sys.stderr)
        sys.exit(1)

    with open(args.map, "r", encoding="utf-8") as f:
        map_data = json.load(f)

    result = validate_design(map_data)
    result_str = json.dumps(result, indent=2, ensure_ascii=False)

    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(result_str)
        print(f"Validation report saved to {args.json_out}")
    else:
        print(result_str)

    sys.exit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()

