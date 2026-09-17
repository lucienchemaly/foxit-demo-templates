import io, json, os, re, time, zipfile
import requests

BASE_URL = "https://na1.fusion.foxit.com/pdf-services"
HEADERS = {
    "client_id": os.environ["FOXIT_CLIENT_ID"],
    "client_secret": os.environ["FOXIT_CLIENT_SECRET"],
}
POLL_SECONDS = 2
POLL_TIMEOUT = 120


def extract_structure(pdf_path: str) -> dict:
    with open(pdf_path, "rb") as f:
        upload = requests.post(
            f"{BASE_URL}/api/documents/upload",
            headers=HEADERS,
            files={"file": (os.path.basename(pdf_path), f, "application/pdf")},
        )
    upload.raise_for_status()
    document_id = upload.json()["documentId"]

    started = requests.post(
        f"{BASE_URL}/api/documents/pdf-structural-extract",
        headers=HEADERS,
        json={"documentId": document_id},
    )
    started.raise_for_status()
    task_id = started.json()["taskId"]

    deadline = time.monotonic() + POLL_TIMEOUT
    while True:
        task = requests.get(f"{BASE_URL}/api/tasks/{task_id}", headers=HEADERS)
        task.raise_for_status()
        task = task.json()
        if task["status"] == "COMPLETED":
            break
        if task["status"] == "FAILED":
            raise RuntimeError(f"task {task_id} FAILED: {task}")
        if time.monotonic() > deadline:
            raise TimeoutError(f"task {task_id} stuck at {task['status']}")
        time.sleep(POLL_SECONDS)

    result = requests.get(
        f"{BASE_URL}/api/documents/{task['resultDocumentId']}/download",
        headers=HEADERS,
    )
    result.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(result.content)) as zf:
        return json.loads(zf.read("StructureInfo.json"))


def element_text(element: dict) -> str:
    """Return an element's text, or '' when it carries none."""
    text = element.get("content", {}).get("text", "")
    return " ".join(text.split())


def cell_text(cell: dict) -> str:
    """Return a table cell's text, or '' when the cell is blank."""
    return element_text(cell.get("paragraph", {}))


FOOTER_LABELS = ("subtotal", "tax rate", "tax amount", "tax", "total due", "total")
HEADER_PATTERNS = {
    "vendor_name":    r"bill to:\s*(.+)",
    "invoice_number": r"invoice number:\s*(.+)",
    "invoice_date":   r"invoice date:\s*(.+)",
    "due_date":       r"due date:\s*(.+)",
    "payment_terms":  r"payment is due within (.+?) of",
}


def parse_invoice(structure_info: dict) -> dict:
    elements = structure_info["analyzeResult"]["elements"]
    invoice = {key: "" for key in HEADER_PATTERNS}
    invoice.update(line_items=[], subtotal="", tax="", total_due="")

    for element in elements:
        if element["type"] != "paragraph":
            continue
        text = element_text(element)
        for field, pattern in HEADER_PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not invoice[field]:
                invoice[field] = match.group(1).strip()

    tables = [e for e in elements if e["type"] == "table"]
    if not tables:
        return invoice

    grid: dict = {}
    for cell in tables[0]["content"]["body"]["cells"]:
        grid.setdefault(cell["rowIndex"], {})[cell["columnIndex"]] = cell_text(cell)

    columns = {name.lower(): i for i, name in grid.get(0, {}).items() if name}

    def column_for(*candidates, default):
        for candidate in candidates:
            for name, index in columns.items():
                if candidate in name:
                    return index
        return default

    description_col = column_for("description", "item", default=1)
    quantity_col = column_for("qty", "quantity", default=2)
    unit_price_col = column_for("unit price", default=3)
    line_total_col = column_for("total", "amount", default=4)

    for row_index in sorted(r for r in grid if r > 0):
        row = grid[row_index]
        label = next(
            (v.lower().rstrip(":").strip() for v in row.values()
             if v.lower().rstrip(":").strip() in FOOTER_LABELS),
            None,
        )
        if label:
            value = row[max(row)]
            if label == "subtotal":
                invoice["subtotal"] = value
            elif label == "tax amount":
                invoice["tax"] = value
            elif label in ("total due", "total"):
                invoice["total_due"] = value
            continue
        if row.get(description_col):
            invoice["line_items"].append({
                "description": row.get(description_col, ""),
                "quantity": row.get(quantity_col, ""),
                "unit_price": row.get(unit_price_col, ""),
                "line_total": row.get(line_total_col, ""),
            })

    return invoice


if __name__ == "__main__":
    structure = extract_structure(os.environ["INVOICE_PDF"])
    print(json.dumps(parse_invoice(structure), indent=2))
