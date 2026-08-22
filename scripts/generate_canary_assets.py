#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks/2026-08-market-canary/assets"
FONT_CANDIDATES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ) if bold else FONT_CANDIDATES
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    raise RuntimeError("Install PingFang or Noto Sans CJK to regenerate the canary assets")


def canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (1200, 900), "#f6f3ec")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((45, 40, 1155, 860), radius=18, fill="white", outline="#1f2937", width=3)
    draw.text((85, 72), title, fill="#111827", font=font(38, bold=True))
    draw.line((85, 130, 1115, 130), fill="#9ca3af", width=2)
    return image, draw


def save(image: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    image.save(OUT / name, format="PNG", optimize=True)


def order() -> None:
    image, draw = canvas("设备采购订单 / EQUIPMENT PURCHASE ORDER")
    rows = [
        ("产品", "工业视觉检测终端"),
        ("型号", "MX-420"),
        ("数量", "12 台"),
        ("含税总价", "人民币 318,000 元"),
        ("交付日期", "2026 年 9 月 15 日"),
        ("验收方式", "到货安装后现场验收"),
    ]
    y = 180
    for label, value in rows:
        draw.rounded_rectangle((105, y, 1095, y + 78), radius=8, fill="#f9fafb", outline="#d1d5db", width=2)
        draw.text((135, y + 18), f"{label}：", fill="#374151", font=font(27, bold=True))
        draw.text((370, y + 18), value, fill="#111827", font=font(29))
        y += 96
    draw.text((90, 820), "DOC-PO-2026-0817 · page-1", fill="#6b7280", font=font(20))
    save(image, "equipment-order.png")


def inspection() -> None:
    image, draw = canvas("来料检验报告 / INCOMING INSPECTION")
    rows = [
        ("批次号", "B-260817"),
        ("抽样数量", "800 件"),
        ("缺陷数量", "17 件"),
        ("缺陷率", "2.125%"),
        ("合格阈值", "≤ 1.5%"),
        ("判定", "不合格"),
    ]
    y = 180
    for index, (label, value) in enumerate(rows):
        fill = "#fff1f2" if index == 5 else "#f8fafc"
        color = "#be123c" if index == 5 else "#111827"
        draw.rectangle((100, y, 1100, y + 72), fill=fill, outline="#cbd5e1", width=2)
        draw.text((135, y + 16), f"{label}：", fill="#334155", font=font(26, bold=True))
        draw.text((400, y + 16), value, fill=color, font=font(28, bold=index == 5))
        y += 76
    draw.rounded_rectangle((100, 674, 1100, 770), radius=10, fill="#fffbeb", outline="#f59e0b", width=2)
    draw.text((135, 703), "处置：异常批次转质量经理复核（SLA 4 小时）", fill="#92400e", font=font(27, bold=True))
    draw.text((90, 820), "QA-B260817 · page-1", fill="#6b7280", font=font(20))
    save(image, "inspection-report.png")


def chart() -> None:
    image, draw = canvas("2026 Q4 区域销售额（万元）")
    values = [("华东", 92, "#2563eb"), ("华南", 76, "#0d9488"), ("华北", 68, "#7c3aed"), ("西部", 54, "#ea580c")]
    origin_x, origin_y = 155, 730
    draw.line((origin_x, 190, origin_x, origin_y), fill="#374151", width=3)
    draw.line((origin_x, origin_y, 1080, origin_y), fill="#374151", width=3)
    for tick in range(0, 101, 20):
        y = origin_y - tick * 4.7
        draw.line((origin_x - 8, y, 1080, y), fill="#e5e7eb", width=1)
        draw.text((95, y - 13), str(tick), fill="#6b7280", font=font(19))
    for index, (region, value, color) in enumerate(values):
        x = 240 + index * 205
        top = origin_y - value * 4.7
        draw.rounded_rectangle((x, top, x + 105, origin_y), radius=8, fill=color)
        draw.text((x + 25, top - 42), str(value), fill="#111827", font=font(27, bold=True))
        draw.text((x + 20, origin_y + 18), region, fill="#111827", font=font(25, bold=True))
    draw.rounded_rectangle((760, 165, 1085, 222), radius=8, fill="#eff6ff", outline="#93c5fd")
    draw.text((785, 177), "最高：华东 92 万元", fill="#1d4ed8", font=font(23, bold=True))
    draw.text((90, 820), "SALES-Q4-2026 · page-1", fill="#6b7280", font=font(20))
    save(image, "regional-sales-chart.png")


def process() -> None:
    image, draw = canvas("客户材料解析与人工接管流程")
    boxes = [
        ((90, 220, 330, 310), "材料接收", "#dbeafe"),
        ((420, 220, 700, 310), "多模态预解析", "#dcfce7"),
        ((800, 200, 1110, 330), "关键字段缺失？", "#fef3c7"),
        ((760, 480, 1110, 590), "业务顾问补录\nSLA 4 小时", "#fee2e2"),
        ((330, 640, 690, 750), "生成客户调研摘要", "#ede9fe"),
    ]
    for coords, text, fill in boxes:
        draw.rounded_rectangle(coords, radius=16, fill=fill, outline="#475569", width=3)
        bbox = draw.multiline_textbbox((0, 0), text, font=font(27, bold=True), spacing=8, align="center")
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (coords[0] + coords[2] - width) / 2
        y = (coords[1] + coords[3] - height) / 2
        draw.multiline_text((x, y), text, fill="#111827", font=font(27, bold=True), spacing=8, align="center")
    draw.line((330, 265, 420, 265), fill="#334155", width=5)
    draw.polygon([(420, 265), (402, 255), (402, 275)], fill="#334155")
    draw.line((700, 265, 800, 265), fill="#334155", width=5)
    draw.polygon([(800, 265), (782, 255), (782, 275)], fill="#334155")
    draw.line((955, 330, 955, 480), fill="#be123c", width=5)
    draw.polygon([(955, 480), (945, 462), (965, 462)], fill="#be123c")
    draw.text((975, 385), "是", fill="#be123c", font=font(23, bold=True))
    draw.line((800, 275, 570, 640), fill="#15803d", width=5)
    draw.polygon([(570, 640), (573, 620), (590, 632)], fill="#15803d")
    draw.text((660, 455), "否", fill="#15803d", font=font(23, bold=True))
    draw.line((760, 535, 620, 640), fill="#334155", width=4)
    draw.polygon([(620, 640), (627, 621), (640, 635)], fill="#334155")
    draw.text((90, 820), "FLOW-DOC-01 · page-1", fill="#6b7280", font=font(20))
    save(image, "analysis-process.png")


if __name__ == "__main__":
    order()
    inspection()
    chart()
    process()
    print(f"generated 4 assets in {OUT}")
