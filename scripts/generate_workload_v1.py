#!/usr/bin/env python3
"""Generate the deterministic, synthetic enterprise workload corpus."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "benchmarks/enterprise-workload-v1"
ASSETS = TARGET / "assets"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
FONT_NAME = "ArialUnicode"


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def card(name: str, title: str, lines: list[str], *, jpeg: bool = False, low_quality: bool = False) -> str:
    image = Image.new("RGB", (1400, 960), "#f7f8fa")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((55, 50, 1345, 910), radius=24, fill="white", outline="#b8c2cc", width=3)
    draw.text((100, 92), title, font=font(48), fill="#172b4d")
    y = 190
    for line in lines:
        draw.text((110, y), line, font=font(34), fill="#253858")
        y += 72
    if low_quality:
        image = image.resize((700, 480), Image.Resampling.LANCZOS).resize((1400, 960), Image.Resampling.BILINEAR)
    suffix = ".jpg" if jpeg else ".png"
    path = ASSETS / f"{name}{suffix}"
    image.save(path, quality=62 if low_quality else 90)
    return f"assets/{path.name}"


def supplier_pdf() -> str:
    path = ASSETS / "supplier-proposal.pdf"
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    c = canvas.Canvas(str(path), pagesize=A4, invariant=1)
    pages = [
        ("供应商方案 / Supplier Proposal", ["供应商：北辰精工 / Northstar Manufacturing", "方案编号：NS-2608-A", "报价有效期：2026-09-30"]),
        ("商务报价 / Commercial Offer", ["设备型号：MX-420", "数量：12 台", "含税总价：人民币 318,000 元", "Delivery term: DDP Shanghai"]),
        ("交付与服务 / Delivery & Service", ["计划交付日期：2026-09-15", "质保期：24 个月", "Service response SLA: 4 hours"]),
        ("风险与审批 / Risks & Approval", ["付款条款：30% 预付款，70% 验收后", "异常升级责任人：质量经理", "审批状态：待法务复核"]),
    ]
    for title, lines in pages:
        c.setFont(FONT_NAME, 20)
        c.drawString(55, 790, title)
        c.setFont(FONT_NAME, 13)
        y = 730
        for line in lines:
            c.drawString(65, y, line)
            y -= 45
        c.setFont(FONT_NAME, 9)
        c.drawRightString(540, 35, f"Synthetic benchmark · page {pages.index((title, lines)) + 1}")
        c.showPage()
    c.save()
    return "assets/supplier-proposal.pdf"


def deck_pdf() -> str:
    path = ASSETS / "campaign-deck.pdf"
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    c = canvas.Canvas(str(path), pagesize=landscape(A4), invariant=1)
    slides = [
        ("Q4 Growth Campaign", ["Primary CTA: Start Free Trial", "Target: APAC operations teams"]),
        ("Value Proposition", ["Reduce review time by 35%", "统一材料解析，保留原文证据"]),
        ("Pricing", ["Launch price: ¥2,999 / month", "Includes 20 seats"]),
        ("Offer Summary", ["Launch price: ¥3,299 / month", "Limited offer ends 2026-10-31"]),
        ("Final CTA", ["Start Free Trial", "CTA contrast ratio: 2.1:1"]),
    ]
    for index, (title, lines) in enumerate(slides, 1):
        c.setFillColorRGB(0.05, 0.09, 0.18)
        c.rect(0, 0, 842, 595, fill=1, stroke=0)
        c.setFillColorRGB(1, 1, 1)
        c.setFont(FONT_NAME, 27)
        c.drawString(58, 500, title)
        c.setFont(FONT_NAME, 16)
        y = 410
        for line in lines:
            c.drawString(70, y, line)
            y -= 60
        c.setFillColorRGB(0.25, 0.28, 0.32) if index == 5 else c.setFillColorRGB(0.1, 0.65, 0.85)
        c.roundRect(600, 70, 170, 48, 8, fill=1, stroke=0)
        c.setFillColorRGB(0.32, 0.35, 0.39) if index == 5 else c.setFillColorRGB(1, 1, 1)
        c.setFont(FONT_NAME, 13)
        c.drawCentredString(685, 88, "Start Free Trial")
        c.showPage()
    c.save()
    return "assets/campaign-deck.pdf"


def fact(fid: str, path: str, expected, source: str, evidence: str, weight: int = 1) -> dict:
    return {"id": fid, "path": path, "expected": expected, "source_refs": [source], "evidence_text": evidence, "weight": weight}


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    supplier = supplier_pdf()
    deck = deck_pdf()
    procurement_1 = card("procurement-page-1", "采购申请 / Purchase Request", ["设备型号：MX-420", "数量：12 台", "申请部门：智能制造部"], jpeg=True)
    procurement_2 = card("procurement-page-2", "交付条款 / Delivery Terms", ["交付日期：2026-09-15", "Delivery term: DDP Shanghai", "审批状态：待法务复核"], jpeg=True)
    invoice = card("invoice-low-quality", "增值税发票", ["发票号码：INV-260822-07", "价税合计：¥84,520.00", "购买方：海桥科技"], jpeg=True, low_quality=True)
    chat_1 = card("support-chat-1", "客户群聊截图 1/2", ["客户：控制台一直提示 502", "Simi：已记录，工单 CS-8841", "Customer: production is blocked"])
    chat_2 = card("support-chat-2", "客户群聊截图 2/2", ["工程师：根因是上游超时", "承诺恢复时间：18:30", "Owner: 值班工程师"])
    chart_1 = card("regional-chart", "区域销售 / Regional Sales", ["华东 92 万元", "华南 76 万元", "华北 68 万元", "西部 54 万元"])
    chart_2 = card("regional-note", "图表附注", ["最高：华东 92 万元", "四区合计：290 万元", "Data as of 2026-08-20"])
    flow = card("analysis-flow", "材料解析流程", ["输入 → 文件入库 → 多模态解析", "关键字段缺失？ → 业务顾问补录", "正常路径 → 生成客户调研摘要"])
    ui_before = card("ui-before", "Checkout UI · Before", ["Plan: Team", "Price: ¥2,999 / month", "Button: Confirm Purchase"])
    ui_after = card("ui-after", "Checkout UI · After", ["Plan: Team", "Price: ¥3,299 / month", "Button clipped: Confirm Purc..."])
    product_1 = card("product-front", "设备铭牌照片 · Front", ["Model: XR-17", "Serial: SN-884210", "Ingress protection: IP54"], jpeg=True)
    product_2 = card("product-damage", "设备外观照片 · Side", ["Inspection note: dent on left panel", "Damage severity: medium", "Photo ref: IMG-02"], jpeg=True)
    general = card("warehouse-scene", "仓库现场 / Warehouse", ["Zone: B-3", "Pallet count: 18", "Safety exit: unobstructed"], jpeg=True)
    ambiguity = card("conflicting-dates", "项目排期核对", ["首页上线日期：2026-10-08", "批注上线日期：2026-10-18", "结论：日期冲突，需人工确认"])

    cases = [
        {"id": "supplier-commercial", "name": "多页供应商方案商务抽取", "weight": 1, "lane": "document-extraction", "tags": ["pdf", "bilingual", "completeness", "evidence-required"], "assets": [{"path": supplier, "media_type": "application/pdf"}], "instructions": "提取供应商、型号、数量、含税总价和交付条款。", "facts": [fact("supplier", "supplier.name", "北辰精工", "page-1", "供应商：北辰精工"), fact("model", "supplier.model", "MX-420", "page-2", "设备型号：MX-420", 2), fact("total", "supplier.total_cny", 318000, "page-2", "含税总价：人民币 318,000 元", 2)]},
        {"id": "procurement-cross-image", "name": "跨截图采购与交付信息", "weight": 1, "lane": "document-extraction", "tags": ["multi-asset", "jpeg", "bilingual", "completeness", "evidence-required"], "assets": [{"path": procurement_1, "media_type": "image/jpeg"}, {"path": procurement_2, "media_type": "image/jpeg"}], "instructions": "跨两张截图提取型号、数量、交付日和审批状态。", "facts": [fact("quantity", "procurement.quantity", 12, "asset-1", "数量：12 台"), fact("delivery", "procurement.delivery_date", "2026-09-15", "asset-2", "交付日期：2026-09-15", 2)]},
        {"id": "invoice-low-quality", "name": "低清压缩发票", "weight": 1, "lane": "document-extraction", "tags": ["jpeg", "low-quality", "evidence-required"], "assets": [{"path": invoice, "media_type": "image/jpeg"}], "instructions": "提取发票号码和价税合计。", "facts": [fact("invoice-no", "invoice.number", "INV-260822-07", "asset-1", "发票号码：INV-260822-07"), fact("invoice-total", "invoice.total_cny", 84520, "asset-1", "价税合计：¥84,520.00", 2)]},
        {"id": "support-chat", "name": "跨图客户故障上下文", "weight": 1, "lane": "document-extraction", "tags": ["multi-asset", "bilingual", "completeness", "evidence-required"], "assets": [{"path": chat_1, "media_type": "image/png"}, {"path": chat_2, "media_type": "image/png"}], "instructions": "合并两张群聊截图，提取工单、根因、恢复承诺和责任人。", "facts": [fact("ticket", "incident.ticket", "CS-8841", "asset-1", "工单 CS-8841"), fact("root-cause", "incident.root_cause", "上游超时", "asset-2", "根因是上游超时", 2)]},
        {"id": "supplier-risk", "name": "多页供应商风险与服务条款", "weight": 1, "lane": "document-extraction", "tags": ["pdf", "bilingual", "completeness", "evidence-required"], "assets": [{"path": supplier, "media_type": "application/pdf"}], "instructions": "提取质保期、服务 SLA、异常责任人和审批状态。", "facts": [fact("warranty", "risk.warranty_months", 24, "page-3", "质保期：24 个月"), fact("sla", "risk.sla_hours", 4, "page-3", "Service response SLA: 4 hours"), fact("approval", "risk.approval_status", "待法务复核", "page-4", "审批状态：待法务复核", 2)]},
        {"id": "regional-sales", "name": "图表与附注交叉核验", "weight": 1, "lane": "chart-flow", "tags": ["multi-asset", "completeness", "evidence-required"], "assets": [{"path": chart_1, "media_type": "image/png"}, {"path": chart_2, "media_type": "image/png"}], "instructions": "结合图表和附注提取最高区域及四区合计。", "facts": [fact("top-region", "sales.top_region", "华东", "asset-2", "最高：华东 92 万元", 2), fact("total-sales", "sales.total", 290, "asset-2", "四区合计：290 万元", 2)]},
        {"id": "analysis-flow", "name": "流程图分支理解", "weight": 1, "lane": "chart-flow", "tags": ["visual-reasoning", "evidence-required"], "assets": [{"path": flow, "media_type": "image/png"}], "instructions": "提取异常触发条件、异常责任人和正常输出。", "facts": [fact("trigger", "flow.trigger", "关键字段缺失", "asset-1", "关键字段缺失？", 2), fact("normal-output", "flow.normal_output", "生成客户调研摘要", "asset-1", "生成客户调研摘要")]},
        {"id": "campaign-deck", "name": "营销 PDF 跨页一致性与视觉审查", "weight": 1, "lane": "ppt-review", "tags": ["pdf", "bilingual", "visual-review", "human-review", "evidence-required"], "assets": [{"path": deck, "media_type": "application/pdf"}], "instructions": "提取第 3、4 页价格并检查一致性，同时检查最终 CTA 可读性。", "facts": [fact("price-page-3", "deck.price_page_3", 2999, "page-3", "Launch price: ¥2,999 / month", 2), fact("price-page-4", "deck.price_page_4", 3299, "page-4", "Launch price: ¥3,299 / month", 2), fact("cta-contrast", "deck.cta_contrast_ratio", 2.1, "page-5", "CTA contrast ratio: 2.1:1", 2)]},
        {"id": "ui-regression", "name": "UI 前后版本回归验收", "weight": 1, "lane": "ui-review", "tags": ["multi-asset", "visual-review", "human-review", "evidence-required"], "assets": [{"path": ui_before, "media_type": "image/png"}, {"path": ui_after, "media_type": "image/png"}], "instructions": "比较前后版本，分别提取价格并识别按钮裁切。", "facts": [fact("price-before", "ui.price_before", 2999, "asset-1", "Price: ¥2,999 / month", 2), fact("price-after", "ui.price_after", 3299, "asset-2", "Price: ¥3,299 / month", 2), fact("button-clipped", "ui.button_clipped", True, "asset-2", "Button clipped: Confirm Purc...", 2)]},
        {"id": "warehouse-scene", "name": "一般现场图像理解", "weight": 1, "lane": "general-image", "tags": ["jpeg", "evidence-required"], "assets": [{"path": general, "media_type": "image/jpeg"}], "instructions": "提取区域、托盘数和安全出口状态。", "facts": [fact("zone", "warehouse.zone", "B-3", "asset-1", "Zone: B-3"), fact("pallets", "warehouse.pallet_count", 18, "asset-1", "Pallet count: 18")]},
        {"id": "product-inspection", "name": "产品铭牌与外观缺陷联合判断", "weight": 1, "lane": "physical-product", "tags": ["multi-asset", "jpeg", "visual-review", "human-review", "evidence-required"], "assets": [{"path": product_1, "media_type": "image/jpeg"}, {"path": product_2, "media_type": "image/jpeg"}], "instructions": "结合铭牌和外观图提取型号、序列号、损伤位置及严重度。", "facts": [fact("serial", "product.serial", "SN-884210", "asset-1", "Serial: SN-884210"), fact("damage", "product.damage", "left-panel-dent", "asset-2", "dent on left panel", 2)]},
        {"id": "conflicting-dates", "name": "冲突信息与人工升级", "weight": 1, "lane": "ambiguity", "tags": ["ambiguity", "low-quality", "human-review", "evidence-required"], "assets": [{"path": ambiguity, "media_type": "image/png"}], "instructions": "判断上线日期是否可自动确定；冲突时必须升级人工。", "facts": [fact("decision", "schedule.decision", "requires-human", "asset-1", "日期冲突，需人工确认", 3)]},
    ]
    suite = {
        "schema_version": "0.2", "kind": "benchmark-suite", "id": "enterprise-workload-v1", "name": "企业材料多模态代表性工作负载 v1", "corpus_policy": "synthetic", "output_schema": "output.schema.json",
        "workload_profile": {"lanes": [
            {"id": "document-extraction", "name": "文档表格文字抽取", "weight": 0.50, "min_cases": 5}, {"id": "chart-flow", "name": "图表流程架构理解", "weight": 0.12, "min_cases": 2}, {"id": "ppt-review", "name": "PPT 营销视觉审查", "weight": 0.10, "min_cases": 1}, {"id": "ui-review", "name": "UI 视觉验收", "weight": 0.10, "min_cases": 1}, {"id": "general-image", "name": "一般图片理解", "weight": 0.05, "min_cases": 1}, {"id": "physical-product", "name": "产品与现场照片", "weight": 0.05, "min_cases": 1}, {"id": "ambiguity", "name": "歧义与人工升级", "weight": 0.08, "min_cases": 1}],
            "coverage_gates": {"min_pdf_case_share": 0.25, "min_multi_asset_case_share": 0.33, "required_tag_shares": {"bilingual": 0.33, "low-quality": 0.16, "visual-review": 0.25, "evidence-required": 1.0}},
            "human_review_lanes": ["ppt-review", "ui-review", "physical-product", "ambiguity"]},
        "cases": cases,
        "candidates": [{"id": "reference-pipeline", "name": "机制参考链路", "version": "synthetic-reference@1", "endpoint": "fixture://captures/reference-pipeline.json"}, {"id": "degraded-pipeline", "name": "对抗性退化链路", "version": "synthetic-degraded@1", "endpoint": "fixture://captures/degraded-pipeline.json"}],
        "rubric": {"dimensions": [{"id": "factual_accuracy", "name": "事实准确性", "weight": 0.45}, {"id": "completeness", "name": "信息完整性", "weight": 0.25}, {"id": "evidence_grounding", "name": "证据可追溯性", "weight": 0.20}, {"id": "schema_compliance", "name": "结构合规性", "weight": 0.10}]},
    }
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["fields", "evidence", "uncertainties"], "properties": {"fields": {"type": "object"}, "evidence": {"type": "array", "items": {"type": "object", "required": ["fact_id", "source_ref", "quote"], "properties": {"fact_id": {"type": "string"}, "source_ref": {"type": "string"}, "quote": {"type": "string", "minLength": 1}}, "additionalProperties": False}}, "uncertainties": {"type": "array", "items": {"type": "object", "required": ["fact_id", "reason"], "properties": {"fact_id": {"type": "string"}, "reason": {"type": "string", "minLength": 1}}, "additionalProperties": False}}}, "additionalProperties": False}
    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / "captures").mkdir(exist_ok=True)
    (TARGET / "suite.yaml").write_text(yaml.safe_dump(suite, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (TARGET / "output.schema.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    responses = {}
    degraded = {}
    degraded_ids = {"supplier-commercial", "regional-sales", "campaign-deck", "ui-regression", "product-inspection", "conflicting-dates"}
    for case in cases:
        fields = {}
        evidence = []
        for item in case["facts"]:
            node = fields
            parts = item["path"].split(".")
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = item["expected"]
            evidence.append({"fact_id": item["id"], "source_ref": item["source_refs"][0], "quote": item["evidence_text"]})
        response = {"model_version": "synthetic-reference@1", "output": {"fields": fields, "evidence": evidence, "uncertainties": []}, "usage": {"input_tokens": 1000, "output_tokens": 200, "cost_usd": 0.01}, "latency_ms": 1000}
        responses[case["id"]] = response
        weaker = json.loads(json.dumps(response, ensure_ascii=False))
        weaker["model_version"] = "synthetic-degraded@1"
        if case["id"] in degraded_ids:
            first = case["facts"][0]
            node = weaker["output"]["fields"]
            parts = first["path"].split(".")
            for part in parts[:-1]:
                node = node[part]
            node.pop(parts[-1])
            weaker["output"]["evidence"] = [item for item in weaker["output"]["evidence"] if item["fact_id"] != first["id"]]
        degraded[case["id"]] = weaker
    (TARGET / "captures/reference-pipeline.json").write_text(json.dumps({"cases": responses}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (TARGET / "captures/degraded-pipeline.json").write_text(json.dumps({"cases": degraded}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
