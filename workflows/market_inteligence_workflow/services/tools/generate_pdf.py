import os
import re
import json
import uuid
from workflows.market_inteligence_workflow.node.upload_to_s3 import upload_to_s3_node
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
    Table,
    TableStyle,
)

# =========================================================
# REPORT DIRECTORY
# =========================================================

REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


# =========================================================
# PAGE NUMBER
# =========================================================


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(500, 20, f"Page {doc.page}")
    canvas.restoreState()


# =========================================================
# TEXT CLEANING & ENCODING
# =========================================================


def clean_text(text: str) -> str:
    """
    Clean text from encoding issues and special characters
    """
    if not text:
        return ""

    # Replace common problematic characters
    replacements = {
        "\u2011": "-",  # Non-breaking hyphen
        "\u2012": "-",  # Figure dash
        "\u2013": "-",  # En dash
        "\u2014": "--",  # Em dash
        "\u2015": "--",  # Horizontal bar
        "\u2010": "-",  # Hyphen
        "\u00ad": "",  # Soft hyphen
        "\u200b": "",  # Zero-width space
        "\u202f": " ",  # Narrow no-break space
        "\u00a0": " ",  # Non-breaking space
        "\u2022": "*",  # Bullet point
        "\u2026": "...",  # Ellipsis
        "\u201c": '"',  # Left double quote
        "\u201d": '"',  # Right double quote
        "\u2018": "'",  # Left single quote
        "\u2019": "'",  # Right single quote
        "■": "-",  # Black square (the issue in your PDF)
        "€": "EUR ",  # Euro symbol
        "$": "USD ",  # Dollar might need space for clarity
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining non-ASCII characters that might cause issues
    # text = text.encode('ascii', 'ignore').decode('ascii')

    return text


# =========================================================
# CLEAN INLINE MARKDOWN
# =========================================================


def clean_inline_markdown(text: str) -> str:
    """
    Convert markdown inline styles into ReportLab-compatible tags
    """
    if not text:
        return ""

    # First clean the text
    text = clean_text(text)

    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # Italic
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

    # Inline code
    text = re.sub(
        r"`(.*?)`",
        r"<font name='Courier'>\1</font>",
        text,
    )

    return text


# =========================================================
# TABLE RENDERER WITH PROPER COLUMN WIDTHS
# =========================================================


def add_markdown_table(table_lines, elements, available_width=7 * inch):
    """
    Render markdown table with proper column widths and text wrapping
    """
    rows = []

    for line in table_lines:
        # Skip markdown separator line
        if re.match(r"^\|\s*[-:]+", line):
            continue

        cols = [clean_text(c.strip()) for c in line.strip("|").split("|")]
        rows.append(cols)

    if not rows:
        return

    # Calculate column widths based on content
    num_cols = len(rows[0])
    if num_cols == 0:
        return

    # Calculate max content length per column
    col_max_lengths = [0] * num_cols
    for row in rows:
        for i, cell in enumerate(row):
            if i < num_cols:
                col_max_lengths[i] = max(col_max_lengths[i], len(cell))

    # Distribute width proportionally
    total_length = sum(col_max_lengths)
    if total_length > 0:
        col_widths = [
            (length / total_length) * available_width for length in col_max_lengths
        ]
    else:
        col_widths = [available_width / num_cols] * num_cols

    # Ensure minimum width
    min_width = 0.75 * inch
    col_widths = [max(w, min_width) for w in col_widths]

    # Wrap text in Paragraphs for proper wrapping
    from reportlab.lib.styles import getSampleStyleSheet

    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        wordWrap="CJK",
    )

    formatted_rows = []
    for i, row in enumerate(rows):
        formatted_row = []
        for cell in row:
            # Wrap cell content in Paragraph for proper text wrapping
            formatted_row.append(Paragraph(clean_inline_markdown(cell), cell_style))
        formatted_rows.append(formatted_row)

    table = Table(formatted_rows, colWidths=col_widths, repeatRows=1)

    table.setStyle(
        TableStyle(
            [
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                # Body
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                # Grid
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                # Padding
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                # Alignment
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 16))


# =========================================================
# JSON RENDERER
# =========================================================


def render_json_block(data, styles, elements):
    """
    Render JSON data as formatted text
    """
    pretty_json = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )

    # Clean the JSON text
    pretty_json = clean_text(pretty_json)

    # Split by lines and create paragraphs
    lines = pretty_json.split("\n")
    for line in lines:
        if line.strip():
            elements.append(
                Paragraph(
                    f"<font name='Courier' size='8'>{line}</font>",
                    styles["CustomCode"],
                )
            )

    elements.append(Spacer(1, 12))


