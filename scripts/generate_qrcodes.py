#!/usr/bin/env python3
"""
Clap Cafe QR Code Generator
============================
生成 22 个座位的 QR 码（中英双语）
座位: T01-T12 (室内), O01-O04 (户外), B01-B06 (吧台)

Usage:
    python scripts/generate_qrcodes.py
    python scripts/generate_qrcodes.py --base-url https://staging.order.clapcafe.sg
"""

import argparse
import os
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

# ── 座位定义 / Seat Definitions ─────────────────────────────────

BASE_URL_DEFAULT = "https://order.clapcafe.sg"

# 座位: (zone_prefix, number, label_zh, label_en)
SEATS = [
    ("T", "01", "室内 1号桌", "Indoor Table 01"),
    ("T", "02", "室内 2号桌", "Indoor Table 02"),
    ("T", "03", "室内 3号桌", "Indoor Table 03"),
    ("T", "04", "室内 4号桌", "Indoor Table 04"),
    ("T", "05", "室内 5号桌", "Indoor Table 05"),
    ("T", "06", "室内 6号桌", "Indoor Table 06"),
    ("T", "07", "室内 7号桌", "Indoor Table 07"),
    ("T", "08", "室内 8号桌", "Indoor Table 08"),
    ("T", "09", "室内 9号桌", "Indoor Table 09"),
    ("T", "10", "室内 10号桌", "Indoor Table 10"),
    ("T", "11", "室内 11号桌", "Indoor Table 11"),
    ("T", "12", "室内 12号桌", "Indoor Table 12"),
    ("O", "01", "户外 1号桌", "Outdoor Table 01"),
    ("O", "02", "户外 2号桌", "Outdoor Table 02"),
    ("O", "03", "户外 3号桌", "Outdoor Table 03"),
    ("O", "04", "户外 4号桌", "Outdoor Table 04"),
    ("B", "01", "吧台 1", "Bar Seat 01"),
    ("B", "02", "吧台 2", "Bar Seat 02"),
    ("B", "03", "吧台 3", "Bar Seat 03"),
    ("B", "04", "吧台 4", "Bar Seat 04"),
    ("B", "05", "吧台 5", "Bar Seat 05"),
    ("B", "06", "吧台 6", "Bar Seat 06"),
]

# ── 颜色 ───────────────────────────────────────────────────────

COLOR_FG = "#1a1a2e"  # 深蓝黑（QR码颜色）
COLOR_ACCENT = "#e94560"  # 玫红（座位号）
COLOR_TEXT = "#555555"  # 灰色（副标题）

# ── QR 规格 ────────────────────────────────────────────────────

MODULE_SIZE = 10
MARGIN = 4  # QR 静默区（模块数）
TARGET_PX = 590  # 5cm @ 300DPI


# ── 字体 ──────────────────────────────────────────────────────


def load_font(size: int):
    """尝试加载中文字体，回退到默认字体"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── QR 生成 ────────────────────────────────────────────────────


def make_qr(url: str) -> Image.Image:
    """生成 QR 码，返回 PIL Image"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=MODULE_SIZE,
        border=MARGIN,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(back_color="white").convert("RGB")
    return img.resize((TARGET_PX, TARGET_PX), Image.LANCZOS)


