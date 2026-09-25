# ============================================================
# PACKCHECK AI
# PROFESSIONAL INSPECTION REPORT GENERATOR
# ============================================================

import json
import os
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
    PageBreak,
)


# ============================================================
# THEME
# ============================================================

NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#2563EB")
TEAL = colors.HexColor("#0F766E")

GREEN = colors.HexColor("#15803D")
GREEN_BG = colors.HexColor("#ECFDF3")

ORANGE = colors.HexColor("#B45309")
ORANGE_BG = colors.HexColor("#FFF7ED")

RED = colors.HexColor("#B91C1C")
RED_BG = colors.HexColor("#FEF2F2")

GRAY_900 = colors.HexColor("#111827")
GRAY_700 = colors.HexColor("#374151")
GRAY_600 = colors.HexColor("#4B5563")
GRAY_500 = colors.HexColor("#6B7280")
GRAY_300 = colors.HexColor("#D1D5DB")
GRAY_200 = colors.HexColor("#E5E7EB")
GRAY_100 = colors.HexColor("#F3F4F6")
GRAY_50 = colors.HexColor("#F9FAFB")

WHITE = colors.white


# ============================================================
# FONT SETUP
# ============================================================

def register_unicode_font():
    """
    Find a Windows font that supports the Indian Rupee symbol.
    """

    candidates = [
        (
            "SegoeUI",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
        ),
        (
            "ArialUnicode",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
        ),
        (
            "DejaVu",
            r"C:\Windows\Fonts\DejaVuSans.ttf",
            r"C:\Windows\Fonts\DejaVuSans-Bold.ttf",
        ),
    ]

    for regular_name, regular_path, bold_path in candidates:

        if os.path.exists(regular_path):

            try:

                pdfmetrics.registerFont(
                    TTFont(
                        regular_name,
                        regular_path
                    )
                )

                if os.path.exists(bold_path):

                    pdfmetrics.registerFont(
                        TTFont(
                            regular_name + "-Bold",
                            bold_path
                        )
                    )

                return (
                    regular_name,
                    regular_name + "-Bold"
                )

            except Exception:
                continue

    return (
        "Helvetica",
        "Helvetica-Bold"
    )


FONT, FONT_BOLD = register_unicode_font()


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    """
    Convert arbitrary JSON values into readable text.
    """

    if value is None:
        return "Not detected"

    if isinstance(value, list):

        if not value:
            return "Not detected"

        parts = []

        for item in value:

            if isinstance(item, dict):

                declaration = item.get(
                    "declaration",
                    ""
                )

                item_value = item.get(
                    "value",
                    ""
                )

                if declaration:

                    parts.append(
                        f"{declaration}: {item_value}"
                    )

                else:

                    parts.append(
                        str(item_value)
                    )

            else:

                parts.append(
                    str(item)
                )

        return "; ".join(parts)

    text = str(value).strip()

    if not text:
        return "Not detected"

    return text


def escape_xml(text):
    """
    Escape text before passing it to ReportLab Paragraph.
    """

    text = clean_text(text)

    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    return text


def para(
    value,
    style
):
    """
    Safely create a wrapping Paragraph.
    """

    return Paragraph(
        escape_xml(value),
        style
    )


def status_color(status):

    status = str(
        status or ""
    ).upper().strip()

    if status in {
        "PASS",
        "MATCH",
        "VERIFIED",
    }:

        return GREEN

    if status in {
        "REVIEW",
        "REQUIRES REVIEW",
        "PARTIAL MATCH",
    }:

        return ORANGE

    if status in {
        "MISSING",
        "MISMATCH",
    }:

        return RED

    return GRAY_600


def status_background(status):

    status = str(
        status or ""
    ).upper().strip()

    if status in {
        "PASS",
        "MATCH",
        "VERIFIED",
    }:

        return GREEN_BG

    if status in {
        "REVIEW",
        "REQUIRES REVIEW",
        "PARTIAL MATCH",
    }:

        return ORANGE_BG

    if status in {
        "MISSING",
        "MISMATCH",
    }:

        return RED_BG

    return GRAY_100


def load_json(path):

    path = Path(path)

    if not path.exists():

        return None

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return None


# ============================================================
# STYLES
# ============================================================

