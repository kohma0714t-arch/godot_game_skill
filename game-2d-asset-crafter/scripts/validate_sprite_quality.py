#!/usr/bin/env python3
"""
validate_sprite_quality.py
元デザイン画像と抽出・生成された2Dスプライト素材の品質・整合性を自動検査するスクリプト。
- カラーパレット類似度 (Color Palette Consistency)
- 透過境界のクリーンネス (Alpha fringe / noise detection)
- ピクセル密度・グリッド規格整合性 (Pixel consistency & Grid check)
"""

import argparse
import json
import os
import sys
import warnings
from collections import Counter
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_dominant_colors(img, max_colors=16, ignore_transparent=True):
    """
    画像の主要色（RGB）を抽出
    """
    img = img.convert("RGBA")
    data = img.getdata()
    
    colors = []
    for p in data:
        if ignore_transparent and p[3] < 128:
            continue
        # 類似色をグループ化するためRGBを16刻みで丸める
        quantized = (p[0] // 16 * 16, p[1] // 16 * 16, p[2] // 16 * 16)
        colors.append(quantized)
        
    if not colors:
        return []
    
    counter = Counter(colors)
    total = len(colors)
    dominant = [(c, count / total) for c, count in counter.most_common(max_colors)]
    return dominant

def color_dist(c1, c2):
    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2) ** 0.5

def check_palette_similarity(orig_dom, sprite_dom, threshold=60.0):
    """
    スプライトの主要色が元画像の主要色群とどれだけ近いかを検証
    """
    if not orig_dom or not sprite_dom:
        return 1.0, []

    matched_ratio = 0.0
    unmatched_colors = []

    for s_color, s_weight in sprite_dom:
        # 元画像の主要色の中で最も近い色を探す
        min_d = min(color_dist(s_color, o_color) for o_color, _ in orig_dom)
        if min_d <= threshold:
            matched_ratio += s_weight
        else:
            unmatched_colors.append({"color": s_color, "weight": round(s_weight, 3), "min_dist": round(min_d, 1)})

    return min(1.0, matched_ratio), unmatched_colors

def check_alpha_cleanliness(img):
    """
    境界の透過ゴミ（フリンジや半透明ピクセル、孤立ゴミ）を検証
    ドット絵では基本的にアルファ値は 0 または 255 が理想。
    """
    img = img.convert("RGBA")
    data = img.getdata()
    
    semi_transparent_count = 0
    total_pixels = len(data)
    
    for p in data:
        if 0 < p[3] < 255:
            semi_transparent_count += 1
            
    semi_ratio = semi_transparent_count / total_pixels
    # 半透明ピクセルが5%以上あればアンチエイリアス混入（ドット絵としては要警告）
    clean = semi_ratio < 0.05
    return clean, semi_ratio, semi_transparent_count

def check_grid_conformance(img, expected_grid):
    """
    グリッド規格（例: 32x32, 16x16）との整合性を検査
    """
    w, h = img.size
    exp_w, exp_h = expected_grid
    
    # 完全に一致するか、整数の倍数であるか
    exact_match = (w == exp_w and h == exp_h)
    multiple_match = (w % exp_w == 0 and h % exp_h == 0)
    
    return exact_match, multiple_match, (w, h)

def validate_sprite(original_path, sprite_path, expected_grid=None, palette_threshold=0.6):
    """
    1つのスプライトに対して一括検証を実行
    """
    orig_img = Image.open(original_path)
    spr_img = Image.open(sprite_path)
    
    # 1. パレット検査
    orig_dom = get_dominant_colors(orig_img, max_colors=16)
    spr_dom = get_dominant_colors(spr_img, max_colors=12)
    match_ratio, unmatched = check_palette_similarity(orig_dom, spr_dom)
    palette_passed = match_ratio >= palette_threshold
    
    # 2. 透過検査
    alpha_clean, semi_ratio, semi_count = check_alpha_cleanliness(spr_img)
    
    # 3. グリッド検査
    grid_passed = True
    grid_details = {}
    if expected_grid:
        exact, mult, size = check_grid_conformance(spr_img, expected_grid)
        grid_passed = exact or mult
        grid_details = {
            "expected": expected_grid,
            "actual": list(size),
            "exact_match": exact,
            "multiple_match": mult
        }
        
    # 総合判定
    all_passed = palette_passed and alpha_clean and grid_passed
    
    reasons = []
    if not palette_passed:
        reasons.append(f"Palette match ratio ({round(match_ratio*100, 1)}%) is below threshold ({round(palette_threshold*100, 1)}%)")
    if not alpha_clean:
        reasons.append(f"Dirty alpha / excessive semi-transparency detected ({round(semi_ratio*100, 2)}% of pixels are semi-transparent)")
    if not grid_passed:
        reasons.append(f"Grid size mismatch: expected {expected_grid}, got {list(spr_img.size)}")
        
    return {
        "sprite_path": sprite_path,
        "passed": all_passed,
        "score": round((match_ratio * 0.5 + (1.0 - semi_ratio) * 0.3 + (1.0 if grid_passed else 0.0) * 0.2), 3),
        "checks": {
            "palette": {
                "passed": palette_passed,
                "match_ratio": round(match_ratio, 3),
                "unmatched_colors": unmatched[:3]
            },
            "alpha_cleanliness": {
                "passed": alpha_clean,
                "semi_transparent_ratio": round(semi_ratio, 4),
                "semi_transparent_pixels": semi_count
            },
            "grid_conformance": grid_details
        },
        "failure_reasons": reasons
    }

def main():
    parser = argparse.ArgumentParser(description="Validate 2D sprite quality against original design")
    parser.add_argument("--original", "-o", required=True, help="Original design image path")
    parser.add_argument("--sprite", "-s", required=True, help="Extracted / generated sprite image path")
    parser.add_argument("--grid-size", nargs=2, type=int, metavar=('W', 'H'), help="Expected grid dimension (e.g. 32 32)")
    parser.add_argument("--palette-threshold", type=float, default=0.6, help="Minimum palette match ratio (0.0 - 1.0)")
    parser.add_argument("--json-out", help="Path to write JSON validation results")

    args = parser.parse_args()

    if not os.path.exists(args.original):
        print(f"Error: Original image '{args.original}' not found", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.sprite):
        print(f"Error: Sprite image '{args.sprite}' not found", file=sys.stderr)
        sys.exit(1)

    result = validate_sprite(
        args.original,
        args.sprite,
        expected_grid=tuple(args.grid_size) if args.grid_size else None,
        palette_threshold=args.palette_threshold
    )

    result_json = json.dumps(result, indent=2, ensure_ascii=False)
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(result_json)
        print(f"Validation report saved to {args.json_out}")
    else:
        print(result_json)

    # 終了コード: 合格なら0, 不合格なら1
    sys.exit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()
