"""
Build the Word templates referenced by article1-writing.md / article1-client.md
and verify them against the Foxit DocGen API.

Outputs:
  - invoice_simple.docx   (scalar tokens only: welcome / first-run friendly)
  - invoice_table.docx    (full invoice with line-items loop, camelCase tokens)
  - invoice_full.docx     (snake_case tokens, matches article1-client.md payload
                           exactly: customer_name / invoice_number / invoice_date /
                           due_date / line_items / subtotal / tax_rate / tax_amount /
                           total_due)
  - *_test.pdf rendered proof for each template
"""
import base64
import os
import sys
from pathlib import Path

import requests
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.shared import Pt, RGBColor, Inches

HERE = Path(__file__).resolve().parent

# Demo credentials are documented in foxit/CLAUDE.md; pulled from env first
# so the script can run in CI without a code change.
HOST = os.environ.get("BASE_URL", "https://na1.fusion.foxit.com")
CLIENT_ID = os.environ.get("CLIENT_ID", "foxit_8Aqfv2MCkou5rr4i")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "_ySDdB1dKLP3FVjkLmttgIG1X1B_oHGZ")


def _styled_heading(doc, text, size=18):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    return p


def build_invoice_simple(path: Path) -> None:
    """Scalar-only invoice header. Good for first end-to-end run."""
    doc = Document()

    _styled_heading(doc, "INVOICE", size=24)
    doc.add_paragraph("Issued by Foxit DocGen API Demo")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("Bill To: ").bold = True
    p.add_run("{{ companyName }}")

    p = doc.add_paragraph()
    p.add_run("Invoice Number: ").bold = True
    p.add_run("{{ invoiceNumber }}")

    p = doc.add_paragraph()
    p.add_run("Invoice Date: ").bold = True
    p.add_run("{{ invoiceDate \\@ MM/dd/yyyy }}")

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Total Due: ").bold = True
    run = p.add_run('{{ totalDue \\# "$#,##0.00" }}')
    run.bold = True

    doc.add_paragraph()
    doc.add_paragraph(
        "Thank you for your business. Payment is due within 30 days of the invoice date."
    )

    doc.save(path)


def build_invoice_table(path: Path) -> None:
    """Full invoice with line-items loop. Mirrors the article's JSON payload exactly."""
    doc = Document()

    _styled_heading(doc, "INVOICE", size=24)
    doc.add_paragraph("Foxit DocGen API Sample Template")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("Bill To: ").bold = True
    p.add_run("{{ companyName }}")

    p = doc.add_paragraph()
    p.add_run("Invoice Number: ").bold = True
    p.add_run("{{ invoiceNumber }}")

    p = doc.add_paragraph()
    p.add_run("Invoice Date: ").bold = True
    p.add_run("{{ invoiceDate \\@ MM/dd/yyyy }}")

    doc.add_paragraph()

    # Line-items table: header row (static) + loop row (TableStart/TableEnd in same row)
    # + footer row using {{=SUM(ABOVE)}} aggregate.
    table = doc.add_table(rows=3, cols=5)
    table.style = "Light Grid Accent 1"
    table.autofit = True

    headers = ["#", "Description", "Qty", "Unit Price", "Line Total"]
    for idx, text in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = ""
        run = cell.paragraphs[0].add_run(text)
        run.bold = True

    loop_row = table.rows[1].cells
    loop_row[0].text = "{{TableStart:lineItems}}{{ROW_NUMBER}}"
    loop_row[1].text = "{{description}}"
    loop_row[2].text = "{{qty}}"
    loop_row[3].text = '{{unitPrice \\# "$#,##0.00"}}'
    loop_row[4].text = '{{lineTotal \\# "$#,##0.00"}}{{TableEnd:lineItems}}'

    footer = table.rows[2].cells
    footer[0].text = ""
    footer[1].text = ""
    footer[2].text = ""
    p = footer[3].paragraphs[0]
    p.add_run("Subtotal:").bold = True
    footer[4].text = '{{=SUM(ABOVE) \\# "$#,##0.00"}}'

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Total Due: ").bold = True
    p.add_run('{{ totalDue \\# "$#,##0.00" }}').bold = True

    doc.add_paragraph()
    doc.add_paragraph(
        "Thank you for your business. Payment is due within 30 days of the invoice date."
    )

    doc.save(path)