def create_styles():

    base = getSampleStyleSheet()

    styles = {}

    styles["title"] = ParagraphStyle(
        "PC_Title",
        parent=base["Title"],
        fontName=FONT_BOLD,
        fontSize=22,
        leading=26,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=3,
    )

    styles["subtitle"] = ParagraphStyle(
        "PC_Subtitle",
        parent=base["Normal"],
        fontName=FONT,
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#D1D5DB"),
        alignment=TA_LEFT,
    )

    styles["section"] = ParagraphStyle(
        "PC_Section",
        parent=base["Heading2"],
        fontName=FONT_BOLD,
        fontSize=13,
        leading=16,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=7,
    )

    styles["section_number"] = ParagraphStyle(
        "PC_SectionNumber",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=8,
        leading=10,
        textColor=BLUE,
    )

    styles["body"] = ParagraphStyle(
        "PC_Body",
        parent=base["BodyText"],
        fontName=FONT,
        fontSize=8.8,
        leading=12,
        textColor=GRAY_700,
        spaceAfter=3,
    )

    styles["body_small"] = ParagraphStyle(
        "PC_BodySmall",
        parent=base["BodyText"],
        fontName=FONT,
        fontSize=7.5,
        leading=10,
        textColor=GRAY_700,
    )

    styles["body_tiny"] = ParagraphStyle(
        "PC_BodyTiny",
        parent=base["BodyText"],
        fontName=FONT,
        fontSize=6.8,
        leading=8.5,
        textColor=GRAY_700,
    )

    styles["label"] = ParagraphStyle(
        "PC_Label",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=7.2,
        leading=9,
        textColor=GRAY_500,
    )

    styles["value"] = ParagraphStyle(
        "PC_Value",
        parent=base["Normal"],
        fontName=FONT,
        fontSize=8.4,
        leading=11,
        textColor=GRAY_900,
    )

    styles["value_bold"] = ParagraphStyle(
        "PC_ValueBold",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=8.8,
        leading=11,
        textColor=GRAY_900,
    )

    styles["table_header"] = ParagraphStyle(
        "PC_TableHeader",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=7.2,
        leading=9,
        textColor=WHITE,
    )

    styles["table_cell"] = ParagraphStyle(
        "PC_TableCell",
        parent=base["Normal"],
        fontName=FONT,
        fontSize=7.4,
        leading=9.5,
        textColor=GRAY_700,
    )

    styles["table_cell_bold"] = ParagraphStyle(
        "PC_TableCellBold",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=7.4,
        leading=9.5,
        textColor=GRAY_900,
    )

    styles["status"] = ParagraphStyle(
        "PC_Status",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER,
    )

    styles["hero_product"] = ParagraphStyle(
        "PC_HeroProduct",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=17,
        leading=21,
        textColor=NAVY,
    )

    styles["hero_manufacturer"] = ParagraphStyle(
        "PC_HeroManufacturer",
        parent=base["Normal"],
        fontName=FONT,
        fontSize=9,
        leading=12,
        textColor=GRAY_600,
    )

    styles["metric_number"] = ParagraphStyle(
        "PC_MetricNumber",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=17,
        leading=19,
        alignment=TA_CENTER,
        textColor=GRAY_900,
    )

    styles["metric_label"] = ParagraphStyle(
        "PC_MetricLabel",
        parent=base["Normal"],
        fontName=FONT_BOLD,
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=GRAY_600,
    )

    styles["note"] = ParagraphStyle(
        "PC_Note",
        parent=base["Normal"],
        fontName=FONT,
        fontSize=7.7,
        leading=10.5,
        textColor=GRAY_600,
    )

    styles["footer"] = ParagraphStyle(
        "PC_Footer",
        parent=base["Normal"],
        fontName=FONT,
        fontSize=6.5,
        leading=8,
        textColor=GRAY_500,
        alignment=TA_CENTER,
    )

    return styles


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================

def draw_page(canvas, doc):

    canvas.saveState()

    width, height = A4

    # Top accent line
    canvas.setFillColor(NAVY)

    canvas.rect(
        0,
        height - 4 * mm,
        width,
        4 * mm,
        fill=1,
        stroke=0,
    )

    # Footer line
    canvas.setStrokeColor(
        GRAY_200
    )

    canvas.line(
        15 * mm,
        12 * mm,
        width - 15 * mm,
        12 * mm,
    )

    canvas.setFont(
        FONT,
        6.5
    )

    canvas.setFillColor(
        GRAY_500
    )

    canvas.drawString(
        15 * mm,
        7.5 * mm,
        "PACKCHECK AI • Preliminary compliance screening"
    )

    canvas.drawRightString(
        width - 15 * mm,
        7.5 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# ============================================================
# HERO HEADER
# ============================================================

def hero_header(
    styles,
    report_time,
    screening_status,
    verification_status,
):

    left = [
        para(
            "PACKCHECK AI",
            styles["title"]
        ),
        para(
            "Compliance Decision Support Report",
            styles["subtitle"]
        ),
    ]

    right = [
        para(
            "INSPECTION REPORT",
            ParagraphStyle(
                "ReportLabel",
                fontName=FONT_BOLD,
                fontSize=7,
                textColor=colors.HexColor("#BFDBFE"),
                alignment=TA_RIGHT,
            )
        ),
        para(
            report_time,
            ParagraphStyle(
                "ReportTime",
                fontName=FONT,
                fontSize=7.5,
                textColor=WHITE,
                alignment=TA_RIGHT,
            )
        ),
    ]

    header = Table(
        [[left, right]],
        colWidths=[
            120 * mm,
            50 * mm
        ],
    )

    header.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                NAVY
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
        ])
    )

    screening = str(
        screening_status or "REVIEW"
    ).upper()

    verification = str(
        verification_status or "NOT AVAILABLE"
    ).upper()

    status_table = Table(
        [[
            para(
                f"SCREENING  •  {screening}",
                ParagraphStyle(
                    "HeroStatus1",
                    fontName=FONT_BOLD,
                    fontSize=7.5,
                    textColor=status_color(screening),
                    alignment=TA_CENTER,
                )
            ),
            para(
                f"OFFICIAL VERIFY  •  {verification}",
                ParagraphStyle(
                    "HeroStatus2",
                    fontName=FONT_BOLD,
                    fontSize=7.5,
                    textColor=status_color(verification),
                    alignment=TA_CENTER,
                )
            )
        ]],
        colWidths=[
            85 * mm,
            85 * mm
        ]
    )

    status_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, 0),
                status_background(screening)
            ),
            (
                "BACKGROUND",
                (1, 0),
                (1, 0),
                status_background(verification)
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                GRAY_200
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.5,
                GRAY_200
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )

    return [
        header,
        Spacer(1, 4),
        status_table,
        Spacer(1, 10),
    ]


