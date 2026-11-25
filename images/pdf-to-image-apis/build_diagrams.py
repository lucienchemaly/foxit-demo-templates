"""Builds the 3 mechanism diagrams for the PDF to image APIs comparison.

Run: python3 build_diagrams.py  (writes PNGs next to this file)
Diagram 1 labels come from live PDF Services runs on 2026-11-25 (thirtyfive.pdf,
OAuth token, upload, convert/pdf-to-image, task poll IN_PROGRESS -> COMPLETED,
ZIP download of 35 JPEGs). Diagram 3 is list-price arithmetic from the article's
own price table, not a benchmark.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

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
                fontweight='bold' if bold else 'normal', linespacing=1.45,
                family=family or 'Arial')


def arrow(ax, x1, y1, x2, y2, c=T2, ls='-', rad=0.0, lw=1.4):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=14,
                                connectionstyle=f'arc3,rad={rad}'))


def title(ax, t, sub=None):
    ax.text(0.02, 0.945, t, fontsize=16, fontweight='bold', color=T1, va='center')
    if sub:
        ax.text(0.02, 0.893, sub, fontsize=10.5, color=T2, va='center')


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), dpi=150, facecolor='white')
    plt.close(fig)


# 1. Foxit asynchronous render flow --------------------------------------------
fig, ax = canvas(13, 7.4)
title(ax, 'How a Foxit PDF to Image render runs',
      'Five calls from your backend. Only the processing call uses a credit; '
      'upload, task polling, and download are not billed.')
steps = [
    ('POST\n/oauth/token', 'client_id + client_secret\n(grant_type=client_credentials)',
     'access_token (Bearer)', 'not billed', PALE, EDGE),
    ('POST\n/pdf-services/api/\ndocuments/upload', 'multipart field file\n(report.pdf)',
     '200  documentId', 'not billed', LBLUE, BLUE),
    ('POST\n/pdf-services/api/documents/\nconvert/pdf-to-image', 'documentId, pageRange,\nconfig: {dpi: 150}',
     '202  taskId', '1 credit', LORANGE, ORANGE),
    ('GET\n/pdf-services/api/\ntasks/{taskId}', 'taskId in the path,\nrepeated until done',
     'status, progress,\nresultDocumentId', 'not billed', LBLUE, BLUE),
    ('GET\n/pdf-services/api/documents/\n{resultDocumentId}/download', 'resultDocumentId\nin the path',
     'application/zip\nreport_images.zip', 'not billed', LBLUE, BLUE),
]
n = len(steps); w = 0.176; gap = (0.96 - n * w) / (n - 1); y0 = 0.40; h = 0.36
for i, (call, sends, returns, cost, fc, ec) in enumerate(steps):
    x = 0.02 + i * (w + gap)
    box(ax, x, y0, w, h, '', fc=fc, ec=ec, lw=1.6 if ec == ORANGE else 1.2)
    ax.text(x + w / 2, y0 + h - 0.012, f'Step {i + 1}', ha='center', va='top', fontsize=9.5, color=T2)
    ax.text(x + w / 2, y0 + h - 0.10, call, ha='center', va='center', fontsize=7.9,
            family=MONO, color=T1, linespacing=1.35)
    ax.text(x + w / 2, y0 + 0.165, 'sends', ha='center', fontsize=8.5, color=T2, style='italic')
    ax.text(x + w / 2, y0 + 0.125, sends, ha='center', va='center', fontsize=8.8, color=T1, linespacing=1.3)
    ax.text(x + w / 2, y0 + 0.075, 'returns', ha='center', fontsize=8.5, color=T2, style='italic')
    ax.text(x + w / 2, y0 + 0.035, returns, ha='center', va='center', fontsize=8.8, color=T1,
            linespacing=1.3, fontweight='bold')
    # cost badge
    bc, bfc = (ORANGE, LORANGE) if cost == '1 credit' else (T2, 'white')
    box(ax, x + w / 2 - 0.05, y0 - 0.075, 0.10, 0.05, cost, fc=bfc, ec=bc, tc=bc if cost == '1 credit' else T2,
        fs=9.5, bold=cost == '1 credit')
    if i < n - 1:
        arrow(ax, x + w + 0.004, y0 + h / 2, x + w + gap - 0.004, y0 + h / 2)
# poll loop
sx = 0.02 + 3 * (w + gap)
ax.annotate('', xy=(sx + w * 0.30, y0 + h + 0.005), xytext=(sx + w * 0.70, y0 + h + 0.005),
            arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.4, mutation_scale=13,
                            connectionstyle='arc3,rad=1.6'))
ax.text(sx + w / 2 + 0.11, y0 + h + 0.06, 'PENDING or IN_PROGRESS:\npoll again', ha='left', va='center',
        fontsize=9, color=BLUE, linespacing=1.3)
# outcomes
box(ax, 0.02, 0.07, 0.46, 0.15, '', fc='white', ec=GREEN)
ax.text(0.035, 0.185, 'COMPLETED', fontsize=10.5, fontweight='bold', color=GREEN, family=MONO, va='center')
ax.text(0.035, 0.12, 'progress 100 and a resultDocumentId. Download the ZIP: one JPEG per\n'
        'selected page, named by page number. Live run: 35-page PDF, 35 JPEGs.',
        fontsize=9.5, color=T1, va='center', linespacing=1.4)
box(ax, 0.52, 0.07, 0.46, 0.15, '', fc='white', ec=RED)
ax.text(0.535, 0.185, 'FAILED', fontsize=10.5, fontweight='bold', color=RED, family=MONO, va='center')
ax.text(0.535, 0.12, 'error.code and error.message, for example "The PDF file is protected\n'
        'and requires a valid password to access." Nothing to download.',
        fontsize=9.5, color=T1, va='center', linespacing=1.4)
arrow(ax, sx + w * 0.35, y0 - 0.08, 0.40, 0.225, c=GREEN, rad=0.0)
arrow(ax, sx + w * 0.65, y0 - 0.08, 0.70, 0.225, c=RED, rad=0.0)
save(fig, 'foxit-async-render-flow')


# 2. Multi-page output shapes ----------------------------------------------------
fig, ax = canvas(13, 7.8)
title(ax, 'One PDF, four output shapes',
      'How each API hands back N selected pages, and the viewer each shape suits.')
# source
box(ax, 0.02, 0.36, 0.13, 0.26, '', fc='white', ec=T2)
for k in range(3):
    ax.add_patch(FancyBboxPatch((0.045 + k * 0.012, 0.42 - k * 0.012), 0.06, 0.12,
                                boxstyle='round,pad=0,rounding_size=0.004', fc='white', ec=EDGE, lw=1))
ax.text(0.085, 0.585, 'PDF, N selected\npages', ha='center', va='center', fontsize=10, fontweight='bold',
        linespacing=1.3)
ax.text(0.085, 0.385, '1  2  ...  N', ha='center', fontsize=9, color=T2)
shapes = [
    ('One image per call', 'Nutrient, when one page is selected',
     'Suits: list-view thumbnail of page one', BLUE, LBLUE),
    ('A ZIP of page images', 'Foxit (always, even for one page) · Nutrient (2 to 50 pages)\n'
     'Adobe (ZIP option, required for external storage) · Stirling multiple\n'
     'CloudConvert archive_multiple_files=true · pdfRest via a separate Zip call',
     'Suits: batch storage, unzip once and serve', ORANGE, LORANGE),
    ('One URL or file per page', 'ConvertAPI Files array (Base64 or URLs kept up to 3 hours)\n'
     'CloudConvert export URLs (default) · pdfRest one resource per page\n'
     'PDF.co URLs kept 60 minutes · Adobe list (Adobe-hosted assets)',
     'Suits: lazy-loading viewer, fetch pages on scroll', GREEN, LGREEN),
    ('One combined file', 'Stirling single (pages stacked into one tall image)\n'
     'ConvertAPI multi-page TIFF (MultiPage, on by default)',
     'Suits: simple scrolling preview (tall image), archives (TIFF)', PURPLE, LPURPLE),
]
rows = [0.69, 0.47, 0.25, 0.07]; rh = [0.14, 0.18, 0.18, 0.14]
for (name, apis, suits, c, lc), y, hh in zip(shapes, rows, rh):
    box(ax, 0.25, y, 0.20, hh, name, fc=lc, ec=c, fs=11.5, bold=True)
    box(ax, 0.47, y, 0.51, hh, '', fc='white', ec=EDGE)
    ax.text(0.485, y + hh - 0.028, apis, fontsize=9.3, color=T1, va='top', linespacing=1.5)
    ax.text(0.485, y + 0.022, suits, fontsize=9.3, color=c if c != GREEN else '#127a55',
            va='center', fontweight='bold')
    arrow(ax, 0.15, 0.49, 0.25, y + hh / 2, c=c)
save(fig, 'multipage-output-shapes')


# 3. Billing unit cost curve -----------------------------------------------------
pages = list(range(1, 101))
FOXIT = 4500 / 15000            # Business, billed annually: $0.30 per request
PDFREST = 99.99 / 5000          # Pro: about $0.020 per call
NUTRIENT_OP = 0.0375            # per operation, up to 50 selected pages
PDFCO_PAGE = 15 * 99.99 / 159850  # Business 2: 15 credits per PNG page, about $0.0094
series = [
    ('Foxit Business (1 credit per request)', [FOXIT] * 100, ORANGE, '-'),
    ('Nutrient ($0.0375 per operation, up to 50 pages)',
     [NUTRIENT_OP * ((p - 1) // 50 + 1) for p in pages], BLUE, '-'),
    ('pdfRest Pro (1 call per request)', [PDFREST] * 100, GREEN, '-'),
    ('PDF.co Business 2 (15 credits per PNG page)', [PDFCO_PAGE * p for p in pages], PURPLE, '--'),
]
fig = plt.figure(figsize=(13, 7.4), dpi=150, facecolor='white')
fig.text(0.02, 0.955, 'Per-request billing stays flat, per-page billing grows with length',
         fontsize=16, fontweight='bold', color=T1, va='center')
fig.text(0.02, 0.905, 'List-price cost to render every page of one document, by page count. '
         'List-price arithmetic from the plans named, not a benchmark. Prices checked November 2026.',
         fontsize=10.5, color=T2, va='center')
ax = fig.add_axes([0.08, 0.11, 0.60, 0.74])
for label, ys, c, ls in series:
    ax.plot(pages, ys, color=c, lw=2, ls=ls, solid_capstyle='round',
            drawstyle='steps-post' if c == BLUE else 'default')
ax.set_yscale('log')
ax.set_xlim(1, 100); ax.set_ylim(0.005, 1.2)
ticks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
ax.set_yticks(ticks); ax.set_yticklabels([f'${t:.2f}' for t in ticks])
ax.minorticks_off()
ax.set_xticks([1, 10, 25, 50, 75, 100])
ax.set_xlabel('Pages rendered from one document', fontsize=10.5, color=T2)
ax.set_ylabel('List-price cost per document (USD, log scale)', fontsize=10.5, color=T2)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
for s in ('left', 'bottom'):
    ax.spines[s].set_color(EDGE)
ax.tick_params(colors=T2, labelsize=9.5)
ax.grid(axis='y', color='#e8e7e3', lw=0.8)
# direct labels at the right edge
ends = {'Foxit Business': (FOXIT, ORANGE), 'Nutrient': (NUTRIENT_OP * 2, BLUE),
        'pdfRest Pro': (PDFREST, GREEN), 'PDF.co Business 2': (PDFCO_PAGE * 100, PURPLE)}
for name, (yv, c) in ends.items():
    ax.text(101.5, yv, name, fontsize=9.5, color=T1, va='center', fontweight='bold', clip_on=False)
    ax.plot([100], [yv], 'o', color=c, ms=5, clip_on=False)
# markers for the two jobs
for x, lab, ty in ((1, 'Thumbnail (page one only)', 1.05), (10, '10-page preview', 0.70)):
    ax.axvline(x, color=EDGE, lw=1, ls=':')
    ax.text(x + 0.8, ty, lab, fontsize=9, color=T2, va='top')
# crossovers with PDF.co
for other, name in ((PDFREST, 'pdfRest'), (NUTRIENT_OP, 'Nutrient'), (FOXIT, 'Foxit')):
    xc = other / PDFCO_PAGE
    ax.plot([xc], [other], 'o', mfc='white', mec=T1, ms=6, zorder=5)
ax.annotate('PDF.co passes pdfRest\nat about 2 pages', xy=(PDFREST / PDFCO_PAGE, PDFREST),
            xytext=(14, 0.0072), fontsize=8.8, color=T1, arrowprops=dict(arrowstyle='-', color=T2, lw=0.8))
ax.annotate('passes Nutrient\nat 4 pages', xy=(NUTRIENT_OP / PDFCO_PAGE, NUTRIENT_OP),
            xytext=(14, 0.026), fontsize=8.8, color=T1, arrowprops=dict(arrowstyle='-', color=T2, lw=0.8))
ax.annotate('passes Foxit at\nabout 32 pages', xy=(FOXIT / PDFCO_PAGE, FOXIT),
            xytext=(42, 0.13), fontsize=8.8, color=T1, arrowprops=dict(arrowstyle='-', color=T2, lw=0.8))
ax.annotate('a 51st page starts\na 2nd Nutrient operation', xy=(51, NUTRIENT_OP * 2),
            xytext=(58, 0.03), fontsize=8.8, color=T1, arrowprops=dict(arrowstyle='-', color=T2, lw=0.8))
# legend panel
lx = 0.785
fig.text(lx, 0.83, 'Effective unit price', fontsize=11, fontweight='bold', color=T1)
rows3 = [
    (ORANGE, '-', 'Foxit Business', '$4,500/yr for 15,000 credits\n= $0.30 per request, any length'),
    (BLUE, '-', 'Nutrient', '$0.0375 per operation\n(up to 50 selected pages)'),
    (GREEN, '-', 'pdfRest Pro', '$99.99/mo for 5,000 calls\n= about $0.02 per call'),
    (PURPLE, '--', 'PDF.co Business 2', '$99.99/mo for 159,850 credits;\n15 per PNG page, about $0.0094'),
]
for i, (c, ls, nm, desc) in enumerate(rows3):
    yy = 0.76 - i * 0.135
    fig.add_artist(plt.Line2D([lx, lx + 0.03], [yy, yy], color=c, lw=2.2, ls=ls))
    fig.text(lx + 0.038, yy, nm, fontsize=10, fontweight='bold', color=T1, va='center')
    fig.text(lx + 0.038, yy - 0.05, desc, fontsize=8.8, color=T2, va='center', linespacing=1.35)
fig.text(lx, 0.14, 'Assumes all paid units are used.\nUnused credits, overage, retries,\n'
         'and annual vs monthly billing\nchange the real cost.', fontsize=8.8, color=T2, va='center',
         linespacing=1.4)
fig.savefig(os.path.join(OUT, 'billing-unit-cost-curve.png'), dpi=150, facecolor='white')
plt.close(fig)