def build_invoice_full(path: Path) -> None:
    """Snake_case invoice that matches article1-client.md's document_values exactly."""
    doc = Document()

    _styled_heading(doc, "INVOICE", size=24)
    doc.add_paragraph("Foxit DocGen API Sample Template")
    doc.add_paragraph()

    p = doc.add_paragraph()
    p.add_run("Bill To: ").bold = True
    p.add_run("{{ customer_name }}")

    p = doc.add_paragraph()
    p.add_run("Invoice Number: ").bold = True
    p.add_run("{{ invoice_number }}")

    p = doc.add_paragraph()
    p.add_run("Invoice Date: ").bold = True
    p.add_run("{{ invoice_date }}")

    p = doc.add_paragraph()
    p.add_run("Due Date: ").bold = True
    p.add_run("{{ due_date }}")

    doc.add_paragraph()

    # Line-items table: header + loop row + subtotal/tax/total footer rows.
    table = doc.add_table(rows=6, cols=5)
    table.style = "Light Grid Accent 1"
    table.autofit = True

    headers = ["#", "Description", "Qty", "Unit Price", "Total"]
    for idx, text in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = ""
        run = cell.paragraphs[0].add_run(text)
        run.bold = True

    loop_row = table.rows[1].cells
    loop_row[0].text = "{{TableStart:line_items}}{{ROW_NUMBER}}"
    loop_row[1].text = "{{description}}"
    loop_row[2].text = "{{qty}}"
    loop_row[3].text = '{{unit_price \\# "$#,##0.00"}}'
    loop_row[4].text = '{{total \\# "$#,##0.00"}}{{TableEnd:line_items}}'

    # Footer rows: subtotal, tax, total due
    subtotal_row = table.rows[2].cells
    subtotal_row[0].text = ""
    subtotal_row[1].text = ""
    subtotal_row[2].text = ""
    subtotal_row[3].paragraphs[0].add_run("Subtotal:").bold = True
    subtotal_row[4].text = '{{subtotal \\# "$#,##0.00"}}'

    tax_row = table.rows[3].cells
    tax_row[0].text = ""
    tax_row[1].text = ""
    tax_row[2].text = ""
    tax_row[3].paragraphs[0].add_run("Tax Rate:").bold = True
    # Foxit's \# "0.00%" switch does not multiply by 100, so we render
    # tax_rate as a raw decimal (0.08). Articles can still teach the switch
    # against numeric currency fields where the multiply-by-100 is irrelevant.
    tax_row[4].text = "{{tax_rate}}"

    tax_amount_row = table.rows[4].cells
    tax_amount_row[0].text = ""
    tax_amount_row[1].text = ""
    tax_amount_row[2].text = ""
    tax_amount_row[3].paragraphs[0].add_run("Tax Amount:").bold = True
    tax_amount_row[4].text = '{{tax_amount \\# "$#,##0.00"}}'

    total_row = table.rows[5].cells
    total_row[0].text = ""
    total_row[1].text = ""
    total_row[2].text = ""
    total_row[3].paragraphs[0].add_run("Total Due:").bold = True
    p = total_row[4].paragraphs[0]
    run = p.add_run('{{total_due \\# "$#,##0.00"}}')
    run.bold = True

    doc.add_paragraph()
    doc.add_paragraph(
        "Thank you for your business. Payment is due within 30 days of the invoice date."
    )

    doc.save(path)