# ============================================================
# SECTION HEADER
# ============================================================

def section_header(
    number,
    title,
    styles
):

    table = Table(
        [[
            para(
                number,
                styles["section_number"]
            ),
            para(
                title.upper(),
                styles["section"]
            )
        ]],
        colWidths=[
            13 * mm,
            157 * mm
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "LINEBELOW",
                (0, 0),
                (-1, -1),
                0.8,
                GRAY_200
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "BOTTOM"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
        ])
    )

    return table


# ============================================================
# PRODUCT OVERVIEW
# ============================================================

def product_overview(
    extraction,
    styles
):

    product = clean_text(
        extraction.get("product_name")
    )

    manufacturer = clean_text(
        extraction.get("manufacturer")
    )

    category = clean_text(
        extraction.get("category")
    )

    country = clean_text(
        extraction.get("country_of_origin")
    )

    fssai = clean_text(
        extraction.get("fssai_number")
    )

    left = [
        para(
            "DETECTED PRODUCT",
            styles["label"]
        ),
        Spacer(1, 2),
        para(
            product,
            styles["hero_product"]
        ),
        Spacer(1, 3),
        para(
            manufacturer,
            styles["hero_manufacturer"]
        ),
    ]

    right_rows = [
        [
            para(
                "CATEGORY",
                styles["label"]
            ),
            para(
                "COUNTRY",
                styles["label"]
            )
        ],
        [
            para(
                category,
                styles["value_bold"]
            ),
            para(
                country,
                styles["value_bold"]
            )
        ],
        [
            para(
                "FSSAI NUMBER",
                styles["label"]
            ),
            para(
                "MRP",
                styles["label"]
            )
        ],
        [
            para(
                fssai,
                styles["value_bold"]
            ),
            para(
                clean_text(
                    extraction.get("mrp")
                ),
                styles["value_bold"]
            )
        ],
    ]

    right = Table(
        right_rows,
        colWidths=[
            43 * mm,
            43 * mm
        ]
    )

    right.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LINEBELOW",
                (0, 1),
                (-1, 1),
                0.5,
                GRAY_200
            ),
            (
                "LINEBELOW",
                (0, 3),
                (-1, 3),
                0.5,
                GRAY_200
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
        ])
    )

    overview = Table(
        [[left, right]],
        colWidths=[
            84 * mm,
            86 * mm
        ]
    )

    overview.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                GRAY_50
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                GRAY_200
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
        ])
    )

    return overview


# ============================================================
# SCANNED IMAGE
# ============================================================

def scanned_image(
    image_path,
    styles
):

    if not image_path:
        return None

    path = Path(
        image_path
    )

    if not path.exists():
        return None

    try:

        img = Image(
            str(path)
        )

        max_width = 105 * mm
        max_height = 90 * mm

        scale = min(
            max_width / img.imageWidth,
            max_height / img.imageHeight,
            1
        )

        img.drawWidth = (
            img.imageWidth * scale
        )

        img.drawHeight = (
            img.imageHeight * scale
        )

        image_box = Table(
            [[img]],
            colWidths=[
                170 * mm
            ],
            rowHeights=[
                98 * mm
            ]
        )

        image_box.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GRAY_50
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    GRAY_200
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
            ])
        )

        return image_box

    except Exception:

        return None


# ============================================================
# EXTRACTION TABLE
# ============================================================

def extraction_table(
    extraction,
    styles
):

    fields = [
        (
            "Product Name",
            "product_name"
        ),
        (
            "Category",
            "category"
        ),
        (
            "Manufacturer / Packer / Importer",
            "manufacturer"
        ),
        (
            "Manufacturer Address",
            "manufacturer_address"
        ),
        (
            "FSSAI Number",
            "fssai_number"
        ),
        (
            "MRP",
            "mrp"
        ),
        (
            "Net Quantity",
            "net_quantity"
        ),
        (
            "Batch / Lot",
            "batch_number"
        ),
        (
            "Manufacturing Date",
            "manufacturing_date"
        ),
        (
            "Expiry Date",
            "expiry_date"
        ),
        (
            "Best Before",
            "best_before"
        ),
        (
            "Country of Origin",
            "country_of_origin"
        ),
        (
            "Barcode / GTIN",
            "barcode_or_gtin"
        ),
    ]

    rows = [
        [
            para(
                "FIELD",
                styles["table_header"]
            ),
            para(
                "AI EXTRACTED VALUE",
                styles["table_header"]
            ),
        ]
    ]

    for label, key in fields:

        rows.append([
            para(
                label,
                styles["table_cell_bold"]
            ),
            para(
                extraction.get(key),
                styles["table_cell"]
            )
        ])

    table = Table(
        rows,
        colWidths=[
            55 * mm,
            115 * mm
        ],
        repeatRows=1,
        splitByRow=1,
    )

    style_commands = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            NAVY
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            GRAY_200
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
    ]

    for row in range(
        1,
        len(rows)
    ):

        if row % 2 == 0:

            style_commands.append(
                (
                    "BACKGROUND",
                    (0, row),
                    (-1, row),
                    GRAY_50
                )
            )

    table.setStyle(
        TableStyle(style_commands)
    )

    return table


# ============================================================
# TEXT BLOCK
# ============================================================

def text_block(
    title,
    value,
    styles
):

    return Table(
        [[
            para(
                title.upper(),
                styles["label"]
            )
        ], [
            para(
                value,
                styles["body"]
            )
        ]],
        colWidths=[
            170 * mm
        ],
        style=TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                GRAY_50
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                GRAY_200
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )


