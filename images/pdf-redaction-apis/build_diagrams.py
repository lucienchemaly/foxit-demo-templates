"""Builds the 4 mechanism diagrams for the PDF redaction APIs comparison.

Run: python3 build_diagrams.py  (writes PNGs next to this file)
The overlay/true/raster outputs in diagram 2 come from a local PyMuPDF + pdftotext run,
and the Foxit call sequence in diagram 3 from a live PDF Services run on 2026-11-19.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.family'] = 'Arial'
OUT = os.path.dirname(os.path.abspath(__file__))
T1 = '#0b0b0b'; T2 = '#52514e'; GRID = '#d9d8d3'; PALE = '#f0efec'
BLUE = '#2a78d6'; LIGHTBLUE = '#cde2fb'; ORANGE = '#eb6834'; LORANGE = '#fde0d3'
GREEN = '#1baf7a'; LGREEN = '#d3f1e5'; RED = '#c8372d'; LRED = '#f8d9d6'
MONO = 'Menlo'


def canvas(w, h):
    fig = plt.figure(figsize=(w, h), dpi=150, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, text='', fc=PALE, ec='#b9b8b2', tc=T1, fs=11, bold=False,
        family=None, ha='center', ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.01',
                                fc=fc, ec=ec, lw=1.2, ls=ls))
    if text:
        tx = x + w / 2 if ha == 'center' else x + 0.012
        ax.text(tx, y + h / 2, text, ha=ha, va='center', fontsize=fs, color=tc,
                fontweight='bold' if bold else 'normal', linespacing=1.4,
                family=family or 'Arial')


def arrow(ax, x1, y1, x2, y2, c=T2, ls='-'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=1.4, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=14))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=150, facecolor='white')
    plt.close(fig)


# 1. Archetype map ---------------------------------------------------------
fig, ax = canvas(12, 5.2)
ax.text(0.02, 0.92, 'The 3 PDF redaction API archetypes and the 9 tools in each',
        fontsize=16, fontweight='bold', color=T1)
cols = [
    ('Enterprise SDK-first engines', 'Content-stream removal, you supply targets', BLUE, LIGHTBLUE,
     ['Foxit PDF Services API', 'Apryse Server SDK', 'Nutrient (PSPDFKit)',
      'Adobe PDF Library (via Datalogics)']),
    ('AI-first PII detection engines', 'NER finds the entities, then redacts', ORANGE, LORANGE,
     ['Limina (formerly Private AI)', 'Azure Language in Foundry Tools', 'Cloudmersive DLP API']),
    ('Open-core and self-hosted', 'Runs in your own process, license terms apply', GREEN, LGREEN,
     ['Presidio with PyMuPDF', 'iText pdfSweep']),
]
cw = 0.30; gap = 0.025; x0 = 0.02
for i, (title, sub, c, lc, tools) in enumerate(cols):
    x = x0 + i * (cw + gap)
    box(ax, x, 0.70, cw, 0.12, title, fc=c, ec=c, tc='white', fs=13, bold=True)
    ax.text(x + cw / 2, 0.655, sub, ha='center', va='center', fontsize=10.5, color=T2)
    for j, t in enumerate(tools):
        box(ax, x + 0.015, 0.50 - j * 0.115, cw - 0.03, 0.09, t, fc=lc, ec=c, fs=11.5)
save(fig, 'archetype-map')

# 2. Overlay vs true redaction vs rasterization -----------------------------
fig, ax = canvas(13, 6.6)
ax.text(0.02, 0.94, 'What pdftotext returns after 3 kinds of "redaction"',
        fontsize=16, fontweight='bold', color=T1)
lanes = [
    ('Annotation overlay', RED, LRED,
     ['/Annots: black Square rect', 'drawn on top at display time'],
     ['BT 72 692 TD', '[(Patient: John Smith)] TJ ET', 'BT 72 662 TD',
      '[(SSN: 123-45-6789)] TJ', 'ET'],
     None, 'Patient: John Smith\nSSN: 123-45-6789', 'Fails: the SSN is still in the file'),
    ('True redaction', GREEN, LGREEN,
     ['Glyphs inside the target rect', 'removed, stream rebuilt'],
     ['BT 72 692 TD', '[(Patient: John Smith)] TJ ET', 'BT 72 662 TD',
      '[(SSN: )] TJ', 'ET'],
     3, 'Patient: John Smith\nSSN:', 'Passes: the SSN bytes are gone'),
    ('Page rasterization', BLUE, LIGHTBLUE,
     ['Page re-rendered as one image', 'with the region painted over'],
     ['q 612 0 0 792 0 0 cm', '/Im1 Do', 'Q', '', '(no text operators)'],
     None, '(empty)', 'Passes, but nothing on the page\nis searchable or selectable'),
]
lw = 0.30; lg = 0.025
for i, (title, c, lc, how, stream, hit, out, verdict) in enumerate(lanes):
    x = 0.02 + i * (lw + lg)
    box(ax, x, 0.80, lw, 0.08, title, fc=c, ec=c, tc='white', fs=13, bold=True)
    ax.text(x + lw / 2, 0.745, '\n'.join(how), ha='center', va='center', fontsize=10.5,
            color=T2, linespacing=1.35)
    ax.text(x, 0.665, 'Page /Contents stream', fontsize=10, color=T2, fontweight='bold')
    box(ax, x, 0.39, lw, 0.26, fc='#fafaf8', ec=GRID)
    for k, line in enumerate(stream):
        ax.text(x + 0.012, 0.615 - k * 0.048, line, fontsize=10, family=MONO, color=T1, va='center')
    if i == 0:
        ax.text(x + lw - 0.01, 0.42, 'unchanged, the black box lives in /Annots', ha='right',
                fontsize=9, color=RED, style='italic')
    if hit:
        ax.text(x + lw - 0.01, 0.42, '123-45-6789 removed', ha='right', fontsize=9,
                color=GREEN, style='italic')
    arrow(ax, x + lw / 2, 0.38, x + lw / 2, 0.315)
    ax.text(x, 0.29, '$ pdftotext out.pdf -', fontsize=10, family=MONO, color=T2)
    box(ax, x, 0.13, lw, 0.14, out, fc=lc, ec=c, fs=11, family=MONO)
    ax.text(x + lw / 2, 0.065, verdict, ha='center', va='center', fontsize=10.5, color=c,
            fontweight='bold', linespacing=1.3)
save(fig, 'overlay-vs-stream-removal')

# 3. Foxit async redaction flow --------------------------------------------
fig, ax = canvas(13, 4.4)
ax.text(0.02, 0.91, 'A redaction run on the Foxit PDF Services API',
        fontsize=16, fontweight='bold', color=T1)
ax.text(0.02, 0.835, 'Every call sends the client_id and client_secret headers from the developer console',
        fontsize=11, color=T2)
steps = [
    ('1  Upload', 'POST /documents/upload\nmultipart file=@input.pdf', '200  documentId', PALE),
    ('2  Redact', 'POST /documents/\nsecurity/pdf-redact\n{documentId, config}', '202  taskId\n1 credit', LIGHTBLUE),
    ('3  Poll', 'GET /tasks/{taskId}\nevery 3 s', 'COMPLETED\nresultDocumentId', PALE),
    ('4  Download', 'GET /documents/\n{resultDocumentId}\n/download', '200  application/pdf', PALE),
    ('5  Your code', 'Strip XMP and Info\nmetadata', 'title and author\nsurvive step 2', LORANGE),
]
w = 0.172; g = 0.023; y = 0.30; h = 0.38
for i, (t, call, res, fc) in enumerate(steps):
    x = 0.02 + i * (w + g)
    ec = ORANGE if fc == LORANGE else '#b9b8b2'
    box(ax, x, y, w, h, fc=fc, ec=ec, ls='--' if fc == LORANGE else '-')
    ax.text(x + w / 2, y + h - 0.055, t, ha='center', fontsize=12.5, fontweight='bold', color=T1)
    ax.text(x + w / 2, y + h / 2 - 0.02, call, ha='center', va='center', fontsize=10,
            family=MONO, color=T1, linespacing=1.4)
    ax.text(x + w / 2, y - 0.09, res, ha='center', va='center', fontsize=10.5,
            color=ORANGE if fc == LORANGE else BLUE, fontweight='bold', linespacing=1.3)
    if i < len(steps) - 1:
        arrow(ax, x + w + 0.002, y + h / 2, x + w + g - 0.002, y + h / 2)
ax.text(0.02, 0.05, 'Paths are relative to https://na1.fusion.foxit.com/pdf-services/api. '
        'Status strings are PENDING, IN_PROGRESS, COMPLETED, FAILED.',
        fontsize=10, color=T2)
save(fig, 'foxit-redaction-flow')

# 4. Two-phase pipeline coverage --------------------------------------------
stages = ['Text\nextraction', 'NER / regex\ndetection', 'Offsets to\nPDF rects',
          'Content-stream\nremoval', 'Metadata, form,\nobject cleanup', 'Extraction\ncheck']
rows = [
    ('Foxit PDF Services API', ['Y', 'text search', 'Y', 'Y', 'form fields', '']),
    ('Apryse Server SDK', ['Y', 'regex', 'Y', 'Y', '', '']),
    ('Nutrient (Document Engine + DWS)', ['Y', 'Y', 'Y', 'Y', '', '']),
    ('Adobe PDF Library (Datalogics)', ['Y', 'text search', 'Y', 'Y', '', '']),
    ('Limina, enhanced approach', ['Y', 'Y', 'Y', 'Y', '', '']),
    ('Azure Language Document PII', ['Y', 'Y', 'Y', 'Y', '', '']),
    ('Cloudmersive DLP API', ['Y', 'Y', 'Y', 'r', '', '']),
    ('Presidio (detection)', ['', 'Y', '', '', '', '']),
    ('PyMuPDF (removal)', ['Y', '', '', 'Y', '', '']),
    ('iText pdfSweep', ['Y', 'regex', 'Y', 'Y', '', '']),
]
fig, ax = canvas(13, 6.6)
ax.text(0.02, 0.955, 'The two-phase redaction pipeline, and which boxes each tool fills',
        fontsize=16, fontweight='bold', color=T1)
x0 = 0.27; cw = (0.985 - x0) / 6; top = 0.80; rh = 0.064
ax.text(x0 + cw * 1, top + 0.115, 'Phase 1: detection', ha='center', fontsize=11.5,
        color=ORANGE, fontweight='bold')
ax.text(x0 + cw * 4, top + 0.115, 'Phase 2: removal and verification', ha='center',
        fontsize=11.5, color=BLUE, fontweight='bold')
for i, s in enumerate(stages):
    cx = x0 + cw * i + 0.004
    box(ax, cx, top + 0.005, cw - 0.008, 0.085, s, fc=LORANGE if i < 2 else LIGHTBLUE,
        ec=ORANGE if i < 2 else BLUE, fs=10, bold=True)
    if i < 5:
        arrow(ax, cx + cw - 0.008, top + 0.047, cx + cw, top + 0.047)
for r, (name, cells) in enumerate(rows):
    y = top - (r + 1) * rh
    ax.text(0.02, y + rh / 2 - 0.004, name, va='center', fontsize=11, color=T1)
    for i, c in enumerate(cells):
        cx = x0 + cw * i + 0.004
        if c == 'Y': fc, ec, txt = BLUE, BLUE, ''
        elif c == 'r': fc, ec, txt = PALE, '#9a9993', 'rasterizes'
        elif c: fc, ec, txt = LIGHTBLUE, '#86b6ef', c
        else: fc, ec, txt = 'white', GRID, ''
        box(ax, cx, y + 0.008, cw - 0.008, rh - 0.016, txt, fc=fc, ec=ec, fs=9.5)
ly = 0.05
for fc, ec, lab, xx in [(BLUE, BLUE, 'Handled by the tool', 0.27),
                        (LIGHTBLUE, '#86b6ef', 'Pattern or field level only', 0.45),
                        (PALE, '#9a9993', 'Replaces the page with an image', 0.66),
                        ('white', GRID, 'Your own code', 0.88)]:
    box(ax, xx, ly, 0.022, 0.03, fc=fc, ec=ec)
    ax.text(xx + 0.03, ly + 0.015, lab, va='center', fontsize=10, color=T2)
save(fig, 'two-phase-pipeline')
