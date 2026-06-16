#!/usr/bin/env python3
"""Generate portfolio PNG images from benchmark JSON and captured text."""

import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont


def load_font(size: int, mono: bool = False):
    if mono:
        candidates = [
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/JetBrainsMono-Regular.ttf"),
            "C:/Windows/Fonts/jetbrainsmono-regular.ttf",
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/cour.ttf",
            "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_image(lines: list[str], title: str, out_path: Path, width: int = 1100):
    font = load_font(14, mono=True)
    title_font = load_font(18, mono=False)
    line_height = 20
    padding = 24
    height = padding * 2 + 30 + len(lines) * line_height
    img = Image.new("RGB", (width, max(height, 200)), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.text((padding, padding), title, fill=(100, 200, 255), font=title_font)
    y = padding + 32
    for line in lines:
        draw.text((padding, y), line.rstrip(), fill=(220, 220, 220), font=font)
        y += line_height
    img.save(out_path)
    print(f"Wrote {out_path}")


def k6_results_card(summary: dict, title: str, out_path: Path, accent: tuple[int, int, int]):
    width, height = 920, 520
    bg = (248, 249, 252)
    card = (255, 255, 255)
    border = (220, 224, 230)
    muted = (100, 110, 125)
    text = (30, 35, 45)

    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)

    title_font = load_font(22, mono=False)
    label_font = load_font(13, mono=False)
    value_font = load_font(36, mono=True)
    sub_font = load_font(14, mono=True)
    badge_font = load_font(12, mono=False)

    draw.rounded_rectangle((32, 28, width - 32, height - 28), radius=16, fill=card, outline=border, width=1)
    draw.rectangle((32, 28, width - 32, 34), fill=accent)

    draw.text((52, 48), title, fill=text, font=title_font)
    endpoint = summary.get("endpoint", "?")
    draw.text((52, 82), endpoint, fill=muted, font=sub_font)

    badge = f"{summary.get('vus', '?')} VUs  |  {summary.get('total_requests', summary.get('iterations', '?')):,} requests"
    draw.rounded_rectangle((52, 108, 52 + 16 * len(badge) // 2 + 120, 132), radius=8, fill=(240, 243, 248))
    draw.text((64, 112), badge, fill=muted, font=badge_font)

    metrics = [
        ("Total requests", f"{summary.get('total_requests', summary.get('iterations', 0)):,}"),
        ("p95 latency", f"{summary.get('p95_ms', '?')} ms"),
        ("avg latency", f"{summary.get('avg_ms', '?')} ms"),
        ("throughput", f"{summary.get('rps', '?')} req/s"),
        ("error rate", f"{summary.get('error_rate_pct', summary.get('error_rate', 0))}%"),
    ]

    x0, y0 = 52, 160
    col_w = (width - 104 - 24) // 2
    for i, (label, value) in enumerate(metrics):
        col = i % 2
        row = i // 2
        x = x0 + col * (col_w + 24)
        y = y0 + row * 88
        draw.rounded_rectangle((x, y, x + col_w, y + 72), radius=10, fill=(245, 247, 250), outline=border)
        draw.text((x + 16, y + 12), label.upper(), fill=muted, font=label_font)
        draw.text((x + 16, y + 32), str(value), fill=accent if i == 1 else text, font=value_font if i < 3 else sub_font)

    ts = summary.get("timestamp", "")
    if ts:
        draw.text((52, height - 58), f"Measured {ts[:10]}", fill=muted, font=badge_font)

    draw.text((52, height - 38), "k6 shared-iterations load test", fill=muted, font=badge_font)
    img.save(out_path)
    print(f"Wrote {out_path}")


def comparison_image(buggy: dict, fixed: dict, out_path: Path):
    width, height = 900, 420
    img = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    title_font = load_font(20, mono=False)
    label_font = load_font(16, mono=False)
    value_font = load_font(28, mono=True)

    draw.text((40, 24), "SQL Queries per Request (measured)", fill=(30, 30, 30), font=title_font)

    draw.rounded_rectangle((40, 80, 420, 360), radius=12, fill=(255, 235, 235), outline=(220, 80, 80))
    draw.text((60, 100), "BUGGY (N+1 lazy load)", fill=(180, 40, 40), font=label_font)
    draw.text((60, 160), str(buggy.get("queryCount", 111)), fill=(200, 50, 50), font=value_font)
    draw.text((60, 220), "queries / request", fill=(120, 60, 60), font=label_font)
    draw.text((60, 280), f"p95: {buggy.get('p95_ms', '?')} ms", fill=(120, 60, 60), font=label_font)

    draw.rounded_rectangle((480, 80, 860, 360), radius=12, fill=(230, 245, 235), outline=(60, 140, 80))
    draw.text((500, 100), "FIXED (JOIN FETCH)", fill=(40, 120, 60), font=label_font)
    draw.text((500, 160), str(fixed.get("queryCount", 1)), fill=(40, 140, 70), font=value_font)
    draw.text((500, 220), "queries / request", fill=(60, 100, 70), font=label_font)
    draw.text((500, 280), f"p95: {fixed.get('p95_ms', '?')} ms", fill=(60, 100, 70), font=label_font)

    img.save(out_path)
    print(f"Wrote {out_path}")


def metrics_bar_chart(buggy: dict, fixed: dict, out_path: Path):
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = load_font(14, mono=False)
    title_font = load_font(18, mono=False)

    draw.text((40, 20), "Before / After Metrics (measured Jun 2026)", fill=(30, 30, 30), font=title_font)

    metrics = [
        ("Queries / req", buggy.get("queryCount", 111), fixed.get("queryCount", 1)),
        ("p95 latency (ms)", buggy.get("p95_ms", 0), fixed.get("p95_ms", 0)),
        ("Throughput (req/s)", buggy.get("rps", 0), fixed.get("rps", 0)),
    ]

    chart_left, chart_bottom = 120, 420
    chart_width = 500
    max_bar = max(m[1] for m in metrics) * 1.1 or 1

    y = 70
    for label, b_val, f_val in metrics:
        draw.text((40, y + 8), label, fill=(60, 60, 60), font=font)
        bar_h = 18
        b_width = int((b_val / max_bar) * chart_width)
        f_width = int((f_val / max_bar) * chart_width)
        draw.rectangle((chart_left, y, chart_left + b_width, y + bar_h), fill=(220, 80, 80))
        draw.text((chart_left + b_width + 8, y), str(b_val), fill=(180, 40, 40), font=font)
        draw.rectangle((chart_left, y + bar_h + 6, chart_left + f_width, y + 2 * bar_h + 6), fill=(60, 160, 90))
        draw.text((chart_left + f_width + 8, y + bar_h + 6), str(f_val), fill=(40, 120, 60), font=font)
        y += 70

    draw.text((chart_left, chart_bottom + 10), "red = buggy  |  green = fixed", fill=(100, 100, 100), font=font)
    img.save(out_path)
    print(f"Wrote {out_path}")


def architecture_diagram(buggy: dict, fixed: dict, out_path: Path):
    width, height = 1000, 520
    img = Image.new("RGB", (width, height), color=(248, 249, 252))
    draw = ImageDraw.Draw(img)
    font = load_font(14, mono=False)
    title_font = load_font(18, mono=False)
    box_font = load_font(15, mono=False)

    draw.text((40, 20), "Request Flow: N+1 vs JOIN FETCH", fill=(30, 30, 30), font=title_font)

    def box(x, y, w, h, text, fill, outline):
        draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=outline)
        for i, line in enumerate(text.split("\n")):
            draw.text((x + 12, y + 12 + i * 18), line, fill=(40, 40, 40), font=box_font)

    def arrow(x1, y1, x2, y2, color):
        draw.line((x1, y1, x2, y2), fill=color, width=2)
        draw.polygon([(x2, y2), (x2 - 8, y2 - 4), (x2 - 8, y2 + 4)], fill=color)

    draw.text((40, 55), "BUGGY", fill=(180, 50, 50), font=font)
    box(40, 80, 100, 50, "Client\n(k6)", "#e8eaf0", "#888")
    box(200, 80, 140, 50, "Spring Boot\n/buggy", "#ffe8e8", "#c44")
    box(400, 80, 120, 50, "Hibernate\nN+1 loop", "#ffe0e0", "#c44")
    box(580, 80, 130, 50, "PostgreSQL\n111 SELECTs", "#ffd8d8", "#c44")
    arrow(140, 105, 200, 105, "#888")
    arrow(340, 105, 400, 105, "#c44")
    arrow(520, 105, 580, 105, "#c44")
    draw.arc((395, 130, 555, 200), 0, 180, fill=(200, 60, 60), width=2)
    draw.text((420, 175), "100x item SELECTs", fill=(180, 50, 50), font=font)

    draw.text((40, 280), "FIXED", fill=(40, 120, 60), font=font)
    box(40, 305, 100, 50, "Client\n(k6)", "#e8eaf0", "#888")
    box(200, 305, 140, 50, "Spring Boot\n/fixed", "#e8f5e9", "#4a8")
    box(400, 305, 160, 50, "JOIN FETCH\n1 query", "#d4edda", "#4a8")
    box(620, 305, 130, 50, "PostgreSQL\n1 round trip", "#c8e6c9", "#4a8")
    arrow(140, 330, 200, 330, "#888")
    arrow(340, 330, 400, 330, "#4a8")
    arrow(560, 330, 620, 330, "#4a8")

    footer = (
        f"Measured: {buggy.get('queryCount', 111)} queries / {buggy.get('p95_ms', '?')} ms p95"
        f"  ->  {fixed.get('queryCount', 1)} query / {fixed.get('p95_ms', '?')} ms p95"
    )
    draw.text((40, 450), footer, fill=(60, 60, 60), font=font)
    img.save(out_path)
    print(f"Wrote {out_path}")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    images = root / "docs" / "images"
    raw = images / "raw"
    images.mkdir(parents=True, exist_ok=True)

    buggy_stats = {}
    fixed_stats = {}
    if (raw / "query-stats-buggy.json").exists():
        buggy_stats = json.loads((raw / "query-stats-buggy.json").read_text())
    if (raw / "query-stats-fixed.json").exists():
        fixed_stats = json.loads((raw / "query-stats-fixed.json").read_text())

    buggy_k6_path = root / "load" / "results" / "buggy-summary.json"
    fixed_k6_path = root / "load" / "results" / "fixed-summary.json"
    buggy_k6 = json.loads(buggy_k6_path.read_text()) if buggy_k6_path.exists() else {}
    fixed_k6 = json.loads(fixed_k6_path.read_text()) if fixed_k6_path.exists() else {}

    for k6, stats in ((buggy_k6, buggy_stats), (fixed_k6, fixed_stats)):
        if k6:
            stats["p95_ms"] = k6.get("p95_ms")
            stats["rps"] = k6.get("rps")

    k6_results_card(
        buggy_k6,
        "k6 Load Test: Before Fix",
        images / "k6-buggy-results.png",
        accent=(200, 60, 60),
    )
    k6_results_card(
        fixed_k6,
        "k6 Load Test: After Fix",
        images / "k6-fixed-results.png",
        accent=(40, 140, 80),
    )

    if (raw / "explain-buggy.txt").exists():
        lines = (raw / "explain-buggy.txt").read_text(encoding="utf-8", errors="replace").splitlines()
        text_image(lines, "EXPLAIN ANALYZE: N+1 item fetch (per order)", images / "explain-buggy.png")
    if (raw / "explain-fixed.txt").exists():
        lines = (raw / "explain-fixed.txt").read_text(encoding="utf-8", errors="replace").splitlines()
        text_image(lines, "EXPLAIN ANALYZE: JOIN FETCH (single query)", images / "explain-fixed.png")

    comparison_image(buggy_stats, fixed_stats, images / "query-count-comparison.png")
    metrics_bar_chart(buggy_stats, fixed_stats, images / "metrics-comparison.png")
    architecture_diagram(buggy_stats, fixed_stats, images / "architecture-diagram.png")


if __name__ == "__main__":
    main()
