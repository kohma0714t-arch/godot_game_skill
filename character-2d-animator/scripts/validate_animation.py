#!/usr/bin/env python3
"""
validate_animation.py
2Dキャラクターアニメーションのフレーム間整合性・重心ジッター・ループ滑らかさを自動検証するスクリプト。
"""

import argparse
import glob
import json
import os
import sys
import warnings
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_opaque_pixels_and_com(img):
    """
    不透明ピクセル数（体積）と重心（Center of Mass）を計算
    """
    img = img.convert("RGBA")
    w, h = img.size
    data = img.getdata()

    count = 0
    sum_x = 0
    sum_y = 0

    for idx, p in enumerate(data):
        if p[3] > 64: # 不透明判定
            x = idx % w
            y = idx // w
            count += 1
            sum_x += x
            sum_y += y

    if count == 0:
        return 0, (w / 2, h / 2)

    return count, (sum_x / count, sum_y / count)

def calculate_frame_diff(img1, img2):
    """
    2つのフレーム間のピクセル差分（距離）を計算
    """
    img1 = img1.convert("RGBA")
    img2 = img2.convert("RGBA")
    
    if img1.size != img2.size:
        return 1.0

    d1 = img1.getdata()
    d2 = img2.getdata()
    total = len(d1)
    diff_count = 0

    for p1, p2 in zip(d1, d2):
        if abs(p1[0] - p2[0]) > 30 or abs(p1[1] - p2[1]) > 30 or abs(p1[2] - p2[2]) > 30 or abs(p1[3] - p2[3]) > 50:
            diff_count += 1

    return diff_count / total

def validate_animation(frame_paths, is_loop=True, max_volume_variance=0.25, max_jitter_dist=3.5):
    """
    アニメーション連番フレームの一括検証
    """
    if len(frame_paths) < 2:
        return {"passed": False, "error": "At least 2 frames required for animation validation"}

    frames = [Image.open(p) for p in frame_paths]
    n = len(frames)

    volumes = []
    centers_of_mass = []

    for img in frames:
        vol, com = get_opaque_pixels_and_com(img)
        volumes.append(vol)
        centers_of_mass.append(com)

    # 1. 体積（シルエットピクセル数）のばらつき検査
    avg_vol = sum(volumes) / n if n > 0 else 1
    vol_deviations = [abs(v - avg_vol) / avg_vol for v in volumes]
    max_vol_dev = max(vol_deviations)
    vol_passed = max_vol_dev <= max_volume_variance

    # 2. 重心の急激なジッター（揺れ）検査
    jitter_issues = []
    for i in range(n - 1):
        com1 = centers_of_mass[i]
        com2 = centers_of_mass[i + 1]
        dist = ((com1[0] - com2[0])**2 + (com1[1] - com2[1])**2)**0.5
        if dist > max_jitter_dist:
            jitter_issues.append({
                "from_frame": i,
                "to_frame": i + 1,
                "distance": round(dist, 2),
                "threshold": max_jitter_dist
            })

    # 3. ループ接続検査（ループモーションの場合）
    loop_issue = None
    if is_loop:
        # 最終コマから最初コマへの重心差
        dist_loop = ((centers_of_mass[-1][0] - centers_of_mass[0][0])**2 + 
                     (centers_of_mass[-1][1] - centers_of_mass[0][1])**2)**0.5
        if dist_loop > max_jitter_dist * 1.5:
            loop_issue = {
                "description": "Large jump between last frame and first frame (pop on loop)",
                "distance": round(dist_loop, 2)
            }

    jitter_passed = len(jitter_issues) == 0 and (loop_issue is None)
    passed = vol_passed and jitter_passed

    reasons = []
    if not vol_passed:
        reasons.append(f"Excessive volume/silhouette variance ({round(max_vol_dev*100, 1)}% > allowed {round(max_volume_variance*100, 1)}%)")
    if len(jitter_issues) > 0:
        reasons.append(f"Detected {len(jitter_issues)} sudden center-of-mass jitter spikes between frames")
    if loop_issue:
        reasons.append(f"Loop seam issue: sudden position jump on loop cycle ({loop_issue['distance']}px)")

    return {
        "passed": passed,
        "frame_count": n,
        "is_loop": is_loop,
        "score": round((1.0 if vol_passed else 0.5) * 0.5 + (1.0 if jitter_passed else 0.5) * 0.5, 3),
        "metrics": {
            "average_volume": round(avg_vol, 1),
            "max_volume_deviation_percent": round(max_vol_dev * 100, 1),
            "centers_of_mass": [{"frame": i, "x": round(c[0], 2), "y": round(c[1], 2)} for i, c in enumerate(centers_of_mass)],
            "jitter_issues": jitter_issues,
            "loop_issue": loop_issue
        },
        "failure_reasons": reasons
    }

def main():
    parser = argparse.ArgumentParser(description="Validate 2D character animation frames")
    parser.add_argument("--frames", "-f", nargs="+", required=True, help="Input animation frame PNG paths or pattern")
    parser.add_argument("--no-loop", action="store_true", help="Specify if animation is one-shot (not looping)")
    parser.add_argument("--max-variance", type=float, default=0.25, help="Max allowed silhouette volume variance (0.1 - 0.5)")
    parser.add_argument("--max-jitter", type=float, default=3.5, help="Max allowed center of mass shift in pixels")
    parser.add_argument("--json-out", help="Output path for validation report JSON")

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

    result = validate_animation(
        files,
        is_loop=not args.no_loop,
        max_volume_variance=args.max_variance,
        max_jitter_dist=args.max_jitter
    )

    result_str = json.dumps(result, indent=2, ensure_ascii=False)
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(result_str)
        print(f"Validation report saved: {args.json_out}")
    else:
        print(result_str)

    sys.exit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()