# ============================================================
# COMPLIANCE SUMMARY
# ============================================================

def compliance_summary(
    compliance,
    styles
):

    summary = compliance.get(
        "summary",
        {}
    )

    overall = str(
        compliance.get(
            "overall_status",
            "REVIEW"
        )
    ).upper()

    metrics = [
        (
            summary.get(
                "pass",
                0
            ),
            "PASS",
            GREEN
        ),
        (
            summary.get(
                "missing",
                0
            ),
            "MISSING",
            ORANGE
        ),
        (
            summary.get(
                "review",
                0
            ),
            "REVIEW",
            ORANGE
        ),
        (
            summary.get(
                "mismatch",
                0
            ),
            "MISMATCH",
            RED
        ),
    ]

    cells = []

    for number, label, colour in metrics:

        cells.append(
            Table(
                [[
                    para(
                        str(number),
                        ParagraphStyle(
                            "MetricNumber",
                            parent=styles[
                                "metric_number"
                            ],
                            textColor=colour
                        )
                    )
                ], [
                    para(
                        label,
                        styles["metric_label"]
                    )
                ]],
                colWidths=[
                    39 * mm
                ],
                style=TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        WHITE
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        GRAY_200
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                ])
            )
        )

    metric_table = Table(
        [cells],
        colWidths=[
            42.5 * mm,
            42.5 * mm,
            42.5 * mm,
            42.5 * mm,
        ]
    )

    metric_table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                2
            ),
        ])
    )

    decision = Table(
        [[
            para(
                "OVERALL SCREENING",
                styles["label"]
            ),
            para(
                overall,
                ParagraphStyle(
                    "OverallStatus",
                    fontName=FONT_BOLD,
                    fontSize=12,
                    leading=14,
                    textColor=status_color(
                        overall
                    ),
                    alignment=TA_CENTER,
                )
            )
        ]],
        colWidths=[
            85 * mm,
            85 * mm
        ]
    )

    decision.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                status_background(
                    overall
                )
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                status_color(
                    overall
                )
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    return [
        metric_table,
        Spacer(1, 5),
        decision,
    ]


# ============================================================
# COMPLIANCE DETAILS
# ============================================================

def compliance_details(
    compliance,
    styles
):

    checks = compliance.get(
        "checks",
        []
    )

    rows = [[
        para(
            "REQUIREMENT",
            styles["table_header"]
        ),
        para(
            "STATUS",
            styles["table_header"]
        ),
        para(
            "ASSESSMENT",
            styles["table_header"]
        )
    ]]

    for check in checks:

        field = check.get(
            "field",
            "Unknown"
        )

        status = check.get(
            "status",
            "REVIEW"
        )

        message = check.get(
            "message",
            ""
        )

        rows.append([
            para(
                field,
                styles["table_cell_bold"]
            ),
            para(
                status,
                ParagraphStyle(
                    "CheckStatus",
                    parent=styles[
                        "status"
                    ],
                    textColor=status_color(
                        status
                    )
                )
            ),
            para(
                message,
                styles["table_cell"]
            )
        ])

    table = Table(
        rows,
        colWidths=[
            45 * mm,
            28 * mm,
            97 * mm
        ],
        repeatRows=1,
        splitByRow=1,
    )

    commands = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            NAVY
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            GRAY_200
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),
        (
            "ALIGN",
            (1, 1),
            (1, -1),
            "CENTER"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
    ]

    for index, check in enumerate(
        checks,
        start=1
    ):

        status = str(
            check.get(
                "status",
                ""
            )
        ).upper()

        commands.append(
            (
                "BACKGROUND",
                (1, index),
                (1, index),
                status_background(
                    status
                )
            )
        )

    table.setStyle(
        TableStyle(commands)
    )

    return table


# ============================================================
# FOSCOS VERIFICATION
# ============================================================

def normalize_official_data(
    verification
):

    if not verification:
        return None

    # New structure:
    #
    # {
    #   officialData: {...},
    #   verification: {
    #       overallStatus: ...,
    #       results: {...}
    #   }
    # }

    if "verification" in verification:

        official_data = (
            verification.get(
                "officialData",
                {}
            )
        )

        verification_data = (
            verification.get(
                "verification",
                {}
            )
        )

        return {
            "officialData": official_data,
            "verification": verification_data,
        }

    # Older/direct structure support

    return {
        "officialData": verification.get(
            "officialData",
            {}
        ),
        "verification": verification,
    }


