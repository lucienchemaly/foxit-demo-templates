# Foxit Demo Templates

Reference Word templates for the [Foxit DocGen API](https://developer-api.foxit.com/), built and verified end-to-end against the live API. Use them as-is for first-run testing, fork them as starting points for your own designs, or open them in Word to study Foxit's placeholder syntax in context.

## Templates

| File | Scenario | Tokens | Use it for |
|---|---|---|---|
| [`invoice_simple.docx`](invoice_simple.docx) | Invoice header only, scalar values | `{{ companyName }}`, `{{ invoiceNumber }}`, `{{ invoiceDate \@ MM/dd/yyyy }}`, `{{ totalDue \# "$#,##0.00" }}` | Smoke-testing the auth + request-response loop with the smallest possible payload |
| [`invoice_table.docx`](invoice_table.docx) | Full invoice with line items and a computed subtotal | All of the above, plus `{{TableStart:lineItems}}` / `{{TableEnd:lineItems}}` loop, `{{ROW_NUMBER}}`, `{{=SUM(ABOVE) \# "$#,##0.00"}}` | Validating dynamic table rendering, currency formatting on derived fields, and aggregate functions |

A pre-rendered PDF for each template (`invoice_simple_test.pdf`, `invoice_table_test.pdf`) is included so you can confirm what the API output should look like before running your own request.

## Quick start

```bash
git clone https://github.com/lucienchemaly/foxit-demo-templates.git
cd foxit-demo-templates

# Set your DocGen credentials from the Foxit developer console
export BASE_URL="https://na1.fusion.foxit.com"
export CLIENT_ID="your_client_id"
export CLIENT_SECRET="your_client_secret"

# Install dependencies and run the round-trip test
pip install python-docx requests pypdf
python build_templates.py
```

`build_templates.py` rebuilds both `.docx` files from scratch, posts them to `/document-generation/api/GenerateDocumentBase64`, and writes the rendered PDFs back to disk. It exits non-zero if any token fails to populate.

## Sending a template to the DocGen API

Minimal Python example (matches the article tutorial):

```python
import base64, os, requests

with open("invoice_table.docx", "rb") as f:
    template_b64 = base64.b64encode(f.read()).decode("utf-8")

response = requests.post(
    f"{os.environ['BASE_URL']}/document-generation/api/GenerateDocumentBase64",
    headers={
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "Content-Type": "application/json",
    },
    json={
        "base64FileString": template_b64,
        "documentValues": {
            "companyName": "Meridian Financial Group",
            "invoiceDate": "2024-01-15",
            "invoiceNumber": "INV-00471",
            "lineItems": [
                {"description": "API Integration Consulting", "qty": 10, "unitPrice": 150.00, "lineTotal": 1500.00},
                {"description": "Compliance Review", "qty": 5, "unitPrice": 200.00, "lineTotal": 1000.00},
            ],
            "totalDue": 2500.00,
        },
        "outputFormat": "pdf",
    },
)
pdf_bytes = base64.b64decode(response.json()["base64FileString"])
open("invoice.pdf", "wb").write(pdf_bytes)
```

## Verified Foxit DocGen syntax

Every pattern below was confirmed against the live API (`na1.fusion.foxit.com`, April 2026). If you build new templates, stick to these forms:

| Goal | Working syntax | Notes |
|---|---|---|
| Scalar substitution | `{{ companyName }}` | Spaces inside braces are tolerated. |
| Date formatting | `{{ invoiceDate \@ MM/dd/yyyy }}` | Standard Word date picture string. |
| Currency formatting | `{{ totalDue \# "$#,##0.00" }}` | Use Word's MERGEFIELD picture string, not a friendly keyword. |
| Other locales / decimals | `{{ amount \# "€#,##0.00" }}`, `{{ count \# "0" }}` | Any valid Word numeric picture works. |
| Repeating rows | `{{TableStart:items}} ... {{TableEnd:items}}` | Both delimiters must sit in cells of the same Word table row. |
| Auto row number | `{{ROW_NUMBER}}` | Inside a loop only. |
| Column subtotal | `{{=SUM(ABOVE) \# "$#,##0.00"}}` | In a footer row immediately below the loop. |

## Patterns that do NOT work

These were tested and confirmed broken. Do not put them in templates:

- `{{ totalDue \# Currency }}` — friendly keyword renders blank or as literal text. Use the picture string instead.
- `{{=qty*unitPrice}}` — inline arithmetic between fields is not evaluated. Compute derived values in your application and send them as JSON fields (this is why the table template's payload includes a precomputed `lineTotal`).
- `{{ field | Currency }}`, `{{ field:Currency }}` — pipe and colon syntaxes are unsupported.

## Adding a new template

1. Create the `.docx` either by hand in Word or programmatically (see `build_templates.py` for a `python-docx` builder pattern).
2. Add a builder function and a payload to `build_templates.py` so the round-trip is reproducible.
3. Run `python build_templates.py` and verify the rendered PDF is correct.
4. Commit the `.docx`, the test PDF, and the builder updates together.
5. Open a PR or push to `main`; the raw URL `https://github.com/lucienchemaly/foxit-demo-templates/raw/main/<file>.docx` is immediately available for tutorials to link.

## Troubleshooting

- Status `200` but a token rendered as blank: most likely a wrong format spec. Re-check the picture string against the table above.
- Status `401`: credentials missing or wrong. Confirm `client_id` and `client_secret` are sent as headers, not query parameters.
- Status `400` with "invalid base64": the template was sent as raw bytes. It must be base64-encoded as a UTF-8 string.
- Loop renders one row instead of N: `{{TableStart:array}}` and `{{TableEnd:array}}` are not in the same Word table row. Open the document in Word and confirm both tags sit in the same row of the same table.

## License

These templates are sample assets meant to accompany Foxit DocGen tutorials. Reuse freely.
