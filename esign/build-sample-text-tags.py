"""Build a Foxit eSign sample PDF with Text Tags for party 1."""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

OUT = "/tmp/sample-text-tags.pdf"

c = canvas.Canvas(OUT, pagesize=letter)
width, height = letter

c.setFont("Helvetica-Bold", 16)
c.drawString(1 * inch, height - 1 * inch, "Service Agreement")

c.setFont("Helvetica", 11)
body = [
    "This sample document demonstrates Foxit eSign Text Tags for party 1.",
    "The tags below are parsed into interactive fields on upload.",
    "",
    "Full name (required text field):",
    "${t:1:y:Full_Name:__________}",
    "",
    "Please initial here:  ${i:1:______}",
    "",
    "Date:  ${d:1:n::____}",
    "",
    "Signature:",
    "${s:1: }",
]
y = height - 1.6 * inch
for line in body:
    c.drawString(1 * inch, y, line)
    y -= 0.35 * inch

c.showPage()
c.save()
print("wrote", OUT)
