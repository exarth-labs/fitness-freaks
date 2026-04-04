"""
Fitness Freak - Image Optimization Script
Converts iPhone JPEG images to compressed WebP and saves them to static/website/images/gym/

Usage:
    python docs/bash/optimize_images.py
    python docs/bash/optimize_images.py --quality 75 --max-dim 1400
"""

import argparse
import pathlib
import sys
from PIL import Image

# These images need 90° counter-clockwise rotation
ROTATE_CCW_90 = {
    "IMG_1658", "IMG_1668",
    "IMG_1685", "IMG_1687", "IMG_1689", "IMG_1690",
}

# These images need 90° clockwise rotation (opposite direction)
ROTATE_CW_90 = {
    "IMG_1662", "IMG_1686", "IMG_1688",
}


def fmt_size(bytes_val):
    if bytes_val >= 1_048_576:
        return f"{bytes_val / 1_048_576:.1f} MB"
    return f"{bytes_val / 1024:.0f} KB"


def optimize_images(quality: int = 82, max_dim: int = 1920):
    # Resolve paths relative to project root (script lives in docs/bash/)
    project_root = pathlib.Path(__file__).resolve().parent.parent.parent
    src_dir = project_root / "static" / "website" / "images"
    dst_dir = src_dir / "gym"

    if not src_dir.exists():
        print(f"ERROR: Source folder not found: {src_dir}")
        sys.exit(1)

    dst_dir.mkdir(exist_ok=True)

    extensions = ("*.jpeg", "*.jpg", "*.png", "*.JPEG", "*.JPG", "*.PNG")
    src_files = []
    for ext in extensions:
        src_files.extend(src_dir.glob(ext))
    src_files = sorted(set(src_files))

    if not src_files:
        print(f"No images found in {src_dir}")
        sys.exit(0)

    results = []

    for img_path in src_files:
        try:
            original_size = img_path.stat().st_size
            img = Image.open(img_path)

            # Convert RGBA/P to RGB for WebP compatibility
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")

            # Apply manual rotation for known sideways shots
            if img_path.stem in ROTATE_CCW_90:
                img = img.rotate(90, expand=True)
            elif img_path.stem in ROTATE_CW_90:
                img = img.rotate(-90, expand=True)

            orig_w, orig_h = img.size

            # Resize only if larger than max_dim
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)
            new_w, new_h = img.size

            out_path = dst_dir / (img_path.stem + ".webp")
            img.save(out_path, "WEBP", quality=quality, method=6)
            new_size = out_path.stat().st_size

            saved = original_size - new_size
            pct = (saved / original_size) * 100

            results.append({
                "src": img_path.name,
                "dst": out_path.name,
                "orig_size": original_size,
                "new_size": new_size,
                "saved": saved,
                "pct": pct,
                "orig_dims": f"{orig_w}x{orig_h}",
                "new_dims": f"{new_w}x{new_h}",
            })

            print(f"  ✓ {img_path.name} → {out_path.name}  "
                  f"({fmt_size(original_size)} → {fmt_size(new_size)}, -{pct:.0f}%)")

        except Exception as e:
            print(f"  ✗ {img_path.name}: {e}")

    if not results:
        print("No images processed.")
        return

    total_orig = sum(r["orig_size"] for r in results)
    total_new = sum(r["new_size"] for r in results)
    total_saved = total_orig - total_new
    total_pct = (total_saved / total_orig) * 100

    col_file = max(len(r["dst"]) for r in results) + 2
    col_file = max(col_file, 22)
    line_width = col_file + 52

    print()
    print("=" * line_width)
    print(f"{'FITNESS FREAK — IMAGE OPTIMIZATION REPORT':^{line_width}}")
    print("=" * line_width)
    print(f"  Settings: quality={quality}, max_dimension={max_dim}px")
    print("-" * line_width)
    header = f"  {'Output File':<{col_file}} {'Original':>10}  {'Optimized':>10}  {'Saved':>9}  {'%':>5}  {'Dimensions'}"
    print(header)
    print("-" * line_width)

    for r in results:
        dims = f"{r['orig_dims']} → {r['new_dims']}" if r["orig_dims"] != r["new_dims"] else r["new_dims"]
        print(
            f"  {r['dst']:<{col_file}} "
            f"{fmt_size(r['orig_size']):>10}  "
            f"{fmt_size(r['new_size']):>10}  "
            f"{fmt_size(r['saved']):>9}  "
            f"{r['pct']:>4.0f}%  "
            f"{dims}"
        )

    print("-" * line_width)
    print(
        f"  {'TOTAL (' + str(len(results)) + ' images)':<{col_file}} "
        f"{fmt_size(total_orig):>10}  "
        f"{fmt_size(total_new):>10}  "
        f"{fmt_size(total_saved):>9}  "
        f"{total_pct:>4.0f}%"
    )
    print("=" * line_width)
    print(f"  Output folder: {dst_dir}")
    print("=" * line_width)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize gym images to WebP")
    parser.add_argument("--quality", type=int, default=82,
                        help="WebP quality 1-100 (default: 82)")
    parser.add_argument("--max-dim", type=int, default=1920,
                        help="Max width or height in pixels (default: 1920)")
    args = parser.parse_args()
    optimize_images(quality=args.quality, max_dim=args.max_dim)