def foscos_section(
    verification,
    styles
):

    normalized = normalize_official_data(
        verification
    )

    if not normalized:
        return None

    official_data = normalized.get(
        "officialData",
        {}
    )

    verification_data = normalized.get(
        "verification",
        {}
    )

    results = verification_data.get(
        "results",
        {}
    )

    overall = verification_data.get(
        "overallStatus",
        "UNKNOWN"
    )

    license_row = results.get(
        "licenseNo",
        {}
    )

    company_row = results.get(
        "companyName",
        {}
    )

    address_row = results.get(
        "address",
        {}
    )

    rows = [[
        para(
            "FIELD",
            styles["table_header"]
        ),
        para(
            "PACKAGE / AI",
            styles["table_header"]
        ),
        para(
            "OFFICIAL FOSCOS",
            styles["table_header"]
        ),
        para(
            "RESULT",
            styles["table_header"]
        )
    ]]

    mapping = [
        (
            "FSSAI License",
            license_row
        ),
        (
            "Company Name",
            company_row
        ),
        (
            "Address",
            address_row
        ),
    ]

    for label, item in mapping:

        status = item.get(
            "status",
            "UNKNOWN"
        )

        rows.append([
            para(
                label,
                styles["table_cell_bold"]
            ),
            para(
                item.get(
                    "packet"
                ),
                styles["table_cell"]
            ),
            para(
                item.get(
                    "official"
                ),
                styles["table_cell"]
            ),
            para(
                status,
                ParagraphStyle(
                    "FoSCoSStatus",
                    parent=styles[
                        "status"
                    ],
                    textColor=status_color(
                        status
                    )
                )
            )
        ])

    table = Table(
        rows,
        colWidths=[
            32 * mm,
            49 * mm,
            61 * mm,
            28 * mm
        ],
        repeatRows=1,
        splitByRow=1,
    )

    commands = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            NAVY
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            GRAY_200
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),
        (
            "ALIGN",
            (3, 1),
            (3, -1),
            "CENTER"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            4
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            4
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
    ]

    for index, (_, item) in enumerate(
        mapping,
        start=1
    ):

        status = item.get(
            "status",
            "UNKNOWN"
        )

        commands.append(
            (
                "BACKGROUND",
                (3, index),
                (3, index),
                status_background(
                    status
                )
            )
        )

    table.setStyle(
        TableStyle(commands)
    )

    # Official metadata

    company = clean_text(
        official_data.get(
            "companyName"
        )
    )

    license_type = clean_text(
        official_data.get(
            "licenseType"
        )
    )

    official_status = clean_text(
        official_data.get(
            "status"
        )
    )

    metadata = Table(
        [[
            para(
                "OFFICIAL COMPANY",
                styles["label"]
            ),
            para(
                "LICENSE TYPE",
                styles["label"]
            ),
            para(
                "LICENSE STATUS",
                styles["label"]
            )
        ], [
            para(
                company,
                styles["value_bold"]
            ),
            para(
                license_type,
                styles["value"]
            ),
            para(
                official_status,
                styles["value_bold"]
            )
        ]],
        colWidths=[
            80 * mm,
            45 * mm,
            45 * mm
        ]
    )

    metadata.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                GRAY_50
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                GRAY_200
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    overall_box = Table(
        [[
            para(
                "OVERALL FOSCOS VERIFICATION",
                styles["label"]
            ),
            para(
                overall,
                ParagraphStyle(
                    "FoSCoSOverall",
                    fontName=FONT_BOLD,
                    fontSize=11,
                    leading=13,
                    textColor=status_color(
                        overall
                    ),
                    alignment=TA_CENTER,
                )
            )
        ]],
        colWidths=[
            100 * mm,
            70 * mm
        ]
    )

    overall_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                status_background(
                    overall
                )
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                status_color(
                    overall
                )
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    return [
        metadata,
        Spacer(1, 6),
        table,
        Spacer(1, 6),
        overall_box,
    ]


# ============================================================
# OFFICIAL VERIFICATION HELPERS
# ============================================================

def _verification_payload(verification):
    """
    Normalize the verification_result.json structure.

    Supported current structure:
    {
        "officialData": {...},
        "verification": {
            "overallStatus": "...",
            "results": {...}
        }
    }

    Also supports a direct verification object for compatibility.
    """
    if not verification:
        return {}, {}, {}

    official_data = verification.get("officialData") or {}

    verification_data = verification.get("verification")
    if not isinstance(verification_data, dict):
        verification_data = verification

    results = verification_data.get("results") or {}

    return official_data, verification_data, results


def _result_item(results, *keys):
    for key in keys:
        item = results.get(key)
        if isinstance(item, dict):
            return item
    return {}


def _verification_label(verification):
    """
    Return the official system used for the verification result.
    """
    official_data, verification_data, _ = _verification_payload(verification)

    candidates = [
        verification.get("type") if isinstance(verification, dict) else None,
        verification_data.get("type"),
        official_data.get("source"),
        official_data.get("portal"),
        official_data.get("authority"),
    ]

    for value in candidates:
        if value:
            value = str(value).strip().upper()
            if "BIS" in value:
                return "BIS"
            if "FOSCOS" in value or "FSSAI" in value:
                return "FOSCOS"
            if "COSMETIC" in value or "CDSCO" in value:
                return "CDSCO / COSMETICS"

    return "OFFICIAL PORTAL"


