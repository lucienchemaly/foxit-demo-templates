"""Builds the 4 mechanism diagrams for the PDF compression APIs comparison.

Run: python3 build_diagrams.py  (writes PNGs next to this file)
The Foxit call sequence in diagram 1 comes from a live PDF Services run on 2026-11-19
(MEDIUM, a-midsummer-nights-dream.pdf, 572,679 -> 535,533 bytes).
Diagram 2 uses a self-signed test PDF and a local qpdf full rewrite, validated with pyHanko
(intact True before, intact False after). Files and log: foxit/november/article9/_verify/sigtest,
signature_rewrite_2026-11-19.log (53,547 -> 48,312 bytes).
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams['font.family'] = 'Arial'
OUT = os.path.dirname(os.path.abspath(__file__))
T1 = '#0b0b0b'; T2 = '#52514e'; PALE = '#f0efec'
BLUE = '#2a78d6'; LIGHTBLUE = '#cde2fb'; ORANGE = '#eb6834'; LORANGE = '#fde0d3'
GREEN = '#1baf7a'; LGREEN = '#d3f1e5'; RED = '#c8372d'; LRED = '#f8d9d6'
PURPLE = '#7a5af5'; LPURPLE = '#e6e0fd'
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


def arrow(ax, x1, y1, x2, y2, c=T2, ls='-', rad=0.0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=1.4, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=14,
                                connectionstyle=f'arc3,rad={rad}'))


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=150, facecolor='white')
    plt.close(fig)


# 1. Foxit async compression flow ------------------------------------------
fig, ax = canvas(13, 7.4)
ax.text(0.02, 0.945, 'The 4 PDF Services calls behind one compression job',
        fontsize=16, fontweight='bold', color=T1)
ax.text(0.02, 0.905, 'All calls go to https://na1.fusion.foxit.com/pdf-services/api with the '
        'client_id and client_secret headers. IDs are from a live run.',
        fontsize=10.5, color=T2)
steps = [
    ('1', 'POST documents/upload', 'multipart field: file',
     '{"documentId":"6afe39ac4109060c740dc75a"}', BLUE, LIGHTBLUE),
    ('2', 'POST documents/modify/pdf-compress', '{documentId, compressionLevel: "MEDIUM"}',
     'HTTP 202  {"taskId":"6afe39ad2752dc0c4fd36079"}', ORANGE, LORANGE),
    ('3', 'GET tasks/{taskId}', 'repeat every 2 s while PENDING or IN_PROGRESS',
     '"status":"COMPLETED","resultDocumentId":"6afe39ad00610d26be7e2a9e"', PURPLE, LPURPLE),
    ('4', 'GET documents/{resultDocumentId}/download', 'write the bytes to compressed.pdf',
     'HTTP 200 application/pdf, 535,533 bytes', GREEN, LGREEN),
]
ys = [0.72, 0.53, 0.34, 0.15]
for (n, call, req, resp, c, lc), y in zip(steps, ys):
    ax.add_patch(plt.Circle((0.045, y + 0.06), 0.022, color=c))
    ax.text(0.045, y + 0.06, n, ha='center', va='center', color='white', fontsize=13,
            fontweight='bold')
    box(ax, 0.08, y, 0.36, 0.12, '', fc=lc, ec=c)
    ax.text(0.095, y + 0.08, call, fontsize=12, fontweight='bold', color=T1, family=MONO,
            va='center')
    ax.text(0.095, y + 0.035, req, fontsize=10, color=T2, family=MONO, va='center')
    arrow(ax, 0.445, y + 0.06, 0.505, y + 0.06, c=c)
    box(ax, 0.51, y + 0.015, 0.47, 0.09, resp, fc='white', ec=c, fs=9.5, family=MONO)
for y1, y2 in zip(ys[:-1], ys[1:]):
    arrow(ax, 0.26, y1, 0.26, y2 + 0.12, c=T2)
ax.text(0.51, 0.31, 'Each poll is free. A FAILED task returns an "error" object with a code and message.',
        fontsize=9.5, color=RED)
# optional linearize branch
box(ax, 0.51, 0.03, 0.47, 0.075,
    'Optional: send resultDocumentId to POST documents/optimize/pdf-linearize,\n'
    'then poll and download the same way (1 more credit)',
    fc=PALE, ec='#b9b8b2', fs=9.5, ls='--')
save(fig, 'foxit-async-flow')

# 2. Signature byte range ----------------------------------------------------
fig, ax = canvas(13, 6.6)
ax.text(0.02, 0.94, 'Why compressing a signed PDF breaks its signature',
        fontsize=16, fontweight='bold', color=T1)


def filebar(ax, y, segs, label):
    ax.text(0.02, y + 0.045, label, fontsize=11.5, fontweight='bold', color=T1, va='center')
    for x, w, txt, fc, ec in segs:
        ax.add_patch(Rectangle((x, y), w, 0.09, fc=fc, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + 0.045, txt, ha='center', va='center', fontsize=9.5,
                color=T1, linespacing=1.3)


# signed original
filebar(ax, 0.72, [
    (0.22, 0.30, 'Hashed bytes 0 to 48,700\npages, fonts, content streams', LGREEN, GREEN),
    (0.52, 0.13, 'Signature hole\n/Contents <PKCS#7>', '#ffffff', T2),
    (0.65, 0.33, 'Hashed bytes 53,016 to 53,547\ntrailer, final xref', LGREEN, GREEN),
], 'Signed (53,547 bytes)')
ax.text(0.22, 0.675, '/ByteRange [0 48700 53016 531] stores these offsets, and the signature '
        'is a hash over exactly those bytes', fontsize=10, color=T2, family=MONO)
arrow(ax, 0.60, 0.645, 0.60, 0.565, c=ORANGE)
ax.text(0.615, 0.605, 'a full rewrite recompresses streams, renumbers objects, rebuilds the xref',
        fontsize=10, color=ORANGE, va='center')
filebar(ax, 0.45, [
    (0.22, 0.25, 'Recompressed streams\n(smaller, new offsets)', LORANGE, ORANGE),
    (0.47, 0.13, 'Old signature\n/Contents <PKCS#7>', '#ffffff', T2),
    (0.60, 0.25, 'Rebuilt xref and trailer\nat new offsets', LORANGE, ORANGE),
], 'Rewritten (48,312 bytes)')
box(ax, 0.22, 0.29, 0.63, 0.1,
    '/ByteRange is still [0 48700 53016 531], but the file is now 48,312 bytes long.\n'
    'The signed bytes are gone, so pyHanko reports the signature as no longer intact.',
    fc=LRED, ec=RED, fs=10.5)
# right order
ax.text(0.02, 0.17, 'Safe order', fontsize=11.5, fontweight='bold', color=T1, va='center')
for i, (t, c, lc) in enumerate([('Compress', BLUE, LIGHTBLUE), ('Sign', GREEN, LGREEN),
                                 ('Store the signed file as is', PURPLE, LPURPLE)]):
    x = 0.22 + i * 0.25
    box(ax, x, 0.12, 0.2, 0.1, t, fc=lc, ec=c, fs=11.5, bold=True)
    if i:
        arrow(ax, x - 0.05, 0.17, x, 0.17)
ax.text(0.22, 0.05, 'Keep the signed original. Any later rewrite of the file needs a new signature.',
        fontsize=10, color=T2)
save(fig, 'signature-byte-range')

# 3. MRC layers --------------------------------------------------------------
fig, ax = canvas(13, 6.2)
ax.text(0.02, 0.94, 'How Mixed Raster Content (MRC) splits a scanned page',
        fontsize=16, fontweight='bold', color=T1)
# scanned page
box(ax, 0.03, 0.18, 0.18, 0.62, '', fc='#fbfaf7', ec=T2)
ax.text(0.12, 0.76, 'Scanned page', ha='center', fontsize=11, fontweight='bold', color=T1)
ax.add_patch(Rectangle((0.05, 0.5), 0.14, 0.18, fc='#9ab7d3', ec='none'))
ax.text(0.12, 0.59, 'photo', ha='center', va='center', fontsize=9.5, color='white')
for k in range(6):
    ax.add_patch(Rectangle((0.05, 0.43 - k * 0.04), 0.14 if k % 3 else 0.09, 0.012,
                           fc=T1 if k != 1 else RED, ec='none'))
ax.text(0.12, 0.2, 'one raster image', ha='center', fontsize=9, color=T2)
layers = [
    ('Mask layer', 'text outlines and line art,\n1 bit per pixel', 'JBIG2', T1, '#e7e6e2'),
    ('Foreground layer', 'the colors that fill the mask\n(e.g. red or blue text)', 'color codec, low resolution', RED, LRED),
    ('Background layer', 'photos, shading,\npaper texture', 'JPEG / JPEG2000', BLUE, LIGHTBLUE),
]
for i, (name, what, codec, c, lc) in enumerate(layers):
    y = 0.62 - i * 0.22
    arrow(ax, 0.215, 0.49, 0.30, y + 0.075, c=T2)
    box(ax, 0.30, y, 0.25, 0.15, '', fc=lc, ec=c)
    ax.text(0.315, y + 0.11, name, fontsize=12, fontweight='bold', color=T1, va='center')
    ax.text(0.315, y + 0.05, what, fontsize=9.5, color=T2, va='center', linespacing=1.3)
    arrow(ax, 0.555, y + 0.075, 0.60, y + 0.075, c=c)
    box(ax, 0.60, y + 0.025, 0.17, 0.1, codec, fc='white', ec=c, fs=10.5, bold=True)
    arrow(ax, 0.775, y + 0.075, 0.83, 0.49, c=T2)
box(ax, 0.83, 0.36, 0.15, 0.26, 'Viewer recombines\nthe 3 layers\non render', fc=LGREEN,
    ec=GREEN, fs=11)
ax.text(0.30, 0.08, 'Each layer gets the codec suited to it, so text stays sharp while the '
        'photo layer is compressed hard.', fontsize=10.5, color=T2)
save(fig, 'mrc-layers')

# 4. Deployment topology -----------------------------------------------------
fig, ax = canvas(13, 6.4)
ax.text(0.02, 0.94, 'Where the compression engine runs relative to your data boundary',
        fontsize=16, fontweight='bold', color=T1)
# boundary
ax.add_patch(FancyBboxPatch((0.36, 0.08), 0.62, 0.76,
                            boxstyle='round,pad=0,rounding_size=0.015', fc='#f7fbf9',
                            ec=GREEN, lw=2, ls='--'))
ax.text(0.375, 0.805, 'Your network and infrastructure', fontsize=11.5, fontweight='bold',
        color=GREEN)
cols = [
    ('Multi-tenant SaaS REST', 'the document leaves your network', ORANGE, LORANGE, 0.03,
     ['Foxit PDF Services API', 'Adobe PDF Services API', 'Nutrient DWS Processor API',
      'iLovePDF API', 'ConvertAPI', 'PDF.co', 'pdfRest (cloud)']),
    ('In-process SDK', 'a library inside your app', BLUE, LIGHTBLUE, 0.39,
     ['Apryse SDK Optimizer', 'Foxit PDF SDK + Optimizer']),
    ('Self-hosted container', 'a service you deploy and patch', PURPLE, LPURPLE, 0.69,
     ['Stirling-PDF (Docker)', 'pdfRest Container / AWS', 'Nutrient Document Engine']),
]
for title, sub, c, lc, x, tools in cols:
    w = 0.28
    box(ax, x, 0.66, w, 0.1, title, fc=c, ec=c, tc='white', fs=12.5, bold=True)
    ax.text(x + w / 2, 0.625, sub, ha='center', va='center', fontsize=10, color=T2)
    for j, t in enumerate(tools):
        box(ax, x + 0.015, 0.53 - j * 0.068, w - 0.03, 0.055, t, fc=lc, ec=c, fs=10.5)
# app box and arrows
box(ax, 0.39, 0.12, 0.28, 0.08, 'Your application', fc='white', ec=T2, fs=11.5, bold=True)
arrow(ax, 0.39, 0.16, 0.31, 0.16, c=ORANGE)
ax.text(0.335, 0.125, 'HTTPS', ha='center', fontsize=9.5, color=ORANGE)
arrow(ax, 0.53, 0.20, 0.53, 0.455, c=BLUE)
arrow(ax, 0.67, 0.16, 0.83, 0.385, c=PURPLE)
save(fig, 'deployment-topology')
print('ok')
