"""Builds the 3 mechanism diagrams for the PDF to Excel APIs comparison.

Run: python3 build_diagrams.py  (writes PNGs next to this file)
The Foxit IDs in foxit-async-flow come from a live PDF Services run on 2026-11-25
(a scanned table page through analyze/pdf-ocr, then convert/pdf-to-excel).
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


def badge(ax, x, y, n):
    ax.text(x, y, str(n), ha='center', va='center', fontsize=9, color='white',
            fontweight='bold', zorder=6,
            bbox=dict(boxstyle='circle,pad=0.3', fc=RED, ec=RED))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=150, facecolor='white')
    plt.close(fig)


# 1. From positioned text to cells ---------------------------------------------
fig, ax = canvas(13, 7.4)
title(ax, 'How a converter turns a PDF page into spreadsheet cells',
      'The page holds positioned text and lines, not cells. Every row and column in the workbook '
      'is an inference. Red numbers mark where errors enter.')

# PDF page
box(ax, 0.02, 0.10, 0.25, 0.72, '', fc='white', ec=T2)
ax.text(0.145, 0.79, 'What the PDF page stores', ha='center', fontsize=11, fontweight='bold')
runs = [('Region', 0.04, 0.70, '(72,700)'), ('Q1', 0.12, 0.70, '(160,700)'),
        ('Q2', 0.19, 0.70, '(230,700)'), ('North', 0.04, 0.62, '(72,672)'),
        ('1,200', 0.12, 0.62, '(160,672)'), ('1,350', 0.19, 0.62, '(230,672)')]
for t, x, y, c in runs:
    ax.text(x, y, t, fontsize=9.5, color=T1)
    ax.text(x, y - 0.025, c, fontsize=6.5, color=BLUE, family=MONO)
ax.plot([0.035, 0.255], [0.665, 0.665], color=T2, lw=1.2)
ax.plot([0.035, 0.255], [0.585, 0.585], color=T2, lw=1.2)
ax.text(0.04, 0.545, 'Text runs at (x, y) glyph coordinates', fontsize=8.5, color=BLUE)
ax.text(0.04, 0.515, 'Vector rules (ruling lines)', fontsize=8.5, color=T2)
box(ax, 0.035, 0.40, 0.22, 0.08, 'Optional tags: Table, TR, TH, TD', fc=LGREEN, ec=GREEN,
    fs=8.5, family=MONO, ls='--', lw=0.9)
box(ax, 0.035, 0.27, 0.22, 0.10, 'Scanned page: one image,\nno text runs at all', fc=PALE,
    ec=T2, fs=8.5, ls='--', lw=0.9)
ax.text(0.145, 0.16, 'No cell, row, or column objects', ha='center', fontsize=9.5,
        color=RED, fontweight='bold')

# OCR (optional)
box(ax, 0.31, 0.25, 0.15, 0.13, 'OCR\n(image-only pages)', fc=LPURPLE, ec=PURPLE, fs=10,
    bold=True, ls='--')
arrow(ax, 0.255, 0.32, 0.31, 0.32, c=PURPLE, ls='--')
badge(ax, 0.30, 0.395, 4)
ax.text(0.385, 0.215, 'adds text runs, can\nmisread digits (8 vs 3)', ha='center', fontsize=8.5,
        color=T2, linespacing=1.3)
arrow(ax, 0.46, 0.32, 0.51, 0.46, c=PURPLE, ls='--')

# Inference
box(ax, 0.51, 0.40, 0.22, 0.38, '', fc=LBLUE, ec=BLUE)
ax.text(0.62, 0.75, 'Table inference', ha='center', fontsize=11.5, fontweight='bold', color=BLUE)
steps = ['Find table regions', 'Group x positions\ninto columns', 'Group y positions\ninto rows',
         'Use ruling lines and\ntags when present']
for i, s in enumerate(steps):
    ax.text(0.53, 0.69 - i * 0.075, '- ' + s, fontsize=9.5, color=T1, va='top', linespacing=1.25)
arrow(ax, 0.27, 0.62, 0.51, 0.62, c=BLUE)
badge(ax, 0.685, 0.595, 1)
badge(ax, 0.71, 0.595, 2)
badge(ax, 0.685, 0.52, 3)

# XLSX
box(ax, 0.77, 0.40, 0.21, 0.38, '', fc='white', ec=GREEN)
ax.text(0.875, 0.75, 'XLSX cells', ha='center', fontsize=11.5, fontweight='bold', color=GREEN)
cells = [['Region', 'Q1', 'Q2'], ['North', "'1,200", '1350']]
for r, row in enumerate(cells):
    for c, v in enumerate(row):
        x = 0.785 + c * 0.062; y = 0.66 - r * 0.06
        ax.add_patch(Rectangle((x, y), 0.06, 0.05, fc=LGREEN if r == 0 else 'white', ec=GREEN, lw=0.8))
        ax.text(x + 0.03, y + 0.025, v, ha='center', va='center', fontsize=8.5,
                color=RED if v.startswith("'") else T1, family=MONO)
ax.text(0.785, 0.53, "'1,200 = number stored as text", fontsize=8.5, color=RED)
ax.text(0.785, 0.495, 'SUM() skips it', fontsize=8.5, color=RED)
badge(ax, 0.97, 0.52, 5)
arrow(ax, 0.73, 0.69, 0.77, 0.69, c=GREEN)

# Legend
box(ax, 0.51, 0.06, 0.47, 0.28, '', fc=PALE, ec=EDGE)
ax.text(0.525, 0.31, 'Where errors enter', fontsize=11, fontweight='bold', color=RED, va='center')
legend = ['1  Column grouping: borderless or tightly spaced columns merge or split',
          '2  Merged headers: a header spanning 2 columns lands in only one',
          '3  Multi-page tables: the header repeats as a data row on each page',
          '4  OCR misreads: a wrong digit still looks like a valid number',
          '5  Numbers as text: separators or currency symbols keep values as strings']
for i, s in enumerate(legend):
    ax.text(0.525, 0.265 - i * 0.042, s, fontsize=9.3, color=T1, va='center')
save(fig, 'pdf-to-cells-inference')

# 2. Where OCR happens -----------------------------------------------------------
fig, ax = canvas(13, 7.2)
title(ax, 'Three places OCR can happen for a scanned report',
      'The topology decides how many requests you send and how many billing units a scanned '
      'file uses.')
cols = [(0.02, 'Inside the conversion call', BLUE, LBLUE,
         ['ConvertAPI (OcrMode auto)', 'PDF.co (OCRMode Auto)', 'Adobe Export PDF (ocrLang)']),
        (0.35, 'Chained in one request', PURPLE, LPURPLE,
         ['Nutrient DWS Processor', 'Build: OCR action then xlsx output',
          'skipOcrForSearchableDocuments']),
        (0.68, 'Separate OCR call first', ORANGE, LORANGE,
         ['Foxit (analyze/pdf-ocr)', 'CloudConvert (pdf/ocr)', 'pdfRest (pdf-with-ocr-text)',
          'Stirling PDF (misc/ocr-pdf)'])]
for x, head, c, lc, names in cols:
    box(ax, x, 0.08, 0.30, 0.76, '', fc='white', ec=c)
    ax.text(x + 0.15, 0.81, head, ha='center', fontsize=12.5, fontweight='bold', color=c)
for i, n in enumerate(cols[0][4]):
    ax.text(0.035, 0.75 - i * 0.04, '- ' + n, fontsize=9.5, color=T1, va='center')
for i, n in enumerate(cols[1][4]):
    ax.text(0.365, 0.75 - i * 0.04, '- ' + n, fontsize=9.5, color=T1, va='center',
            family=MONO if i == 2 else 'Arial')
for i, n in enumerate(cols[2][4]):
    ax.text(0.695, 0.75 - i * 0.04, '- ' + n, fontsize=9.5, color=T1, va='center')

# column 1 flow
box(ax, 0.06, 0.50, 0.22, 0.07, 'Scanned PDF', fc=PALE, ec=T2, fs=10, bold=True)
arrow(ax, 0.17, 0.50, 0.17, 0.45, c=BLUE)
box(ax, 0.04, 0.31, 0.26, 0.14, 'One conversion request\nOCR + table inference + XLSX',
    fc=LBLUE, ec=BLUE, fs=10)
arrow(ax, 0.17, 0.31, 0.17, 0.26, c=BLUE)
box(ax, 0.08, 0.19, 0.18, 0.07, 'XLSX', fc=LGREEN, ec=GREEN, fs=10, bold=True)
ax.text(0.17, 0.125, '1 request. OCR billed inside\nthe conversion price',
        ha='center', fontsize=9, color=T2, linespacing=1.3)

# column 2 flow
box(ax, 0.39, 0.50, 0.22, 0.07, 'Scanned PDF', fc=PALE, ec=T2, fs=10, bold=True)
arrow(ax, 0.50, 0.50, 0.50, 0.45, c=PURPLE)
box(ax, 0.37, 0.29, 0.26, 0.16, '', fc=LPURPLE, ec=PURPLE)
ax.text(0.50, 0.425, 'One Build request', ha='center', fontsize=10, color=T1)
box(ax, 0.385, 0.35, 0.10, 0.05, 'OCR action', fc='white', ec=PURPLE, fs=8.5)
arrow(ax, 0.485, 0.375, 0.515, 0.375, c=PURPLE)
box(ax, 0.515, 0.35, 0.10, 0.05, 'output: xlsx', fc='white', ec=PURPLE, fs=8.5, family=MONO)
ax.text(0.50, 0.31, 'no second upload', ha='center', fontsize=8.5, color=T2)
arrow(ax, 0.50, 0.29, 0.50, 0.26, c=PURPLE)
box(ax, 0.41, 0.19, 0.18, 0.07, 'XLSX', fc=LGREEN, ec=GREEN, fs=10, bold=True)
ax.text(0.50, 0.125, '1 request. Conversion fee plus\n$0.0015 per OCR page',
        ha='center', fontsize=9, color=T2, linespacing=1.3)

# column 3 flow
box(ax, 0.72, 0.53, 0.22, 0.06, 'Scanned PDF', fc=PALE, ec=T2, fs=10, bold=True)
arrow(ax, 0.83, 0.53, 0.83, 0.50, c=ORANGE)
box(ax, 0.72, 0.43, 0.22, 0.07, 'Request 1: OCR\n-> searchable PDF', fc=LORANGE, ec=ORANGE, fs=9.5)
arrow(ax, 0.83, 0.43, 0.83, 0.40, c=ORANGE)
box(ax, 0.72, 0.33, 0.22, 0.07, 'Request 2: PDF to Excel', fc=LORANGE, ec=ORANGE, fs=9.5)
arrow(ax, 0.83, 0.33, 0.83, 0.26, c=ORANGE)
box(ax, 0.74, 0.19, 0.18, 0.07, 'XLSX', fc=LGREEN, ec=GREEN, fs=10, bold=True)
ax.text(0.83, 0.125, '2 requests. Foxit +1 credit, CloudConvert\n+1 base credit, pdfRest +1 Pro '
        'Tool call,\nStirling counts toward the allowance',
        ha='center', fontsize=8.6, color=T2, linespacing=1.3)
ax.text(0.02, 0.035, 'PDFTables takes a fourth route: its AI extractors read scans directly '
        'at 2 credits per page instead of 1.', fontsize=9.5, color=T2)
save(fig, 'ocr-placement-patterns')

# 3. Foxit async sequence ---------------------------------------------------------
fig, ax = canvas(13, 9.0)
title(ax, 'One PDF to Excel conversion with the Foxit PDF Services API',
      'IDs are from a live run on a scanned table page. Every call counts toward the rate limit '
      '(15/min sandbox, 100/min production).')
xc, xs = 0.13, 0.80
for x, lab in [(xc, 'Your backend'), (xs, 'na1.fusion.foxit.com')]:
    box(ax, x - 0.11, 0.80, 0.22, 0.06, lab, fc=LBLUE if x == xc else LORANGE,
        ec=BLUE if x == xc else ORANGE, fs=11, bold=True)
    ax.plot([x, x], [0.03, 0.80], color=EDGE, lw=1.4, ls='--')


def msg(y, text, c, back=None, back_c=None, note=None, note_c=None):
    arrow(ax, xc, y, xs, y, c=c)
    ax.text((xc + xs) / 2, y + 0.014, text, ha='center', fontsize=9.6, family=MONO, color=T1)
    if back:
        arrow(ax, xs, y - 0.045, xc, y - 0.045, c=back_c or T2, ls='--')
        ax.text((xc + xs) / 2, y - 0.033, back, ha='center', fontsize=9.2, family=MONO, color=T2)
    if note:
        ax.text(xs + 0.015, y - 0.02, note, fontsize=9.5, color=note_c or c, va='center',
                fontweight='bold')


msg(0.75, 'POST /oauth/token   (grant_type=client_credentials)', T2,
    '200  {"access_token": "eyJhbGciOi...", "expires_in": ...}', note='free')
ax.text(xc + 0.01, 0.685, 'Send Authorization: Bearer <token> on every call below',
        fontsize=9, color=BLUE)
msg(0.64, 'POST /pdf-services/api/documents/upload   (multipart "file")', BLUE,
    '200  {"documentId": "6b07555eead7f178a28485f2"}', note='free')
box(ax, 0.035, 0.455, 0.90, 0.10, '', fc='none', ec=PURPLE, ls='--')
ax.text(0.045, 0.54, 'scanned file only', fontsize=9, color=PURPLE, fontweight='bold')
msg(0.525, 'POST .../documents/analyze/pdf-ocr  -> poll -> resultDocumentId', PURPLE,
    'searchable PDF  {"resultDocumentId": "6b0755752513604fe19feb1b"}', note='1 credit')
msg(0.415, 'POST .../documents/convert/pdf-to-excel   {"documentId": ...}', ORANGE,
    '202  {"taskId": "6b075578bf87271040c21175"}', note='1 credit')
box(ax, 0.035, 0.155, 0.90, 0.175, '', fc='none', ec=T2, ls='--')
ax.text(0.045, 0.315, 'loop every 3 s', fontsize=9, color=T2, fontweight='bold')
msg(0.285, 'GET /pdf-services/api/tasks/{taskId}', T2,
    '200  {"status": "PENDING" | "IN_PROGRESS", "progress": ...}', note='free')
arrow(ax, xs, 0.185, xc, 0.185, c=GREEN, ls='--')
ax.text((xc + xs) / 2, 0.197, '{"status": "COMPLETED", "resultDocumentId": "6b0755796e25117323b97d0e"}',
        ha='center', fontsize=9.2, family=MONO, color=GREEN)
msg(0.10, 'GET /pdf-services/api/documents/{resultDocumentId}/download', GREEN,
    '200  XLSX bytes  ->  report.xlsx', note='free')
save(fig, 'foxit-async-flow')