# =========================================================
# MAIN MARKDOWN RENDERER
# =========================================================


def render_markdown_content(content, styles, elements):
    """
    Render markdown content with proper handling of tables, lists, and text
    """
    if not content:
        return

    content = content.strip()

    # Remove leading ":" bug
    if content.startswith(":"):
        content = content[1:].strip()

    # Remove leading/trailing whitespace and newlines
    content = content.strip()

    # Try JSON rendering only if it looks like pure JSON
    if (content.startswith("{") and content.endswith("}")) or (
        content.startswith("[") and content.endswith("]")
    ):
        try:
            parsed_json = json.loads(content)
            if isinstance(parsed_json, (dict, list)):
                render_json_block(parsed_json, styles, elements)
                return
        except Exception:
            pass

    lines = content.split("\n")
    table_buffer = []
    list_buffer = []
    current_list_type = None  # 'bullet' or 'numbered'

    for line in lines:
        line_stripped = line.strip()

        if not line_stripped:
            # Empty line - flush any buffered content
            if table_buffer:
                add_markdown_table(table_buffer, elements)
                table_buffer = []
            if list_buffer:
                for item in list_buffer:
                    elements.append(item)
                list_buffer = []
                current_list_type = None
            continue

        # =================================================
        # TABLE DETECTION
        # =================================================
        if "|" in line_stripped:
            # Flush list buffer if we're entering a table
            if list_buffer:
                for item in list_buffer:
                    elements.append(item)
                list_buffer = []
                current_list_type = None

            table_buffer.append(line_stripped)
            continue
        else:
            if table_buffer:
                add_markdown_table(table_buffer, elements)
                table_buffer = []

        # =================================================
        # HEADINGS
        # =================================================
        if line_stripped.startswith("### "):
            elements.append(
                Paragraph(
                    clean_inline_markdown(line_stripped[4:]),
                    styles["Heading3"],
                )
            )
            elements.append(Spacer(1, 6))

        elif line_stripped.startswith("## "):
            elements.append(
                Paragraph(
                    clean_inline_markdown(line_stripped[3:]),
                    styles["Heading2"],
                )
            )
            elements.append(Spacer(1, 8))

        elif line_stripped.startswith("# "):
            elements.append(
                Paragraph(
                    clean_inline_markdown(line_stripped[2:]),
                    styles["Heading1"],
                )
            )
            elements.append(Spacer(1, 10))

        # =================================================
        # BULLET POINTS
        # =================================================
        elif line_stripped.startswith("- ") or line_stripped.startswith("* "):
            bullet_text = clean_inline_markdown(line_stripped[2:])
            para = Paragraph(
                f"• {bullet_text}",
                styles["BodyText"],
            )
            list_buffer.append(para)
            list_buffer.append(Spacer(1, 4))
            current_list_type = "bullet"

        # =================================================
        # NUMBERED LIST
        # =================================================
        elif re.match(r"^\d+\.", line_stripped):
            para = Paragraph(
                clean_inline_markdown(line_stripped),
                styles["BodyText"],
            )
            list_buffer.append(para)
            list_buffer.append(Spacer(1, 4))
            current_list_type = "numbered"

        # =================================================
        # HORIZONTAL RULE
        # =================================================
        elif line_stripped in ["---", "***", "___"]:
            if list_buffer:
                for item in list_buffer:
                    elements.append(item)
                list_buffer = []
                current_list_type = None
            elements.append(Spacer(1, 10))
            elements.append(HRFlowable(width="100%", color=colors.grey))
            elements.append(Spacer(1, 10))

        # =================================================
        # NORMAL TEXT
        # =================================================
        else:
            # If we have a list buffer and this isn't a list item, flush it
            if (
                list_buffer
                and not line_stripped.startswith(("- ", "* "))
                and not re.match(r"^\d+\.", line_stripped)
            ):
                for item in list_buffer:
                    elements.append(item)
                list_buffer = []
                current_list_type = None

            elements.append(
                Paragraph(
                    clean_inline_markdown(line_stripped),
                    styles["BodyText"],
                )
            )
            elements.append(Spacer(1, 6))

    # Flush remaining buffers
    if table_buffer:
        add_markdown_table(table_buffer, elements)

    if list_buffer:
        for item in list_buffer:
            elements.append(item)