def official_verification_section(verification, extraction, styles):
    """
    Render official verification evidence without treating portal access
    or an extracted licence/IS number as certification.

    The section is deliberately evidence-oriented:
    - official values are shown separately from package/AI values
    - comparison statuses come from the verification workflow
    - if verification is unavailable, the report says so
    """
    if not verification:
        return [
            text_block(
                "Verification Status",
                "No official verification result was available when this report was generated.",
                styles
            )
        ]

    official_data, verification_data, results = _verification_payload(
        verification
    )

    portal = _verification_label(verification)

    overall = str(
        verification_data.get(
            "overallStatus",
            "UNKNOWN"
        )
    ).upper().strip()

    # --------------------------------------------------------
    # Common evidence values
    # --------------------------------------------------------
    package_license = clean_text(
        extraction.get("fssai_number")
        or extraction.get("bis_license_number")
    )

    package_is = clean_text(
        extraction.get("is_number")
    )

    package_company = clean_text(
        extraction.get("manufacturer")
        or extraction.get("company_name")
    )

    package_address = clean_text(
        extraction.get("manufacturer_address")
    )

    # --------------------------------------------------------
    # FoSCoS / FSSAI results
    # --------------------------------------------------------
    license_row = _result_item(
        results,
        "licenseNo",
        "licenseNumber",
        "fssaiNumber"
    )

    company_row = _result_item(
        results,
        "companyName",
        "company"
    )

    address_row = _result_item(
        results,
        "address",
        "companyAddress"
    )

    # --------------------------------------------------------
    # BIS results
    # --------------------------------------------------------
    is_row = _result_item(
        results,
        "isNumber",
        "is_number",
        "standardNumber",
        "standard"
    )

    bis_license_row = _result_item(
        results,
        "licenseNo",
        "bisLicenseNumber",
        "licenceNo",
        "licenceNumber",
        "licenseNumber"
    )

    # Some BIS workflows may put official values directly in
    # officialData rather than in results.
    official_license = (
        official_data.get("licenseNo")
        or official_data.get("licenceNo")
        or official_data.get("licenseNumber")
        or official_data.get("licenceNumber")
        or official_data.get("bisLicenseNumber")
    )

    official_is = (
        official_data.get("isNumber")
        or official_data.get("is_number")
        or official_data.get("standardNumber")
        or official_data.get("standard")
    )

    if not bis_license_row and official_license:
        bis_license_row = {
            "packet": package_license,
            "official": official_license,
            "status": verification_data.get(
                "licenseStatus",
                "UNKNOWN"
            )
        }

    if not is_row and official_is:
        is_row = {
            "packet": package_is,
            "official": official_is,
            "status": verification_data.get(
                "isStatus",
                "UNKNOWN"
            )
        }

    # --------------------------------------------------------
    # Build rows according to portal
    # --------------------------------------------------------
    rows = [[
        para("FIELD", styles["table_header"]),
        para("PACKAGE / AI", styles["table_header"]),
        para("OFFICIAL SOURCE", styles["table_header"]),
        para("RESULT", styles["table_header"])
    ]]

    if portal == "BIS":
        mapping = [
            ("BIS Licence Number", bis_license_row),
            ("Indian Standard (IS) Number", is_row),
        ]

        # Add product/model/company information if the workflow supplied it.
        official_product = (
            official_data.get("productName")
            or official_data.get("product")
            or official_data.get("model")
        )

        if official_product:
            rows.append([
                para("Product / Model", styles["table_cell_bold"]),
                para(
                    extraction.get("product_name"),
                    styles["table_cell"]
                ),
                para(
                    official_product,
                    styles["table_cell"]
                ),
                para(
                    official_data.get(
                        "productStatus",
                        "REVIEW"
                    ),
                    ParagraphStyle(
                        "BISProductStatus",
                        parent=styles["status"],
                        textColor=status_color(
                            official_data.get(
                                "productStatus",
                                "REVIEW"
                            )
                        )
                    )
                )
            ])

    elif portal == "FOSCOS":
        mapping = [
            (
                "FSSAI License",
                license_row
            ),
            (
                "Company Name",
                company_row
            ),
            (
                "Address",
                address_row
            ),
        ]

    else:
        mapping = []

        # Generic official portal support.
        generic_rows = [
            (
                "Registration / Licence",
                license_row or bis_license_row
            ),
            (
                "Standard / Identifier",
                is_row
            ),
            (
                "Company / Manufacturer",
                company_row
            ),
            (
                "Address",
                address_row
            ),
        ]

        mapping = [
            item for item in generic_rows
            if item[1]
        ]

    for label, item in mapping:
        item = item or {}

        status = str(
            item.get("status", "UNKNOWN")
        ).upper()

        packet_value = item.get(
            "packet",
            item.get("package", "")
        )

        official_value = item.get(
            "official",
            item.get("value", "")
        )

        # If the workflow did not return the package value,
        # use the extracted value where appropriate.
        if not packet_value:
            if "FSSAI" in label:
                packet_value = package_license
            elif "BIS Licence" in label:
                packet_value = package_license
            elif "IS Number" in label:
                packet_value = package_is
            elif "Company" in label:
                packet_value = package_company
            elif "Address" in label:
                packet_value = package_address

        rows.append([
            para(label, styles["table_cell_bold"]),
            para(packet_value, styles["table_cell"]),
            para(official_value, styles["table_cell"]),
            para(
                status,
                ParagraphStyle(
                    "OfficialVerificationStatus",
                    parent=styles["status"],
                    textColor=status_color(status)
                )
            )
        ])

    # If there were no structured comparison rows, still show the
    # official status instead of pretending that verification happened.
    if len(rows) == 1:
        rows.append([
            para("Portal Verification", styles["table_cell_bold"]),
            para("Package data submitted", styles["table_cell"]),
            para(
                official_data.get(
                    "status",
                    "Official result captured"
                ),
                styles["table_cell"]
            ),
            para(
                overall,
                ParagraphStyle(
                    "GenericOfficialStatus",
                    parent=styles["status"],
                    textColor=status_color(overall)
                )
            )
        ])

    table = Table(
        rows,
        colWidths=[
            38 * mm,
            45 * mm,
            59 * mm,
            28 * mm
        ],
        repeatRows=1,
        splitByRow=1,
    )

    commands = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            NAVY
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.35,
            GRAY_200
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),
        (
            "ALIGN",
            (3, 1),
            (3, -1),
            "CENTER"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            4
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            4
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            5
        ),
    ]

    for index in range(1, len(rows)):
        status_text = rows[index][3].getPlainText().upper()
        commands.append(
            (
                "BACKGROUND",
                (3, index),
                (3, index),
                status_background(status_text)
            )
        )

    table.setStyle(TableStyle(commands))

    # --------------------------------------------------------
    # Official metadata / source
    # --------------------------------------------------------
    official_company = (
        official_data.get("companyName")
        or official_data.get("manufacturer")
        or official_data.get("company")
    )

    license_type = official_data.get(
        "licenseType"
    )

    source_status = official_data.get(
        "status"
    )

    metadata = Table(
        [[
            para("OFFICIAL SOURCE", styles["label"]),
            para("OFFICIAL ENTITY", styles["label"]),
            para("OFFICIAL STATUS", styles["label"])
        ], [
            para(portal, styles["value_bold"]),
            para(
                official_company or "Not returned",
                styles["value"]
            ),
            para(
                source_status or "Not returned",
                styles["value_bold"]
            )
        ]],
        colWidths=[
            45 * mm,
            80 * mm,
            45 * mm
        ]
    )

    metadata.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                GRAY_50
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.5,
                GRAY_200
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    overall_box = Table(
        [[
            para(
                f"OVERALL {portal} VERIFICATION",
                styles["label"]
            ),
            para(
                overall,
                ParagraphStyle(
                    "OfficialOverall",
                    fontName=FONT_BOLD,
                    fontSize=11,
                    leading=13,
                    textColor=status_color(overall),
                    alignment=TA_CENTER
                )
            )
        ]],
        colWidths=[
            100 * mm,
            70 * mm
        ]
    )

    overall_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                status_background(overall)
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                status_color(overall)
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    evidence_note = (
        f"Source: {portal} official verification workflow. "
        "The official result shown above is evidence returned by the "
        "verification workflow; detection of an identifier or opening "
        "an official portal is not by itself proof of certification. "
        "Final interpretation remains with the authorized inspector "
        "or competent authority."
    )

    return [
        metadata,
        Spacer(1, 6),
        table,
        Spacer(1, 6),
        overall_box,
        Spacer(1, 5),
        para(evidence_note, styles["note"]),
    ]


