from __future__ import annotations

import html
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "marketing"
PPTX_PATH = OUT_DIR / "AI-Commerce-OS-B2B-Deck.pptx"
HERO_IMAGE = OUT_DIR / "ai-commerce-os-b2b-hero.png"

SLIDE_W = 13_333_333
SLIDE_H = 7_500_000


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def tx_shape(shape_id: int, x: int, y: int, w: int, h: int, text: str, size: int, color: str, bold: bool = False) -> str:
    # 中文字体在 PowerPoint 内优先使用微软雅黑，避免商家打开后出现乱码。
    lines = text.split("\n")
    paragraphs = []
    for line in lines:
        paragraphs.append(
            f"""
            <a:p>
              <a:r>
                <a:rPr lang="zh-CN" sz="{size}" b="{1 if bold else 0}">
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                  <a:latin typeface="Microsoft YaHei"/>
                  <a:ea typeface="Microsoft YaHei"/>
                </a:rPr>
                <a:t>{esc(line)}</a:t>
              </a:r>
              <a:endParaRPr lang="zh-CN" sz="{size}"/>
            </a:p>
            """
        )
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Text {shape_id}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:noFill/>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" anchor="t"/>
        <a:lstStyle/>
        {''.join(paragraphs)}
      </p:txBody>
    </p:sp>
    """


def box(shape_id: int, x: int, y: int, w: int, h: int, fill: str, radius: str = "roundRect") -> str:
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="Box {shape_id}"/>
        <p:cNvSpPr/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="{radius}"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
        <a:ln><a:solidFill><a:srgbClr val="E5E7EB"/></a:solidFill></a:ln>
      </p:spPr>
    </p:sp>
    """


def image_pic(shape_id: int, x: int, y: int, w: int, h: int, rel_id: str = "rId1") -> str:
    return f"""
    <p:pic>
      <p:nvPicPr>
        <p:cNvPr id="{shape_id}" name="Hero image"/>
        <p:cNvPicPr/>
        <p:nvPr/>
      </p:nvPicPr>
      <p:blipFill>
        <a:blip r:embed="{rel_id}"/>
        <a:stretch><a:fillRect/></a:stretch>
      </p:blipFill>
      <p:spPr>
        <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      </p:spPr>
    </p:pic>
    """


def slide_xml(shapes: str, bg: str = "F8FAFC") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>
      </p:grpSpPr>
      {shapes}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def slide_rels(has_image: bool) -> str:
    rel = ""
    if has_image:
        rel = '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/ai-commerce-os-b2b-hero.png"/>'
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rel}</Relationships>"""


def content_types(slide_count: int) -> str:
    slides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {slides}
</Types>"""