def render_via_api(template_path: Path, payload: dict, output_pdf: Path) -> dict:
    with template_path.open("rb") as fh:
        template_b64 = base64.b64encode(fh.read()).decode("utf-8")

    response = requests.post(
        f"{HOST}/document-generation/api/GenerateDocumentBase64",
        headers={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "Content-Type": "application/json",
        },
        json={
            "base64FileString": template_b64,
            "documentValues": payload,
            "outputFormat": "pdf",
        },
        timeout=60,
    )
    print(f"  HTTP {response.status_code} for {template_path.name}")
    response.raise_for_status()
    body = response.json()

    if "base64FileString" not in body:
        raise RuntimeError(f"Unexpected API response: {body}")

    pdf_bytes = base64.b64decode(body["base64FileString"])
    output_pdf.write_bytes(pdf_bytes)
    print(f"  wrote {output_pdf.name} ({len(pdf_bytes):,} bytes)")
    if not pdf_bytes.startswith(b"%PDF-"):
        raise RuntimeError(f"{output_pdf.name} is not a valid PDF")
    return body


SIMPLE_PAYLOAD = {
    "companyName": "Meridian Financial Group",
    "invoiceNumber": "INV-00471",
    "invoiceDate": "2024-01-15",
    "totalDue": 2500.00,
}

TABLE_PAYLOAD = {
    "companyName": "Meridian Financial Group",
    "invoiceDate": "2024-01-15",
    "invoiceNumber": "INV-00471",
    "lineItems": [
        {
            "description": "API Integration Consulting",
            "qty": 10,
            "unitPrice": 150.00,
            "lineTotal": 1500.00,
        },
        {
            "description": "Compliance Review",
            "qty": 5,
            "unitPrice": 200.00,
            "lineTotal": 1000.00,
        },
    ],
    "totalDue": 2500.00,
}

# Mirrors article1-client.md document_values exactly. If you change a key here,
# you MUST also update the article's Python sample, or the rendered PDF will
# have empty fields where readers expect populated data.
FULL_PAYLOAD = {
    "customer_name": "Acme Corporation",
    "invoice_number": "INV-2025-0042",
    "invoice_date": "07/15/2025",
    "due_date": "08/14/2025",
    "line_items": [
        {
            "description": "API Integration Consulting",
            "qty": 8,
            "unit_price": 195.00,
            "total": 1560.00,
        },
        {
            "description": "Document Automation Setup",
            "qty": 1,
            "unit_price": 750.00,
            "total": 750.00,
        },
    ],
    "subtotal": 2310.00,
    "tax_rate": 0.08,
    "tax_amount": 184.80,
    "total_due": 2494.80,
}


def main() -> int:
    simple_docx = HERE / "invoice_simple.docx"
    table_docx = HERE / "invoice_table.docx"
    full_docx = HERE / "invoice_full.docx"
    simple_pdf = HERE / "invoice_simple_test.pdf"
    table_pdf = HERE / "invoice_table_test.pdf"
    full_pdf = HERE / "invoice_full_test.pdf"

    print("Building templates...")
    build_invoice_simple(simple_docx)
    build_invoice_table(table_docx)
    build_invoice_full(full_docx)
    print(f"  {simple_docx.name} ({simple_docx.stat().st_size:,} bytes)")
    print(f"  {table_docx.name} ({table_docx.stat().st_size:,} bytes)")
    print(f"  {full_docx.name} ({full_docx.stat().st_size:,} bytes)")

    print("\nRendering invoice_simple.docx via Foxit DocGen API...")
    render_via_api(simple_docx, SIMPLE_PAYLOAD, simple_pdf)

    print("\nRendering invoice_table.docx via Foxit DocGen API...")
    render_via_api(table_docx, TABLE_PAYLOAD, table_pdf)

    print("\nRendering invoice_full.docx via Foxit DocGen API...")
    render_via_api(full_docx, FULL_PAYLOAD, full_pdf)

    print("\nAll templates rendered successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
