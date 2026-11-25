"""Builds the 2 mechanism diagrams for the PDF watermark APIs comparison.

Run: python3 build_diagrams.py  (writes PNGs next to this file)
Diagram 1 IDs come from a live PDF Services watermark run on 2026-11-25 (getdaypal sandbox,
contract_standard_test.pdf, TEXT "DRAFT", pageRange "odd", onTopOfPage false).
Log: foxit/november/article13/_verify/watermark_run_2026-11-25.log
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.family'] = 'Arial'
OUT = os.path.dirname(os.path.abspath(__file__))
T1 = '#0b0b0b'; T2 = '#52514e'; PALE = '#f0efec'
BLUE = '#2a78d6'; LIGHTBLUE = '#cde2fb'; ORANGE = '#eb6834'; LORANGE = '#fde0d3'
GREEN = '#1baf7a'; LGREEN = '#d3f1e5'; RED = '#c8372d'; LRED = '#f8d9d6'
PURPLE = '#7a5af5'; LPURPLE = '#e6e0fd'; GREY = '#b9b8b2'
MONO = 'Menlo'


def canvas(w, h):
    fig = plt.figure(figsize=(w, h), dpi=150, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def box(ax, x, y, w, h, text='', fc=PALE, ec=GREY, tc=T1, fs=11, bold=False, family=None, ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.01',
                                fc=fc, ec=ec, lw=1.2, ls=ls))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, color=tc,
                fontweight='bold' if bold else 'normal', linespacing=1.4, family=family or 'Arial')


def arrow(ax, x1, y1, x2, y2, c=T2, ls='-'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=1.4, ls=ls, shrinkA=0, shrinkB=0,
                                mutation_scale=14))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=150, facecolor='white')
    plt.close(fig)


def badge(ax, x, y, text, c):
    ax.text(x, y, text, ha='center', va='center', fontsize=9.5, fontweight='bold', color='white',
            bbox=dict(boxstyle='round,pad=0.35', fc=c, ec=c))


# 1. Foxit async watermark flow -------------------------------------------------
fig, ax = canvas(13, 8.2)
ax.text(0.02, 0.955, 'The PDF Services calls behind one watermark job',
        fontsize=16, fontweight='bold', color=T1)
ax.text(0.02, 0.918, 'Every call goes to https://na1.fusion.foxit.com/pdf-services/api with the client_id '
        'and client_secret headers. IDs are from a live run.', fontsize=10.5, color=T2)
steps = [
    ('1', 'POST documents/upload', 'multipart field: file (the PDF, and a logo for IMAGE)',
     '{"documentId":"6b075596b5aa331fce5b6a13"}', BLUE, LIGHTBLUE, ('free', GREEN)),
    ('2', 'POST documents/enhance/pdf-watermark', '{documentId, pageRange:"odd", config:{type:"TEXT", ...}}',
     'HTTP 202  {"taskId":"6b075597255cb30668d25f59"}', ORANGE, LORANGE, ('1 credit', ORANGE)),
    ('3', 'GET tasks/{taskId}', 'repeat every 2 s while PENDING or IN_PROGRESS',
     '"status":"COMPLETED","resultDocumentId":"6b075598b387c31b4637625e"', PURPLE, LPURPLE, ('free', GREEN)),
    ('4', 'GET documents/{resultDocumentId}/download', 'write the bytes to watermarked.pdf',
     'HTTP 200 application/pdf, 9,441 bytes', GREEN, LGREEN, ('free', GREEN)),
]
ys = [0.74, 0.56, 0.38, 0.20]
for (n, call, req, resp, c, lc, (cost, cc)), y in zip(steps, ys):
    ax.add_patch(plt.Circle((0.04, y + 0.06), 0.02, color=c))
    ax.text(0.04, y + 0.06, n, ha='center', va='center', color='white', fontsize=13, fontweight='bold')
    box(ax, 0.07, y, 0.40, 0.12, '', fc=lc, ec=c)
    ax.text(0.083, y + 0.08, call, fontsize=11.5, fontweight='bold', color=T1, family=MONO, va='center')
    ax.text(0.083, y + 0.035, req, fontsize=8.8, color=T2, family=MONO, va='center')
    badge(ax, 0.435, y + 0.095, cost, cc)
    arrow(ax, 0.475, y + 0.06, 0.515, y + 0.06, c=c)
    box(ax, 0.52, y + 0.015, 0.46, 0.09, resp, fc='white', ec=c, fs=9.2, family=MONO)
for y1, y2 in zip(ys[:-1], ys[1:]):
    arrow(ax, 0.27, y1, 0.27, y2 + 0.12, c=T2)
# chain branch
box(ax, 0.07, 0.035, 0.91, 0.12, '', fc=PALE, ec=GREY, ls='--')
ax.text(0.083, 0.125, 'Optional: chain resultDocumentId instead of downloading', fontsize=11,
        fontweight='bold', color=T1, va='center')
ax.text(0.083, 0.08, 'POST documents/modify/pdf-flatten', fontsize=10, family=MONO, color=T1, va='center')
badge(ax, 0.40, 0.08, '1 credit', ORANGE)
arrow(ax, 0.44, 0.08, 0.49, 0.08)
ax.text(0.50, 0.08, 'POST documents/security/pdf-protect', fontsize=10, family=MONO, color=T1, va='center')
badge(ax, 0.83, 0.08, '1 credit', ORANGE)
ax.text(0.083, 0.048, 'Each step returns a taskId you poll and a new resultDocumentId, the same way as steps 2 to 4.',
        fontsize=9.5, color=T2, va='center')
save(fig, 'foxit-async-watermark-flow')

# 2. Layers and removability -----------------------------------------------------
fig, ax = canvas(13, 7.4)
ax.text(0.02, 0.955, 'Where a watermark can live in a PDF, and what it takes to remove it',
        fontsize=16, fontweight='bold', color=T1)
ax.text(0.02, 0.918, 'Annotations are the easiest form to remove and rasterized pages the hardest. Most vendors do not publish '
        'whether an above or below mark is stored as page content or as an annotation.', fontsize=10.5, color=T2)
cols = [
    ('Annotation layer', 'Sits on top of the page as\nan annotation object',
     'Delete it with the annotation\ntools in any PDF editor',
     ['Foxit asAnnotation: true'], BLUE, LIGHTBLUE),
    ('Above page content', 'Drawn over text and images;\ncan hide what is under it',
     'Remove with watermark or\ncontent-editing tools',
     ['Foxit onTopOfPage: true', 'ConvertAPI Style: stamp', 'Adobe appearOnForeground: true',
      'iLoveAPI, CloudConvert layer above', 'Stirling PDF (always above)'], PURPLE, LPURPLE),
    ('Below page content', 'Drawn behind the content; opaque\nimages and scans can hide it',
     'Remove with watermark or\ncontent-editing tools',
     ['Foxit onTopOfPage: false', 'ConvertAPI Style: watermark', 'pdfRest behind_page',
      'GroupDocs IsBackground', 'Adobe appearOnForeground: false', 'iLoveAPI, CloudConvert layer below'],
     ORANGE, LORANGE),
    ('Flattened into content', 'An annotation merged into\nthe page content stream',
     'No longer an annotation; needs\ncontent editing to remove',
     ['Foxit asAnnotation, then pdf-flatten', 'Nutrient Build: watermark, then flatten'], GREEN, LGREEN),
    ('Rasterized page image', 'The whole page, mark included,\nbecomes pixels',
     'Needs image editing; page text\nis not selectable or searchable\nwithout OCR',
     ['Stirling PDF convertPDFToImage', 'GroupDocs Rasterize (1 to 600 DPI)', 'pdfRest rasterize tool (separate call)'],
     RED, LRED),
]
x0, w, gap = 0.02, 0.18, 0.015
for i, (title, what, remove, ctrls, c, lc) in enumerate(cols):
    x = x0 + i * (w + gap)
    box(ax, x, 0.77, w, 0.08, title, fc=c, ec=c, tc='white', fs=12, bold=True)
    box(ax, x, 0.62, w, 0.13, what, fc=lc, ec=c, fs=9.8)
    box(ax, x, 0.47, w, 0.13, remove, fc='white', ec=c, fs=9.8)
    box(ax, x, 0.15, w, 0.30, '', fc=PALE, ec=GREY)
    ax.text(x + 0.01, 0.425, 'Vendor controls', fontsize=9.5, fontweight='bold', color=T2, va='center')
    for j, ctl in enumerate(ctrls):
        ax.text(x + 0.01, 0.38 - j * 0.04, ctl, fontsize=8.6, color=T1, va='center')
ax.text(0.005, 0.685, 'What', rotation=90, fontsize=9, color=T2, va='center')
ax.text(0.005, 0.535, 'Removal', rotation=90, fontsize=9, color=T2, va='center')
arrow(ax, 0.03, 0.075, 0.97, 0.075, c=T1)
ax.text(0.03, 0.045, 'easier to remove', fontsize=10, color=T2)
ax.text(0.97, 0.045, 'harder to remove, less accessible', fontsize=10, color=T2, ha='right')
ax.text(0.5, 0.02, 'Protect (owner password and permissions) can be added to any of these; conforming readers are '
        'expected to honor it, but PDF encryption itself does not enforce it.', fontsize=9.5, color=T2, ha='center')
save(fig, 'watermark-layer-and-removability')
