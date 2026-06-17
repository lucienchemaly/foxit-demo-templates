"""
Build agent_agreement.pdf, a Foxit eSign Text Tags sample for party 1.

The signature/initial/date/text placeholders below are parsed into interactive
fields when the PDF is uploaded to createfolder with "processTextTags": true.
Placeholders must use underscores (e.g. ${s:1:______}); an empty placeholder
like ${s:1: } does not produce a signature field and the folder cannot be sent.

Run:
    pip install reportlab
    python3 build_agent_agreement.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("agent_agreement.pdf", pagesize=letter)
c.setFont("Helvetica-Bold", 16)
c.drawString(72, 730, "Service Agreement")
c.setFont("Helvetica", 11)
c.drawString(72, 700, "This agreement was generated and routed for signature by an AI agent.")
c.drawString(72, 680, "By signing, party 1 accepts the terms of service.")
c.drawString(72, 630, "Full name: ${textfield:1:y:Name_of_signer:__________}")
c.drawString(72, 600, "Signature: ${s:1:______________}")
c.drawString(72, 570, "Initials: ${i:1:______}")
c.drawString(72, 540, "Date: ${datefield:1:n::____}")
c.save()
print("wrote agent_agreement.pdf")