def presentation_xml(slide_count: int) -> str:
    ids = "\n".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldIdLst>{ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(slide_count: int) -> str:
    rels = "\n".join(
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>"""


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def core_props() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:dcmitype="http://purl.org/dc/dcmitype/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>AI Commerce OS B2B Deck</dc:title>
  <dc:creator>AI Commerce OS</dc:creator>
  <cp:lastModifiedBy>AI Commerce OS</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-07-12T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-07-12T00:00:00Z</dcterms:modified>
</cp:coreProperties>"""


def app_props(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
  xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>AI Commerce OS</Application>
  <PresentationFormat>宽屏</PresentationFormat>
  <Slides>{slide_count}</Slides>
</Properties>"""


def make_deck() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    slides: list[tuple[str, bool]] = []

    slides.append(
        (
            slide_xml(
                image_pic(2, 0, 0, SLIDE_W, SLIDE_H)
                + box(3, 0, 0, 5_050_000, SLIDE_H, "FFFFFF", "rect")
                + tx_shape(4, 620_000, 660_000, 4_000_000, 550_000, "AI Commerce OS", 2800, "2563EB", True)
                + tx_shape(5, 620_000, 1_450_000, 4_050_000, 1_500_000, "面向电商企业的\nAI 员工操作系统", 4100, "111827", True)
                + tx_shape(6, 620_000, 3_180_000, 4_000_000, 900_000, "从客服、售后、运营三个岗位开始，帮助老板把重复工作交给 AI，把关键决策留给人。", 1650, "475569")
                + tx_shape(7, 620_000, 5_800_000, 4_000_000, 520_000, "商务版介绍材料 · V0.x", 1500, "64748B"),
                "F8FAFC",
            ),
            True,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 700_000, 650_000, 11_600_000, 750_000, "企业真正要买的不是 AI，而是可验证的降本结果", 3300, "111827", True)
                + tx_shape(3, 760_000, 1_720_000, 11_200_000, 700_000, "深圳基础电商团队中，客服、售后、运营的合计用人成本接近 4 万元/月。AI Commerce OS 优先替代重复、标准化、可审批的工作。", 1850, "475569")
                + box(4, 760_000, 2_850_000, 3_550_000, 2_650_000, "FFFFFF")
                + box(5, 4_900_000, 2_850_000, 3_550_000, 2_650_000, "FFFFFF")
                + box(6, 9_040_000, 2_850_000, 3_550_000, 2_650_000, "FFFFFF")
                + tx_shape(7, 1_070_000, 3_250_000, 2_950_000, 1_600_000, "客服\n重复咨询、订单查询、物流追踪、催付转化", 2000, "111827", True)
                + tx_shape(8, 5_210_000, 3_250_000, 2_950_000, 1_600_000, "售后\n退款退货、投诉分级、异常物流、赔偿初筛", 2000, "111827", True)
                + tx_shape(9, 9_350_000, 3_250_000, 2_950_000, 1_600_000, "运营\n客户分层、私域线索、投流建议、活动复盘", 2000, "111827", True)
            ),
            False,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 720_000, 620_000, 11_500_000, 700_000, "不是聊天机器人，而是 AI 员工控制系统", 3300, "111827", True)
                + tx_shape(3, 780_000, 1_520_000, 11_000_000, 650_000, "系统把 AI 能做的工作、必须审批的动作、老板经验和历史数据放到同一个可追踪工作流里。", 1800, "475569")
                + box(4, 760_000, 2_550_000, 2_500_000, 2_800_000, "EFF6FF")
                + box(5, 3_700_000, 2_550_000, 2_500_000, 2_800_000, "F0FDF4")
                + box(6, 6_640_000, 2_550_000, 2_500_000, 2_800_000, "FFF7ED")
                + box(7, 9_580_000, 2_550_000, 2_500_000, 2_800_000, "F8FAFC")
                + tx_shape(8, 1_040_000, 3_020_000, 1_950_000, 1_600_000, "AI Customer\n售前咨询\n订单物流\n人工接管", 1850, "111827", True)
                + tx_shape(9, 3_980_000, 3_020_000, 1_950_000, 1_600_000, "AI AfterSale\n退款退货\n投诉风险\n审批建议", 1850, "111827", True)
                + tx_shape(10, 6_920_000, 3_020_000, 1_950_000, 1_600_000, "AI Operation\n私域获客\n投流草稿\n经营复盘", 1850, "111827", True)
                + tx_shape(11, 9_860_000, 3_020_000, 1_950_000, 1_600_000, "Boss Approval\n预算审批\n风险确认\n最终决策", 1850, "111827", True)
            ),
            False,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 720_000, 620_000, 11_500_000, 700_000, "AI客服：先替代最高频的重复回复", 3300, "111827", True)
                + tx_shape(3, 780_000, 1_520_000, 11_000_000, 650_000, "低风险问题自动生成回复草稿，高风险问题自动暂停，商家修改进入学习记录。", 1800, "475569")
                + box(4, 760_000, 2_480_000, 5_500_000, 3_400_000, "FFFFFF")
                + box(5, 7_040_000, 2_480_000, 5_500_000, 3_400_000, "FFFFFF")
                + tx_shape(6, 1_140_000, 2_980_000, 4_600_000, 2_200_000, "可自动处理\n· 商品 FAQ\n· 订单状态\n· 物流查询\n· 发货时效\n· 基础催付", 1850, "111827", True)
                + tx_shape(7, 7_420_000, 2_980_000, 4_600_000, 2_200_000, "必须人工确认\n· 退款赔偿\n· 投诉差评\n· 金额优惠\n· 情绪激烈\n· 平台规则风险", 1850, "111827", True)
            ),
            False,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 720_000, 620_000, 11_500_000, 700_000, "AI售后：先做风险分级，再做自动化", 3300, "111827", True)
                + tx_shape(3, 780_000, 1_520_000, 11_000_000, 650_000, "售后不是越自动越好。退款、赔偿、投诉必须可控、可审计、可复盘。", 1800, "475569")
                + box(4, 760_000, 2_600_000, 3_550_000, 2_650_000, "FFFFFF")
                + box(5, 4_900_000, 2_600_000, 3_550_000, 2_650_000, "FFFFFF")
                + box(6, 9_040_000, 2_600_000, 3_550_000, 2_650_000, "FFFFFF")
                + tx_shape(7, 1_060_000, 3_030_000, 2_950_000, 1_600_000, "识别\n退款、退货、物流异常、投诉、赔偿", 1900, "111827", True)
                + tx_shape(8, 5_200_000, 3_030_000, 2_950_000, 1_600_000, "判断\n风险等级、责任归因、是否需要审批", 1900, "111827", True)
                + tx_shape(9, 9_340_000, 3_030_000, 2_950_000, 1_600_000, "沉淀\n售后 SOP、老板审批、异常案例", 1900, "111827", True)
            ),
            False,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 720_000, 620_000, 11_500_000, 700_000, "AI运营：先做私域线索和投流计划草稿", 3300, "111827", True)
                + tx_shape(3, 780_000, 1_520_000, 11_000_000, 650_000, "AI运营不直接花钱。它负责发现机会、生成方案、复盘效果，预算和执行由老板审批。", 1800, "475569")
                + box(4, 760_000, 2_420_000, 11_700_000, 3_300_000, "111827", "roundRect")
                + tx_shape(5, 1_200_000, 2_920_000, 10_700_000, 2_050_000, "高意向客户识别  →  私域引导话术  →  优惠券建议  →  投流计划草稿  →  老板审批  →  复盘 ROI", 2300, "FFFFFF", True)
                + tx_shape(6, 1_200_000, 5_080_000, 10_700_000, 500_000, "所有涉及预算、群发、价格和优惠的动作必须审批。", 1650, "CBD5E1")
            ),
            False,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 720_000, 620_000, 11_500_000, 700_000, "验证闭环：用数据证明 AI 是否真的能替代人", 3300, "111827", True)
                + box(3, 880_000, 2_100_000, 2_200_000, 1_500_000, "EFF6FF")
                + box(4, 3_420_000, 2_100_000, 2_200_000, 1_500_000, "F0FDF4")
                + box(5, 5_960_000, 2_100_000, 2_200_000, 1_500_000, "FFF7ED")
                + box(6, 8_500_000, 2_100_000, 2_200_000, 1_500_000, "F5F3FF")
                + box(7, 11_040_000, 2_100_000, 1_600_000, 1_500_000, "F8FAFC")
                + tx_shape(8, 1_100_000, 2_560_000, 1_760_000, 650_000, "Dataset\n标准数据集", 1650, "111827", True)
                + tx_shape(9, 3_640_000, 2_560_000, 1_760_000, 650_000, "Replay\n历史回放", 1650, "111827", True)
                + tx_shape(10, 6_180_000, 2_560_000, 1_760_000, 650_000, "Evaluate\n评分报告", 1650, "111827", True)
                + tx_shape(11, 8_720_000, 2_560_000, 1_760_000, 650_000, "Training\n老板经验", 1650, "111827", True)
                + tx_shape(12, 11_250_000, 2_560_000, 1_160_000, 650_000, "ROI\n降本", 1650, "111827", True)
                + tx_shape(13, 880_000, 4_550_000, 11_500_000, 900_000, "下一阶段不继续堆页面，而是建立 Commerce Dataset、Replay Engine、Evaluation Engine 和 Training Center。", 1900, "475569")
            ),
            False,
        )
    )

    slides.append(
        (
            slide_xml(
                tx_shape(2, 720_000, 640_000, 11_600_000, 700_000, "试用目标：先证明能省时间，再证明能省人", 3300, "111827", True)
                + tx_shape(3, 780_000, 1_610_000, 11_000_000, 650_000, "建议用 1 到 3 家商家真实数据试跑，按周复盘自动化率、错误率、人工接管率和节省工时。", 1800, "475569")
                + box(4, 900_000, 2_760_000, 3_500_000, 2_600_000, "FFFFFF")
                + box(5, 4_900_000, 2_760_000, 3_500_000, 2_600_000, "FFFFFF")
                + box(6, 8_900_000, 2_760_000, 3_500_000, 2_600_000, "FFFFFF")
                + tx_shape(7, 1_250_000, 3_160_000, 2_700_000, 1_650_000, "阶段一\n客服修正样本\n300 到 1000 条", 1900, "111827", True)
                + tx_shape(8, 5_250_000, 3_160_000, 2_700_000, 1_650_000, "阶段二\n售后决策样本\n100 到 300 条", 1900, "111827", True)
                + tx_shape(9, 9_250_000, 3_160_000, 2_700_000, 1_650_000, "阶段三\n运营线索复盘\n私域与投流建议", 1900, "111827", True)
                + tx_shape(10, 780_000, 6_250_000, 11_200_000, 420_000, "AI 负责工作，老板负责审批；以可验证指标逐步替代 4 万/月重复人力成本。", 1700, "2563EB", True)
            ),
            False,
        )
    )

    with zipfile.ZipFile(PPTX_PATH, "w", zipfile.ZIP_DEFLATED) as pptx:
        pptx.writestr("[Content_Types].xml", content_types(len(slides)))
        pptx.writestr("_rels/.rels", root_rels())
        pptx.writestr("docProps/core.xml", core_props())
        pptx.writestr("docProps/app.xml", app_props(len(slides)))
        pptx.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        pptx.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        pptx.write(HERO_IMAGE, "ppt/media/ai-commerce-os-b2b-hero.png")
        for index, (xml, has_image) in enumerate(slides, start=1):
            pptx.writestr(f"ppt/slides/slide{index}.xml", xml)
            pptx.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", slide_rels(has_image))


if __name__ == "__main__":
    make_deck()
    print(PPTX_PATH)