# ============================================================
# SAFETY / INGREDIENT INFORMATION
# ============================================================

def safety_section(
    extraction,
    styles
):

    ingredients = clean_text(
        extraction.get(
            "ingredients"
        )
    )

    allergens = clean_text(
        extraction.get(
            "allergens"
        )
    )

    warnings = clean_text(
        extraction.get(
            "warnings"
        )
    )

    storage = clean_text(
        extraction.get(
            "storage_conditions"
        )
    )

    cells = []

    for title, value in [
        (
            "Ingredients",
            ingredients
        ),
        (
            "Allergens",
            allergens
        ),
        (
            "Warnings",
            warnings
        ),
        (
            "Storage Conditions",
            storage
        ),
    ]:

        cells.append(
            Table(
                [[
                    para(
                        title.upper(),
                        styles["label"]
                    )
                ], [
                    para(
                        value,
                        styles["body_small"]
                    )
                ]],
                colWidths=[
                    82 * mm
                ],
                style=TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        GRAY_50
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        GRAY_200
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                ])
            )
        )

    table = Table(
        [
            [cells[0], cells[1]],
            [cells[2], cells[3]],
        ],
        colWidths=[
            85 * mm,
            85 * mm
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                1
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                1
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                1
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                1
            ),
        ])
    )

    return table


# ============================================================
# ADDITIONAL DECLARATIONS
# ============================================================

