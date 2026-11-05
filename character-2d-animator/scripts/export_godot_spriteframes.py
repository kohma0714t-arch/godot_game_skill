#!/usr/bin/env python3
"""
export_godot_spriteframes.py
アニメーションフレーム群から Godot 4.x 向けの SpriteFrames リソース (.tres) を自動生成するスクリプト。
"""

import argparse
import glob
import os
import random
import sys

def generate_spriteframes_tres(animation_configs, output_tres_path):
    """
    animation_configs: list of dict:
      {
        "name": "walk_down",
        "speed": 10.0,
        "loop": True,
        "frames": ["path/to/frame0.png", "path/to/frame1.png"]
      }
    """
    ext_resources = []
    anim_entries = []

    res_id = 1
    file_to_res_id = {}

    for anim in animation_configs:
        frame_entries = []
        for fpath in anim["frames"]:
            norm_path = fpath.replace("\\", "/")
            if norm_path not in file_to_res_id:
                file_to_res_id[norm_path] = res_id
                ext_resources.append((res_id, norm_path))
                res_id += 1
            
            frame_entries.append(f"""{{
"duration": 1.0,
"texture": ExtResource("{file_to_res_id[norm_path]}")
}}""")

        frames_str = ",\n".join(frame_entries)
        loop_str = "true" if anim.get("loop", True) else "false"
        speed_val = float(anim.get("speed", 10.0))
        anim_name = anim["name"]

        anim_entries.append(f"""{{
"frames": [
{frames_str}
],
"loop": {loop_str},
"name": &"{anim_name}",
"speed": {speed_val}
}}""")

    ext_res_str = "\n".join([
        f'[ext_resource type="Texture2D" path="res://{p}" id="{rid}"]'
        for rid, p in ext_resources
    ])
    animations_str = ",\n".join(anim_entries)

    tres_content = f"""[gd_resource type="SpriteFrames" format=3 uid="uid://spriteframes_{random.randint(100000, 999999)}"]

{ext_res_str}

[resource]
animations = [
{animations_str}
]
"""

    os.makedirs(os.path.dirname(os.path.abspath(output_tres_path)), exist_ok=True)
    with open(output_tres_path, "w", encoding="utf-8") as f:
        f.write(tres_content)
    print(f"Godot 4.x SpriteFrames resource generated: {output_tres_path} ({len(animation_configs)} animations)")

def main():
    parser = argparse.ArgumentParser(description="Export Godot 4.x SpriteFrames (.tres) from frame sequences")
    parser.add_argument("--name", "-n", required=True, help="Animation state name (e.g. walk_down)")
    parser.add_argument("--frames", "-f", nargs="+", required=True, help="Frame PNG paths")
    parser.add_argument("--speed", type=float, default=10.0, help="Playback speed in FPS")
    parser.add_argument("--no-loop", action="store_true", help="Set animation loop to false")
    parser.add_argument("--output", "-o", required=True, help="Output .tres file path")

    args = parser.parse_args()

    files = []
    for item in args.frames:
        matched = glob.glob(item)
        if matched:
            files.extend(matched)
        elif os.path.exists(item):
            files.append(item)

    files = sorted(list(set(files)))
    if not files:
        print("Error: No frame files found", file=sys.stderr)
        sys.exit(1)

    config = [{
        "name": args.name,
        "speed": args.speed,
        "loop": not args.no_loop,
        "frames": files
    }]

    generate_spriteframes_tres(config, args.output)

if __name__ == "__main__":
    main()