def compose_final(
    qr: Image.Image, seat_id: str, label_zh: str, label_en: str, lang: str
) -> Image.Image:
    """
    将 QR 码 + 座位标签合成为最终图片。
    尺寸: 590 × 690（QR 590 + 标签 100）
    """
    canvas_h = 690
    canvas = Image.new("RGB", (TARGET_PX, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    # 粘贴 QR（左上角）
    canvas.paste(qr, (0, 0))

    # ── 标签区 ──
    seat_text = seat_id  # 如 T01
    scan_text = "扫码点餐" if lang == "zh" else "Scan to Order"
    label = label_zh if lang == "zh" else label_en

    font_seat = load_font(46)
    font_label = load_font(22)
    font_scan = load_font(18)

    label_y = TARGET_PX + 4  # QR 下方留 4px 空隙

    # 座位号（T01 大字，玫红色）
    bbox = draw.textbbox((0, 0), seat_text, font=font_seat)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((TARGET_PX - tw) // 2, label_y), seat_text, fill=COLOR_ACCENT, font=font_seat
    )

    # 座位标签（中文或英文）
    label_y2 = label_y + 54
    bbox2 = draw.textbbox((0, 0), label, font=font_label)
    lw2 = bbox2[2] - bbox2[0]
    draw.text(((TARGET_PX - lw2) // 2, label_y2), label, fill=COLOR_FG, font=font_label)

    # 扫码点餐小字
    label_y3 = label_y2 + 28
    bbox3 = draw.textbbox((0, 0), scan_text, font=font_scan)
    sw = bbox3[2] - bbox3[0]
    draw.text(
        ((TARGET_PX - sw) // 2, label_y3), scan_text, fill=COLOR_TEXT, font=font_scan
    )

    return canvas


def generate_seat(
    zone: str, num: str, label_zh: str, label_en: str, base_url: str, output_dir: Path
):
    """为一个座位生成中英两个 QR 码文件"""
    seat_id = f"{zone}{num}"

    for lang in ["zh", "en"]:
        url = f"{base_url}/?seat={seat_id}&lang={lang}"
        label = label_zh if lang == "zh" else label_en

        qr = make_qr(url)
        final = compose_final(qr, seat_id, label_zh, label_en, lang)

        filename = f"{seat_id}_{lang}.png"
        final.save(output_dir / filename, "PNG", quality=95)
        print(f"    ✅ {filename}")


# ── 汇总页 ────────────────────────────────────────────────────


def make_summary(output_dir: Path):
    """生成 A4 汇总页（3列×2行，中文版 QR）"""
    page_w, page_h = 1240, 1754
    cols, rows = 3, 2
    margin = 30
    cell_w = page_w // cols
    cell_h = page_h // rows
    qr_size = min(cell_w, cell_h) - 20

    page = Image.new("RGB", (page_w, page_h), "white")

    zh_files = sorted(output_dir.glob("*_zh.png"))
    for i, fp in enumerate(zh_files[: cols * rows]):
        row, col = divmod(i, cols)
        x = col * cell_w + (cell_w - qr_size) // 2
        y = row * cell_h + 10

        qr = Image.open(fp).resize((qr_size, qr_size), Image.LANCZOS)
        page.paste(qr, (x, y))

    # 在底部添加标题
    draw = ImageDraw.Draw(page)
    font = load_font(24)
    title = "Clap Cafe - 扫码点餐 QR 码汇总 / QR Code Summary"
    bbox = draw.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((page_w - tw) // 2, page_h - 40), title, fill=COLOR_TEXT, font=font)

    out = output_dir / "QR-Codes-Summary-A4.png"
    page.save(out, "PNG")
    print(f"    ✅ Summary: {out.name}")


# ── 贴纸页 ────────────────────────────────────────────────────


def make_sticker_sheet(output_dir: Path):
    """生成 3×4 贴纸页（适合标签纸打印）"""
    page_w, page_h = 1240, 1754
    cols, rows = 3, 4
    sticker_w = page_w // cols
    sticker_h = page_h // rows
    qr_sz = sticker_w - 24

    page = Image.new("RGB", (page_w, page_h), "white")

    zh_files = sorted(output_dir.glob("*_zh.png"))
    for i, fp in enumerate(zh_files[: cols * rows]):
        row, col = divmod(i, cols)
        x = col * sticker_w + (sticker_w - qr_sz) // 2
        y = row * sticker_h + 8

        qr = Image.open(fp).resize((qr_sz, qr_sz), Image.LANCZOS)
        page.paste(qr, (x, y))

    out = output_dir / "stickers" / "QR-Sticker-Sheet-3x4.png"
    out.parent.mkdir(exist_ok=True)
    page.save(out, "PNG")
    print(f"    ✅ Stickers: {out.relative_to(output_dir.parent)}")


# ── 主程序 ────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Clap Cafe QR Code Generator")
    parser.add_argument(
        "--base-url",
        default=BASE_URL_DEFAULT,
        help=f"Base URL (default: {BASE_URL_DEFAULT})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: public/qr-codes/)",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    output_dir = args.output_dir or (
        Path(__file__).parent.parent / "public" / "qr-codes"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🍴 Clap Cafe QR Code Generator")
    print(f"   Base URL: {base_url}")
    print(f"   Output:   {output_dir}")
    print(f"   Seats:    {len(SEATS)} (T01-T12 / O01-O04 / B01-B06)")
    print()

    for zone, num, label_zh, label_en in SEATS:
        seat_id = f"{zone}{num}"
        print(f"  {seat_id} ...", end="", flush=True)
        generate_seat(zone, num, label_zh, label_en, base_url, output_dir)

    print()
    print("  Summary pages ...")
    try:
        make_summary(output_dir)
        make_sticker_sheet(output_dir)
    except Exception as e:
        print(f"    ⚠️  {e}")

    total = len(list(output_dir.glob("*.png")))
    print(f"\n✅ Done — {total} PNG files in {output_dir}")


if __name__ == "__main__":
    main()