def declarations_section(
    extraction,
    styles
):

    declarations = (
        extraction.get(
            "additional_declarations"
        )
        or []
    )

    if not declarations:

        return None

    rows = [[
        para(
            "DECLARATION",
            styles["table_header"]
        ),
        para(
            "VALUE",
            styles["table_header"]
        )
    ]]

    for item in declarations:

        if isinstance(
            item,
            dict
        ):

            declaration = item.get(
                "declaration",
                "Declaration"
            )

            value = item.get(
                "value",
                ""
            )

        else:

            declaration = "Declaration"
            value = item

        rows.append([
            para(
                declaration,
                styles["table_cell_bold"]
            ),
            para(
                value,
                styles["table_cell"]
            )
        ])

    table = Table(
        rows,
        colWidths=[
            55 * mm,
            115 * mm
        ],
        repeatRows=1,
        splitByRow=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                NAVY
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.35,
                GRAY_200
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    return table


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_report(
    image_path,
    result_path="packcheck_result.json",
    verification_path="verification_result.json",
):

    result_path = Path(
        result_path
    )

    verification_path = Path(
        verification_path
    )

    result = load_json(
        result_path
    )

    if not result:

        raise ValueError(
            f"Unable to read PackCheck result: {result_path}"
        )

    extraction = result.get(
        "extraction",
        {}
    )

    compliance = result.get(
        "compliance",
        {}
    )

    verification = load_json(
        verification_path
    )

    styles = create_styles()

    timestamp = datetime.now()

    filename = (
        "PackCheck_Report_"
        + timestamp.strftime(
            "%Y%m%d_%H%M%S"
        )
        + ".pdf"
    )

    output_path = (
        Path(result_path).parent
        / filename
    )

    # --------------------------------------------------------
    # Determine statuses
    # --------------------------------------------------------

    screening_status = compliance.get(
        "overall_status",
        "REVIEW"
    )

    verification_status = "NOT AVAILABLE"

    if verification:

        verification_data = verification.get(
            "verification",
            verification
        )

        verification_status = (
            verification_data.get(
                "overallStatus",
                "UNKNOWN"
            )
        )

    # --------------------------------------------------------
    # Document
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=17 * mm,
        title="PackCheck AI Inspection Report",
        author="PackCheck AI",
        subject="Automated packaged commodity compliance screening",
    )

    story = []

    # ========================================================
    # COVER / OVERVIEW
    # ========================================================

    story.extend(
        hero_header(
            styles,
            timestamp.strftime(
                "%d %B %Y • %H:%M"
            ),
            screening_status,
            verification_status,
        )
    )

    story.append(
        product_overview(
            extraction,
            styles
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # ========================================================
    # 01 IMAGE
    # ========================================================

    story.append(
        section_header(
            "01",
            "Scanned Product Evidence",
            styles
        )
    )

    story.append(
        Spacer(1, 6)
    )

    image_box = scanned_image(
        image_path,
        styles
    )

    if image_box:

        story.append(
            image_box
        )

        story.append(
            Spacer(1, 4)
        )

        story.append(
            para(
                "Source image supplied for automated label screening.",
                styles["note"]
            )
        )

    else:

        story.append(
            text_block(
                "Image",
                "Scanned product image was not available.",
                styles
            )
        )

    story.append(
        Spacer(1, 10)
    )

    # ========================================================
    # 02 AI EXTRACTION
    # ========================================================

    story.append(
        section_header(
            "02",
            "AI Extracted Product Information",
            styles
        )
    )

    story.append(
        Spacer(1, 5)
    )

    story.append(
        extraction_table(
            extraction,
            styles
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # ========================================================
    # SAFETY
    # ========================================================

    story.append(
        section_header(
            "03",
            "Ingredients & Safety Information",
            styles
        )
    )

    story.append(
        Spacer(1, 5)
    )

    story.append(
        safety_section(
            extraction,
            styles
        )
    )

    # ========================================================
    # ADDITIONAL DECLARATIONS
    # ========================================================

    declarations = declarations_section(
        extraction,
        styles
    )

    if declarations:

        story.append(
            Spacer(1, 10)
        )

        story.append(
            section_header(
                "04",
                "Additional Declarations",
                styles
            )
        )

        story.append(
            Spacer(1, 5)
        )

        story.append(
            declarations
        )

    # ========================================================
    # COMPLIANCE
    # ========================================================

    story.append(
        Spacer(1, 10)
    )

    story.append(
        section_header(
            "05",
            "Automated Compliance Screening",
            styles
        )
    )

    story.append(
        Spacer(1, 6)
    )

    story.extend(
        compliance_summary(
            compliance,
            styles
        )
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        compliance_details(
            compliance,
            styles
        )
    )

    # ========================================================
    # OFFICIAL VERIFICATION
    # ========================================================

    story.append(
        Spacer(1, 12)
    )

    story.append(
        section_header(
            "06",
            "Official Verification",
            styles
        )
    )

    story.append(
        Spacer(1, 6)
    )

    if verification:
        story.extend(
            official_verification_section(
                verification,
                extraction,
                styles
            )
        )
    else:
        story.append(
            text_block(
                "Verification Status",
                "Official verification was not available at the time this report was generated.",
                styles
            )
        )

    # ========================================================
    # EXTRACTION NOTES
    # ========================================================

    notes = (
        extraction.get(
            "extraction_notes"
        )
        or []
    )

    if notes:

        story.append(
            Spacer(1, 12)
        )

        story.append(
            section_header(
                "07",
                "AI Extraction Notes",
                styles
            )

        )

        story.append(
            Spacer(1, 5)
        )

        note_text = "<br/>".join(
            "• " + escape_xml(note)
            for note in notes
        )

        story.append(
            Table(
                [[
                    Paragraph(
                        note_text,
                        styles["body"]
                    )
                ]],
                colWidths=[
                    170 * mm
                ],
                style=TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        ORANGE_BG
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor(
                            "#FED7AA"
                        )
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                ])
            )
        )

    # ========================================================
    # IMPORTANT NOTE
    # ========================================================

    story.append(
        Spacer(1, 12)
    )

    story.append(
        section_header(
            "08",
            "Important Note",
            styles
        )
    )

    story.append(
        Spacer(1, 5)
    )

    disclaimer = (
        "PackCheck AI provides automated preliminary screening "
        "and comparison assistance. AI extraction is not itself "
        "an official record. Results from an applicable official "
        "verification source are shown separately where available. "
        "This report does not constitute legal certification, "
        "laboratory testing, or a final regulatory determination. "
        "Final decisions remain with the authorized inspector "
        "or competent authority."
    )

    story.append(
        Table(
            [[
                para(
                    disclaimer,
                    styles["body"]
                )
            ]],
            colWidths=[
                170 * mm
            ],
            style=TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GRAY_50
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    GRAY_300
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ])
        )
    )

    # ========================================================
    # BUILD
    # ========================================================

    doc.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    return str(output_path)


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    base = Path(
        __file__
    ).resolve().parent.parent

    result_file = (
        base / "packcheck_result.json"
    )

    verification_file = (
        base / "verification_result.json"
    )

    image_file = (
        base / "DM.png"
    )

    output = generate_report(
        image_path=str(image_file),
        result_path=str(result_file),
        verification_path=str(verification_file),
    )

    print(
        f"Report generated: {output}"
    )