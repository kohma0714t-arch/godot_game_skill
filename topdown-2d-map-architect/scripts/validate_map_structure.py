#!/usr/bin/env python3
"""
validate_map_structure.py
トップダウン2Dマップの「構成の崩れ」を自動検証するスクリプト。
- BFS（幅優先探索）による経路到達性テスト（スタート〜ゴール / 宝箱到達率）
- 外周の完全密閉テスト（マップ外脱出バグ防止）
- 孤立床エリアの検知
"""

import argparse
import json
import os
import sys
from collections import deque

def check_perimeter_enclosed(grid, width, height, wall_ids):
    """
    外周（上下左右の境界）が全て壁（wall_ids）で密閉されているか検証
    """
    leaks = []
    # 上端・下端
    for x in range(width):
        if grid[0][x] not in wall_ids:
            leaks.append({"x": x, "y": 0, "tile_id": grid[0][x]})
        if grid[height - 1][x] not in wall_ids:
            leaks.append({"x": x, "y": height - 1, "tile_id": grid[height - 1][x]})
    # 左端・右端
    for y in range(height):
        if grid[y][0] not in wall_ids:
            leaks.append({"x": 0, "y": y, "tile_id": grid[y][0]})
        if grid[y][width - 1] not in wall_ids:
            leaks.append({"x": width - 1, "y": y, "tile_id": grid[y][width - 1]})

    return len(leaks) == 0, leaks

def bfs_reachability(grid, width, height, start_pos, target_positions, walkable_tiles):
    """
    BFSを用いてスタート地点からターゲット地点群への到達可能性を検証
    """
    if not (0 <= start_pos[0] < width and 0 <= start_pos[1] < height):
        return False, {}, set(), ["Start position is out of grid bounds"]

    start_tile = grid[start_pos[1]][start_pos[0]]
    if start_tile not in walkable_tiles:
        return False, {}, set(), [f"Start position ({start_pos[0]}, {start_pos[1]}) is on non-walkable tile {start_tile}"]

    queue = deque([start_pos])
    visited = {tuple(start_pos)}
    distances = {tuple(start_pos): 0}

    while queue:
        cx, cy = queue.popleft()
        current_dist = distances[(cx, cy)]

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    tile = grid[ny][nx]
                    if tile in walkable_tiles:
                        visited.add((nx, ny))
                        distances[(nx, ny)] = current_dist + 1
                        queue.append((nx, ny))

    # 各ターゲットの到達チェック
    targets_status = {}
    unreachable_targets = []
    for t_name, (tx, ty) in target_positions.items():
        if (tx, ty) in visited:
            targets_status[t_name] = {"reached": True, "distance": distances[(tx, ty)]}
        else:
            targets_status[t_name] = {"reached": False, "distance": -1}
            unreachable_targets.append(t_name)

    return len(unreachable_targets) == 0, targets_status, visited, unreachable_targets

def check_isolated_walkable(grid, width, height, visited, walkable_tiles):
    """
    スタート地点から到達できない孤立した歩行可能タイルを検出
    """
    isolated = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] in walkable_tiles and (x, y) not in visited:
                isolated.append({"x": x, "y": y, "tile_id": grid[y][x]})
    return isolated

def validate_structure(map_data):
    width = map_data.get("width")
    height = map_data.get("height")
    grid = map_data.get("layers", {}).get("collision_grid") or map_data.get("grid")
    
    if not grid or not width or not height:
        return {"passed": False, "error": "Invalid map format: missing grid, width, or height"}

    wall_ids = set(map_data.get("wall_tile_ids", [1]))
    walkable_ids = set(map_data.get("walkable_tile_ids", [0, 2, 3]))

    entities = map_data.get("entities", {})
    start_pos = entities.get("spawn", [1, 1])
    targets = {}
    if "exit" in entities:
        targets["exit"] = tuple(entities["exit"])
    for idx, chest in enumerate(entities.get("chests", [])):
        targets[f"chest_{idx}"] = tuple(chest)

    # 1. 外周密閉チェック
    enclosed, leaks = check_perimeter_enclosed(grid, width, height, wall_ids)

    # 2. BFS 到達性チェック
    all_reached, targets_status, visited, unreachable = bfs_reachability(
        grid, width, height, start_pos, targets, walkable_ids
    )

    # 3. 孤立エリアチェック
    isolated_cells = check_isolated_walkable(grid, width, height, visited, walkable_ids)

    passed = enclosed and all_reached and len(isolated_cells) == 0

    reasons = []
    if not enclosed:
        reasons.append(f"Perimeter leak detected at {len(leaks)} boundary points (walls missing)")
    if not all_reached:
        reasons.append(f"Unreachable objectives: {', '.join(unreachable)}")
    if isolated_cells:
        reasons.append(f"Found {len(isolated_cells)} isolated unreachable floor tiles")

    return {
        "passed": passed,
        "score": round((1.0 if enclosed else 0.0) * 0.3 + (1.0 if all_reached else 0.0) * 0.5 + (max(0, 1.0 - len(isolated_cells)/100.0)) * 0.2, 3),
        "checks": {
            "perimeter_enclosed": {
                "passed": enclosed,
                "leaks_count": len(leaks),
                "leaks": leaks[:5]
            },
            "pathfinding_reachability": {
                "passed": all_reached,
                "targets": targets_status,
                "visited_cells_count": len(visited)
            },
            "isolated_floor_check": {
                "passed": len(isolated_cells) == 0,
                "isolated_count": len(isolated_cells),
                "isolated_samples": isolated_cells[:5]
            }
        },
        "failure_reasons": reasons
    }

def main():
    parser = argparse.ArgumentParser(description="Validate top-down 2D map structure and reachability")
    parser.add_argument("--map", "-m", required=True, help="Input map JSON file")
    parser.add_argument("--json-out", help="Output path for validation report JSON")

    args = parser.parse_args()

    if not os.path.exists(args.map):
        print(f"Error: Map file '{args.map}' not found", file=sys.stderr)
        sys.exit(1)

    with open(args.map, "r", encoding="utf-8") as f:
        map_data = json.load(f)

    result = validate_structure(map_data)
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