# =========================================================
# SECTION CREATOR
# =========================================================


def create_section(title, content, styles, elements):
    """
    Create a section with title and content
    """
    if not content:
        return

    elements.append(Spacer(1, 16))

    elements.append(
        Paragraph(
            f"<b>{clean_text(title)}</b>",
            styles["Heading2"],
        )
    )

    elements.append(Spacer(1, 10))

    render_markdown_content(
        content,
        styles,
        elements,
    )

    elements.append(Spacer(1, 20))


# =========================================================
# MAIN PDF GENERATOR
# =========================================================


def generate_market_report_pdf(data: dict) -> str:
    """
    Generate a market intelligence report PDF from data dictionary
    """
    report_id = str(uuid.uuid4())

    file_path = os.path.join(
        REPORTS_DIR,
        f"market_report_{report_id}.pdf",
    )

    # =====================================================
    # DOCUMENT
    # =====================================================

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=40,
    )

    # =====================================================
    # STYLES
    # =====================================================

    styles = getSampleStyleSheet()

    # Custom code style
    styles.add(
        ParagraphStyle(
            name="CustomCode",
            fontName="Courier",
            fontSize=8,
            leading=10,
            leftIndent=20,
        )
    )

    # Improve body text style
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 14
    styles["BodyText"].alignment = TA_JUSTIFY

    # Improve heading styles
    styles["Heading1"].fontSize = 18
    styles["Heading1"].textColor = colors.HexColor("#FFFFFF")
    styles["Heading1"].spaceAfter = 12

    styles["Heading2"].fontSize = 14
    styles["Heading2"].textColor = colors.HexColor("#FFFFFF")
    styles["Heading2"].spaceAfter = 10

    styles["Heading3"].fontSize = 12
    styles["Heading3"].textColor = colors.HexColor("#DDDDDF")
    styles["Heading3"].spaceAfter = 8

    elements = []

    # =====================================================
    # COVER PAGE
    # =====================================================

    company = clean_text(data.get("company", "Unknown Company"))
    description = clean_text(data.get("description", ""))

    elements.append(Spacer(1, 100))

    elements.append(
        Paragraph(
            "<font size=26><b>Market Intelligence Report</b></font>",
            styles["Title"],
        )
    )

    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            f"<font size=20>{company}</font>",
            styles["Heading1"],
        )
    )

    elements.append(Spacer(1, 40))

    elements.append(
        HRFlowable(
            width="100%",
            color=colors.grey,
        )
    )

    elements.append(Spacer(1, 40))

    if description:
        elements.append(
            Paragraph(
                clean_inline_markdown(description),
                styles["BodyText"],
            )
        )

    elements.append(PageBreak())

    create_section(
        "Executive Summary",
        data.get("report"),
        styles,
        elements,
    )

    create_section(
        "Market Research",
        data.get("market_research"),
        styles,
        elements,
    )

    create_section(
        "Competitors",
        data.get("competitors"),
        styles,
        elements,
    )

    create_section(
        "Trends",
        data.get("trends"),
        styles,
        elements,
    )

    create_section(
        "Sentiment Analysis",
        data.get("sentiment"),
        styles,
        elements,
    )

    create_section(
        "SWOT Analysis",
        data.get("swot"),
        styles,
        elements,
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    return file_path
