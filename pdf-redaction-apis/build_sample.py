"""Builds sample-pii-record.pdf, the input for the PDF redaction APIs comparison.

Three lines of fake patient data plus Title/Author metadata, so a reader can see
both what pdf-redact removes from the page and what metadata it carries through.
"""
import pymupdf

doc = pymupdf.open()
page = doc.new_page(width=612, height=792)
page.insert_text((72, 100), "Patient: John Smith", fontsize=12)
page.insert_text((72, 130), "Social Security number: 123-45-6789", fontsize=12)
page.insert_text((72, 160), "Diagnosis: routine checkup", fontsize=12)
doc.set_metadata({"author": "Dr Jane Roe", "title": "John Smith record"})
doc.save("sample-pii-record.pdf")
print(repr(pymupdf.open("sample-pii-record.pdf")[0].get_text()))
