"""Builds the 5 mechanism diagrams for the PDF to Word APIs comparison.

Run: python3 build_diagrams.py  (writes PNGs next to this file)
The Foxit IDs in diagrams 2 and 3 come from live PDF Services runs on 2026-11-19
(invoice_table_test.pdf through pdf-to-word, invoice_table_scan.pdf through pdf-ocr then pdf-to-word).
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams['font.family'] = 'Arial'
OUT = os.path.dirname(os.path.abspath(__file__))
T1 = '#0b0b0b'; T2 = '#52514e'; PALE = '#f0efec'; EDGE = '#b9b8b2'
BLUE = '#2a78d6'; LBLUE = '#cde2fb'; ORANGE = '#eb6834'; LORANGE = '#fde0d3'
GREEN = '#1baf7a'; LGREEN = '#d3f1e5'; RED = '#c8372d'; LRED = '#f8d9d6'
PURPLE = '#7a5af5'; LPURPLE = '#e6e0fd'
MONO = 'Menlo'


def canvas(w, h):
    fig = plt.figure(figsize=(w, h), dpi=150, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, text='', fc=PALE, ec=EDGE, tc=T1, fs=11, bold=False,
        family=None, ha='center', ls='-', lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.01',
                                fc=fc, ec=ec, lw=lw, ls=ls))
    if text:
        tx = x + w / 2 if ha == 'center' else x + 0.012
        ax.text(tx, y + h / 2, text, ha=ha, va='center', fontsize=fs, color=tc,
                fontweight='bold' if bold else 'normal', linespacing=1.4,
                family=family or 'Arial')


def arrow(ax, x1, y1, x2, y2, c=T2, ls='-', rad=0.0, lw=1.4):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=14,
                                connectionstyle=f'arc3,rad={rad}'))


def title(ax, t, sub=None):
    ax.text(0.02, 0.945, t, fontsize=16, fontweight='bold', color=T1, va='center')
    if sub:
        ax.text(0.02, 0.895, sub, fontsize=10.5, color=T2, va='center')


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=150, facecolor='white')
    plt.close(fig)


# 1. Fixed coordinates vs flowing structure -----------------------------------
fig, ax = canvas(13, 7.2)
title(ax, 'Same PDF page, two kinds of DOCX',
      'A PDF stores each glyph run at an absolute (x, y) position. What the converter does with '
      'those positions decides whether Word can reflow the result.')
# PDF page
box(ax, 0.02, 0.12, 0.22, 0.68, '', fc='white', ec=T2)
ax.text(0.13, 0.765, 'PDF page (fixed layout)', ha='center', fontsize=11, fontweight='bold')
glyphs = [('INVOICE', 0.04, 0.70, '(72, 720)'), ('Bill To: Meridian', 0.04, 0.63, '(72, 655)'),
          ('Invoice Number: INV-00471', 0.04, 0.56, '(72, 630)')]
for t, x, y, c in glyphs:
    ax.text(x, y, t, fontsize=9.5, color=T1)
    ax.text(x, y - 0.025, 'Tm ' + c, fontsize=7.5, color=BLUE, family=MONO)
for r in range(3):
    for col in range(3):
        x = 0.04 + col * 0.063; y = 0.42 - r * 0.07
        ax.add_patch(Rectangle((x, y), 0.06, 0.05, fc='none', ec=EDGE, lw=0.8, ls=':'))
        ax.text(x + 0.004, y + 0.03, 'text', fontsize=7.5, color=T1)
        ax.text(x + 0.004, y + 0.008, f'({110 + col * 90},{400 - r * 30})', fontsize=6, color=BLUE,
                family=MONO)
ax.text(0.13, 0.17, 'Lines and text runs, no "table"\nobject, no "paragraph" object',
        ha='center', fontsize=9, color=T2, linespacing=1.3)

# top path: coordinate mapping
arrow(ax, 0.245, 0.60, 0.365, 0.63, c=RED)
ax.text(0.305, 0.665, 'Coordinate\nmapping', ha='center', fontsize=10.5, fontweight='bold', color=RED, linespacing=1.2)
box(ax, 0.37, 0.50, 0.29, 0.26, '', fc='white', ec=RED)
ax.text(0.38, 0.735, 'DOCX with absolute text boxes', fontsize=11, fontweight='bold', color=RED,
        va='center')
for i, (t, y) in enumerate([('w:txbxContent  "INVOICE"', 0.68), ('w:framePr x=72 y=655', 0.63),
                            ('w:txbxContent  "text"  x 9 cells', 0.58)]):
    box(ax, 0.385, y - 0.02, 0.26, 0.04, t, fc=LRED, ec=RED, fs=8.5, family=MONO, ha='left',
        ls='--', lw=0.9)
ax.text(0.385, 0.522, 'Looks right. Change a margin and boxes stay put.',
        fontsize=9, color=T2)
box(ax, 0.69, 0.50, 0.29, 0.26,
    'Edit result\n\n- Text does not reflow\n- Search and select break across boxes\n'
    '- Mail merge and code see loose\n  boxes, not rows and cells',
    fc=PALE, ec=RED, fs=9.5, ha='left')
arrow(ax, 0.66, 0.63, 0.69, 0.63, c=RED)

# bottom path: structure rebuilding
arrow(ax, 0.245, 0.36, 0.365, 0.22, c=GREEN)
ax.text(0.305, 0.33, 'Structure\nrebuilding', ha='center', fontsize=10.5, fontweight='bold', color=GREEN, linespacing=1.2)
box(ax, 0.37, 0.08, 0.29, 0.27, '', fc='white', ec=GREEN)
ax.text(0.38, 0.325, 'DOCX with flowing paragraphs and a table', fontsize=11, fontweight='bold',
        color=GREEN, va='center')
for t, y in [('w:p  "INVOICE"', 0.275), ('w:p  "Bill To: Meridian ..."', 0.235)]:
    box(ax, 0.385, y - 0.018, 0.26, 0.036, t, fc=LGREEN, ec=GREEN, fs=8.5, family=MONO, ha='left',
        lw=0.9)
box(ax, 0.385, 0.095, 0.26, 0.11, '', fc=LGREEN, ec=GREEN, lw=0.9)
ax.text(0.392, 0.19, 'w:tbl', fontsize=8.5, family=MONO, color=T1)
for r in range(2):
    ax.text(0.41, 0.155 - r * 0.04, 'w:tr', fontsize=8, family=MONO, color=T1)
    for col in range(3):
        ax.add_patch(Rectangle((0.45 + col * 0.063, 0.142 - r * 0.04), 0.058, 0.03, fc='white',
                               ec=GREEN, lw=0.8))
        ax.text(0.479 + col * 0.063, 0.157 - r * 0.04, 'w:tc', fontsize=7.5, family=MONO,
                ha='center', va='center')
box(ax, 0.69, 0.08, 0.29, 0.27,
    'Edit result\n\n- Paragraphs reflow when font or\n  margins change\n'
    '- Rows and cells are addressable\n  through the OOXML object model\n'
    '- Outline view shows no text boxes',
    fc=PALE, ec=GREEN, fs=9.5, ha='left')
arrow(ax, 0.66, 0.215, 0.69, 0.215, c=GREEN)
save(fig, 'fixed-vs-flow')

# 2. Foxit async sequence ------------------------------------------------------
fig, ax = canvas(13, 8.2)
title(ax, 'One PDF to Word conversion with the Foxit PDF Services API',
      'Every call carries the client_id and client_secret headers. IDs are from a live run on '
      'the sample invoice.')
xc, xs = 0.14, 0.80
for x, lab in [(xc, 'Your backend\n(convert.sh)'), (xs, 'na1.fusion.foxit.com\n/pdf-services/api')]:
    box(ax, x - 0.11, 0.78, 0.22, 0.08, lab, fc=LBLUE if x == xc else LORANGE,
        ec=BLUE if x == xc else ORANGE, fs=11, bold=True)
    ax.plot([x, x], [0.05, 0.78], color=EDGE, lw=1.4, ls='--')


def msg(y, text, c, back=None, back_c=None, note=None):
    arrow(ax, xc, y, xs, y, c=c)
    ax.text((xc + xs) / 2, y + 0.018, text, ha='center', fontsize=10, family=MONO, color=T1)
    if back:
        arrow(ax, xs, y - 0.055, xc, y - 0.055, c=back_c or T2, ls='--')
        ax.text((xc + xs) / 2, y - 0.04, back, ha='center', fontsize=9.5, family=MONO, color=T2)
    if note:
        ax.text(xs + 0.015, y - 0.02, note, fontsize=9.5, color=c, va='center', fontweight='bold')


msg(0.71, 'POST documents/upload   (multipart, field "file")', BLUE,
    '200  {"documentId": "6afe459e2752dc0c4fd79c11"}', note='free')
msg(0.57, 'POST documents/convert/pdf-to-word   {"documentId": ...}', ORANGE,
    '202  {"taskId": "6afe459f26e6344129664aca"}', note='1 credit')
# poll loop
box(ax, 0.06, 0.20, 0.88, 0.26, '', fc='none', ec=PURPLE, ls='--')
ax.text(0.155, 0.435, 'loop every 3 s', fontsize=10, color=PURPLE, fontweight='bold')
msg(0.40, 'GET tasks/{taskId}', PURPLE,
    '200  {"status": "PENDING" | "IN_PROGRESS", "progress": ...}', note='free')
arrow(ax, xs, 0.27, xc, 0.27, c=GREEN, ls='--')
ax.text((xc + xs) / 2, 0.285, 'until  "status": "COMPLETED", "resultDocumentId": "..."',
        ha='center', fontsize=9.5, family=MONO, color=GREEN)
ax.text((xc + xs) / 2, 0.225, 'or  "status": "FAILED"  (print the task response and stop)',
        ha='center', fontsize=9.5, family=MONO, color=RED)
msg(0.14, 'GET documents/{resultDocumentId}/download', GREEN,
    '200  DOCX bytes  ->  converted.docx', note='free')
save(fig, 'foxit-async-flow')

# 3. OCR chain for scanned PDFs -----------------------------------------------
fig, ax = canvas(13, 7.6)
title(ax, 'Scanned PDFs: convert directly, or run OCR first',
      'A scan is a page image with no text layer. Foxit runs OCR as its own task, other APIs fold it '
      'into the conversion call.')
box(ax, 0.02, 0.62, 0.13, 0.12, 'Scanned PDF\n(page image only)', fc=PALE, ec=T2, fs=10, bold=True)
box(ax, 0.19, 0.62, 0.11, 0.12, 'upload\n-> documentId', fc=LBLUE, ec=BLUE, fs=9.5, family=MONO)
arrow(ax, 0.15, 0.68, 0.19, 0.68)
# wrong path
arrow(ax, 0.30, 0.71, 0.36, 0.79, c=RED)
box(ax, 0.36, 0.75, 0.24, 0.08, 'pdf-to-word -> poll -> download', fc=LRED, ec=RED, fs=9.5,
    family=MONO)
arrow(ax, 0.60, 0.79, 0.64, 0.79, c=RED)
box(ax, 0.64, 0.74, 0.34, 0.10, 'DOCX holds 1 inline page image\nand no selectable text',
    fc='white', ec=RED, fs=10)
ax.text(0.36, 0.855, 'Direct call (1 credit)', fontsize=10, color=RED, fontweight='bold')
# right path
arrow(ax, 0.30, 0.65, 0.36, 0.58, c=GREEN)
ax.text(0.36, 0.635, 'OCR chain (2 credits)', fontsize=10, color=GREEN, fontweight='bold')
steps = [('pdf-ocr\n{config: {languages,\nmakeEditable: true}}', 0.36, 0.16),
         ('poll task\n-> resultDocumentId', 0.545, 0.13),
         ('pdf-to-word\non the OCR result', 0.70, 0.12), ('poll ->\ndownload', 0.845, 0.11)]
for t, x, w in steps:
    box(ax, x, 0.50, w, 0.12, t, fc=LGREEN, ec=GREEN, fs=9, family=MONO)
for x1, x2 in [(0.52, 0.545), (0.675, 0.70), (0.82, 0.845)]:
    arrow(ax, x1, 0.56, x2, 0.56, c=GREEN)
arrow(ax, 0.90, 0.50, 0.90, 0.45, c=GREEN)
box(ax, 0.60, 0.33, 0.38, 0.11,
    'DOCX keeps the page image behind the recognized text.\n'
    'Recovered text depends on scan quality, and scanned\ntables come back as paragraphs.',
    fc='white', ec=GREEN, fs=9.5)
# contrast lane
ax.plot([0.02, 0.98], [0.27, 0.27], color=EDGE, lw=1)
ax.text(0.02, 0.235, 'OCR inside the conversion call', fontsize=11.5, fontweight='bold', color=T1)
for i, (t, sub) in enumerate([('ConvertAPI', 'POST convert/pdf/to/docx\nOcrMode: auto (default)\nthe same call returns the DOCX'),
                              ('CloudConvert', 'convert task pdf -> docx\nimages_ocr: true (default)\nOCR runs inside that task')]):
    x = 0.02 + i * 0.49
    box(ax, x, 0.06, 0.13, 0.12, t, fc=LPURPLE, ec=PURPLE, fs=10.5, bold=True)
    arrow(ax, x + 0.13, 0.12, x + 0.17, 0.12, c=PURPLE)
    box(ax, x + 0.17, 0.06, 0.28, 0.12, sub, fc='white', ec=PURPLE,
        fs=9, family=MONO)
save(fig, 'ocr-chain')

# 4. Execution models ----------------------------------------------------------
fig, ax = canvas(13, 7.0)
title(ax, 'Three execution models across the 8 APIs',
      'Where your code waits for the DOCX decides how you handle large files and timeouts.')
lanes = [
    ('Async task or job', 'Foxit, Adobe, CloudConvert (default)', BLUE, LBLUE,
     ['submit file', 'get task or job ID', 'poll status', 'fetch result'],
     'Caller is free between polls. Suits large files and queue workers.'),
    ('Synchronous HTTP', 'Nutrient /build, Aspose.Words Cloud,\nConvertAPI and pdfRest (default)',
     ORANGE, LORANGE, ['send file', 'connection held open', 'DOCX in the response'],
     'Simplest code. The calling thread waits for the whole conversion.\n'
     'ConvertAPI offers async jobs, pdfRest offers requestId polling.'),
    ('In-process library', 'Apryse Server SDK', GREEN, LGREEN,
     ['call the SDK in your process', 'DOCX written locally'],
     'No network hop. Your servers supply the CPU and memory.'),
]
for i, (name, who, c, lc, steps, note) in enumerate(lanes):
    y = 0.62 - i * 0.255
    box(ax, 0.02, y, 0.24, 0.19, '', fc=lc, ec=c)
    ax.text(0.03, y + 0.14, name, fontsize=12.5, fontweight='bold', color=T1, va='center')
    ax.text(0.03, y + 0.06, who, fontsize=9.5, color=T2, va='center', linespacing=1.3)
    n = len(steps); w = 0.68 / n - 0.03
    for j, s in enumerate(steps):
        x = 0.29 + j * (w + 0.03)
        box(ax, x, y + 0.085, w, 0.08, s, fc='white', ec=c, fs=10)
        if j:
            arrow(ax, x - 0.03, y + 0.125, x, y + 0.125, c=c)
    if i == 0:
        arrow(ax, 0.29 + 2 * (w + 0.03) + w * 0.75, y + 0.165, 0.29 + 2 * (w + 0.03) + w * 0.25,
              y + 0.165, c=c, rad=0.9)
        ax.text(0.29 + 2 * (w + 0.03) + w * 0.8, y + 0.21, 'repeat until done', ha='left', fontsize=9,
                color=c)
    ax.text(0.29, y + 0.035, note, fontsize=9.5, color=T2, va='center', linespacing=1.3)
save(fig, 'execution-models')

# 5. Deployment and data path ---------------------------------------------------
fig, ax = canvas(13, 7.6)
title(ax, 'Where the document travels in each deployment model',
      'The dashed line is your network boundary.')
box(ax, 0.02, 0.10, 0.62, 0.74, '', fc='none', ec=T1, ls='--', lw=1.6)
ax.text(0.03, 0.815, 'Your network', fontsize=11.5, fontweight='bold', color=T1)
# app
box(ax, 0.05, 0.62, 0.16, 0.13, 'Your application', fc=PALE, ec=T2, fs=11, bold=True)
# self-hosted container
box(ax, 0.27, 0.40, 0.34, 0.20,
    'Self-hosted container\n\nAspose.Words Cloud Docker image\nNutrient Document Engine\n'
    'pdfRest on AWS or as a container', fc=LORANGE, ec=ORANGE, fs=9.5)
# embedded
box(ax, 0.05, 0.14, 0.40, 0.20,
    'Embedded SDK, in process\n\nApryse Server SDK\nFoxit PDF Conversion SDK\n(separately licensed)',
    fc=LGREEN, ec=GREEN, fs=9.5)
arrow(ax, 0.13, 0.62, 0.13, 0.34, c=GREEN)
ax.text(0.14, 0.48, 'library call,\nzero egress', fontsize=9, color=GREEN)
arrow(ax, 0.21, 0.66, 0.27, 0.55, c=ORANGE)
ax.text(0.215, 0.555, 'stays\ninside', fontsize=9, color=ORANGE)
# cloud
box(ax, 0.70, 0.46, 0.28, 0.38,
    'Hosted cloud REST\n\nFoxit PDF Services API, Adobe,\nNutrient DWS, Aspose.Words Cloud,\n'
    'ConvertAPI, CloudConvert, pdfRest\n\nRegion options: Adobe US or EU,\npdfRest EU endpoint',
    fc=LBLUE, ec=BLUE, fs=9.5)
arrow(ax, 0.21, 0.71, 0.70, 0.71, c=BLUE)
ax.text(0.45, 0.725, 'document leaves your network', ha='center', fontsize=9.5, color=BLUE)
arrow(ax, 0.70, 0.64, 0.21, 0.64, c=BLUE, ls='--')
ax.text(0.45, 0.615, 'DOCX comes back', ha='center', fontsize=9.5, color=BLUE)
# caveat
box(ax, 0.70, 0.14, 0.28, 0.20,
    "Foxit Conversion SDK's\nenable_ml_recognition setting\nroutes to an online recognition\n"
    'service, so leave it off when\nnothing may leave the network',
    fc=LRED, ec=RED, fs=9.5)
arrow(ax, 0.45, 0.24, 0.70, 0.24, c=RED, ls='--')
ax.text(0.575, 0.255, 'egress again', ha='center', fontsize=9, color=RED)
ax.text(0.02, 0.045, 'Variable-volume SaaS pipelines fit hosted cloud REST. Air-gapped or zero-egress '
        'environments need the embedded SDK path.', fontsize=10, color=T2)
save(fig, 'deployment-data-path')
