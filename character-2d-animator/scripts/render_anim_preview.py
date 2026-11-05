#!/usr/bin/env python3
"""
render_anim_preview.py
連番透過PNGスプライトから、ループプレビューGIFおよび横並びストリップ画像を生成するスクリプト。
ピクセルアートのボケを防止するため、Nearest Neighborで適切に拡大（Scale 2x, 4x）可能。
"""

import argparse
import glob
import os
import sys
import warnings
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

def make_filmstrip(images, scale=1):
    """横一列に並べたフィルムストリップ画像を生成"""
    w, h = images[0].size
    n = len(images)
    strip = Image.new("RGBA", (w * n * scale, h * scale), (0, 0, 0, 0))

    for idx, im in enumerate(images):
        if scale > 1:
            im = im.resize((w * scale, h * scale), Image.Resampling.NEAREST)
        strip.paste(im, (idx * w * scale, 0), im)
    return strip

def render_preview(frame_paths, out_gif_path, fps=10, scale=3, out_strip_path=None):
    images = [Image.open(p).convert("RGBA") for p in frame_paths]
    if not images:
        print("Error: No images to render", file=sys.stderr)
        sys.exit(1)

    # 拡大（Nearest Neighbor）
    w, h = images[0].size
    scaled_images = []
    for im in images:
        if scale > 1:
            scaled = im.resize((w * scale, h * scale), Image.Resampling.NEAREST)
        else:
            scaled = im
        scaled_images.append(scaled)

    # GIF出力
    # Pillowで透過PNGからGIFを生成する際、透過パレットを保持
    duration_ms = int(1000 / fps)

    gif_frames = []
    for im in scaled_images:
        # アルファチャンネルが0の箇所を透明としてパレット化
        alpha = im.split()[3]
        p_im = im.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
        # 透過マスクの適用
        mask = Image.eval(alpha, lambda a: 255 if a < 128 else 0)
        p_im.paste(255, mask)
        p_im.info["transparency"] = 255
        gif_frames.append(p_im)

    os.makedirs(os.path.dirname(os.path.abspath(out_gif_path)), exist_ok=True)
    gif_frames[0].save(
        out_gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=duration_ms,
        loop=0,
        transparency=255,
        disposal=2
    )
    print(f"Animation GIF saved: {out_gif_path} ({len(images)} frames, {fps} FPS, {scale}x scale)")

    if out_strip_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_strip_path)), exist_ok=True)
        strip = make_filmstrip(images, scale=scale)
        strip.save(out_strip_path, "PNG")
        print(f"Filmstrip image saved: {out_strip_path}")

def main():
    parser = argparse.ArgumentParser(description="Render animated preview GIF from sprite frames")
    parser.add_argument("--frames", "-f", nargs="+", required=True, help="Input sprite PNG paths or glob pattern")
    parser.add_argument("--output-gif", "-o", required=True, help="Output GIF path")
    parser.add_argument("--output-strip", "-s", help="Output filmstrip PNG path")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second (default: 10)")
    parser.add_argument("--scale", type=int, default=3, help="Nearest-neighbor integer scale multiplier (default: 3)")

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
        print("Error: No frames found", file=sys.stderr)
        sys.exit(1)

    render_preview(
        files,
        args.output_gif,
        fps=args.fps,
        scale=args.scale,
        out_strip_path=args.output_strip
    )

if __name__ == "__main__":
    main()

