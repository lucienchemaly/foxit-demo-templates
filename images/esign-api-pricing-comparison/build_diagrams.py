"""Builds the five diagrams for the eSignature API pricing comparison article.

Every figure is taken from the article's own verified tables (prices checked against
vendor pages; Foxit quota error from a live call on 2026-11-04). Run:
    python3 build_diagrams.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "Arial"

INK = "#1F2430"
MUTED = "#6B7280"
LINE = "#D1D5DB"
PANEL = "#F3F4F6"
GRAY = "#9CA3AF"
ORANGE = "#FF6A00"
ORANGE_SOFT = "#FFE3CC"
BLUE = "#3B5B92"
BLUE_SOFT = "#DCE5F3"

APIS = ["DocuSign", "Dropbox Sign", "Adobe Acrobat Sign", "PandaDoc", "Foxit eSign API"]


def box(ax, x, y, w, h, fc, ec=None, lw=1.2, r=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec or fc, lw=lw))


def finish(fig, name):
    fig.savefig(name, dpi=100, facecolor="white")
    plt.close(fig)
    print("wrote", name)


# D01: billing moment timeline
def d01():
    fig = plt.figure(figsize=(16, 7.6))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 7.6); ax.axis("off")
    ax.text(0.5, 7.05, "Every API bills before anyone signs", fontsize=24, weight="bold", color=INK)
    ax.text(0.5, 6.6, "The moment each vendor counts a unit against your allowance", fontsize=14, color=MUTED)
    stages = ["Created", "Sent", "Viewed", "Signed", "Completed"]
    xs = [5.0, 7.4, 9.8, 12.2, 14.6]
    box(ax, 4.2, 0.55, 4.4, 5.55, ORANGE_SOFT, r=0.08)
    ax.text(6.4, 0.75, "Billing happens in this window", ha="center", fontsize=12, color=ORANGE, weight="bold")
    for x, s in zip(xs, stages):
        ax.text(x, 5.75, s, ha="center", fontsize=14, weight="bold", color=INK)
        ax.plot([x, x], [1.1, 5.5], color=LINE, lw=1, ls=(0, (3, 3)), zorder=0)
    rows = [
        ("DocuSign", "Sent", "Envelope counts when sent, signed or not"),
        ("Dropbox Sign", "Sent", "Signature request counts when sent; drafts count at Continue or Request Signature"),
        ("Adobe Acrobat Sign", "Sent", "Transaction counts when sent; Send in Bulk counts once per recipient"),
        ("PandaDoc", "Created", "Document counts when created"),
        ("Foxit eSign API", "Created", "Envelope uses 5 credits when created, through the API or the UI"),
    ]
    for i, (name, stage, note) in enumerate(rows):
        y = 4.95 - i * 0.85
        col = ORANGE if name.startswith("Foxit") else BLUE
        ax.text(0.5, y, name, fontsize=14, weight="bold", color=INK, va="center")
        ax.plot([xs[0], xs[-1]], [y, y], color=LINE, lw=2, zorder=1)
        bx = xs[stages.index(stage)]
        ax.scatter([bx], [y], s=420, color=col, zorder=3)
        ax.text(bx, y, "$", ha="center", va="center", color="white", fontsize=13, weight="bold", zorder=4)
        ax.text(bx + 0.35, y - 0.33, note, fontsize=10.5, color=MUTED, va="center", bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.85))
    ax.text(0.5, 0.2, "Unsigned, declined, and abandoned requests still count. Vendor terms checked 27 Oct 2026.",
            fontsize=11, color=MUTED)
    finish(fig, "diagram-billing-moment.png")


# D02: embedded signing plan gate
def d02():
    fig = plt.figure(figsize=(16, 7.8))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 7.8); ax.axis("off")
    ax.text(0.5, 7.25, "Which plan unlocks embedded signing", fontsize=24, weight="bold", color=INK)
    ax.text(0.5, 6.8, "Published plans from lowest to highest, yearly list price in USD", fontsize=14, color=MUTED)
    ladders = [
        ("DocuSign", [("Starter", "$600", 0), ("Intermediate", "$3,600", 0), ("Advanced", "$5,760", 0), ("Enhanced", "Quote, 5 users", 1)]),
        ("Dropbox Sign", [("Essentials 50", "$900", 0), ("Standard 100", "$3,000", 1), ("Standard 250", "$5,400", 1), ("Premium", "Quote", 1)]),
        ("Adobe Acrobat Sign", [("Developer Edition", "Free, test only", 0), ("Sales-led license", "Quote", 1), ("Embed partner", "Quote", 1)]),
        ("PandaDoc", [("Free", "$0", 2), ("API Developer", "$480", 2), ("Enterprise", "Custom", 2)]),
        ("Foxit eSign API", [("Developer", "Free, 30-day trial", 1), ("Startup", "$1,750", 1), ("Business", "$4,500", 1), ("Volume", "Quote", 1)]),
    ]
    for i, (name, tiers) in enumerate(ladders):
        y = 5.75 - i * 1.12
        ax.text(0.5, y + 0.38, name, fontsize=14, weight="bold", color=INK, va="center")
        for j, (tier, price, state) in enumerate(tiers):
            x = 3.7 + j * 3.05
            if state == 1:
                fc, ec, tc = (ORANGE_SOFT, ORANGE, INK) if name.startswith("Foxit") else (BLUE_SOFT, BLUE, INK)
            elif state == 2:
                fc, ec, tc = "white", GRAY, MUTED
            else:
                fc, ec, tc = PANEL, PANEL, MUTED
            box(ax, x, y, 2.8, 0.78, fc, ec, lw=1.6 if state else 0, r=0.06)
            if state == 2:
                ax.add_patch(FancyBboxPatch((x, y), 2.8, 0.78, boxstyle="round,pad=0,rounding_size=0.06",
                                            fc="none", ec=GRAY, lw=1.2, ls=(0, (4, 3))))
            ax.text(x + 0.15, y + 0.52, tier, fontsize=12, weight="bold", color=tc, va="center")
            ax.text(x + 0.15, y + 0.22, price, fontsize=11.5, color=tc, va="center")
            if state == 1:
                ax.text(x + 2.62, y + 0.52, "✓", fontsize=15, color=ORANGE if name.startswith("Foxit") else BLUE,
                        ha="right", va="center", weight="bold", family="Arial Unicode MS")
    ly = 0.3
    box(ax, 0.5, ly, 0.45, 0.32, BLUE_SOFT, BLUE, lw=1.6, r=0.04); ax.text(1.1, ly + 0.16, "Embedded signing included", fontsize=11, va="center", color=INK)
    box(ax, 4.6, ly, 0.45, 0.32, PANEL, r=0.04); ax.text(5.2, ly + 0.16, "Embedded signing not included", fontsize=11, va="center", color=INK)
    ax.add_patch(FancyBboxPatch((7.7, ly), 0.45, 0.32, boxstyle="round,pad=0,rounding_size=0.04", fc="white", ec=GRAY, lw=1.2, ls=(0, (4, 3))))
    ax.text(8.3, ly + 0.16, "No plan gate published (PandaDoc requires you to be a client)", fontsize=11, va="center", color=INK)
    finish(fig, "diagram-embedded-signing-gate.png")


# D03: cost by volume, quote-only cells shown as markers
def d03():
    rows = [
        ("DocuSign, hosted", [600, 3600, "Not published", "Quote"]),
        ("DocuSign, embedded", ["Quote", "Quote", "Quote", "Quote"]),
        ("Dropbox Sign, hosted", [900, 1500, 3300, "Contact sales"]),
        ("Dropbox Sign, embedded", [3000, 3000, 5400, "Contact sales"]),
        ("Adobe Acrobat Sign", ["Quote", "Quote", "Quote", "Quote"]),
        ("PandaDoc", [480, ("est", 3360), ("est", 10560), "Confirm price"]),
        ("Foxit eSign API", [1750, 4500, 4500, "Quote"]),
    ]
    vols = ["40 a month", "100 a month", "250 a month", "2,000 a month"]
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
    ax.text(0.5, 8.45, "Yearly cost at 4 monthly volumes", fontsize=24, weight="bold", color=INK)
    ax.text(0.5, 8.0, "List prices in USD with annual billing where offered. Bars share one scale.", fontsize=14, color=MUTED)
    x0s = [3.9, 7.0, 10.1, 13.2]; pw = 2.75; vmax = 12500
    for c, v in enumerate(vols):
        ax.text(x0s[c] + pw / 2, 7.35, v, ha="center", fontsize=14, weight="bold", color=INK)
    for i, (name, vals) in enumerate(rows):
        y = 6.55 - i * 0.88
        foxit = name.startswith("Foxit")
        ax.text(0.5, y, name, fontsize=13, weight="bold" if foxit else "normal", color=INK, va="center")
        for c, val in enumerate(vals):
            x0 = x0s[c]
            ax.plot([x0, x0 + pw], [y - 0.36, y - 0.36], color=LINE, lw=0.8)
            if isinstance(val, (int, tuple)):
                est = isinstance(val, tuple); amount = val[1] if est else val
                w = pw * amount / vmax
                col = ORANGE if foxit else BLUE
                ax.add_patch(FancyBboxPatch((x0, y - 0.22), max(w, 0.05), 0.44, boxstyle="round,pad=0,rounding_size=0.03",
                                            fc="white" if est else col, ec=col, lw=1.6, hatch="////" if est else None))
                label = f"${amount:,}" + (" *" if est else "")
                if w > 1.2:
                    ax.text(x0 + w - 0.08, y, label, ha="right", va="center", fontsize=11.5,
                            color=INK if est else "white", weight="bold",
                            bbox=dict(fc="white", ec="none", pad=1.5) if est else None)
                else:
                    ax.text(x0 + w + 0.08, y, label, ha="left", va="center", fontsize=11.5, color=INK, weight="bold")
            else:
                box(ax, x0, y - 0.22, 1.9, 0.44, "white", GRAY, lw=1.2, r=0.08)
                ax.text(x0 + 0.95, y, val, ha="center", va="center", fontsize=11, color=MUTED)
    ax.text(0.5, 0.35, "* PandaDoc at 100 and 250 a month is our arithmetic at $4 per extra document on API Developer.",
            fontsize=11, color=MUTED)
    ax.text(0.5, 0.0 + 0.05, "Grey outlined cells have no published price at that volume.", fontsize=11, color=MUTED)
    finish(fig, "diagram-cost-by-volume.png")


# D04: Foxit shared credit pool
def d04():
    fig = plt.figure(figsize=(16, 7.6))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 7.6); ax.axis("off")
    ax.text(0.5, 7.05, "One yearly credit pool for every Foxit API", fontsize=24, weight="bold", color=INK)
    ax.text(0.5, 6.6, "Startup: 5,000 credits a year. Business: 15,000 credits a year. Credits reset at renewal.", fontsize=14, color=MUTED)
    callers = [("eSign envelope created", "5 credits", True), ("PDF Services operation", "1 credit", True),
               ("Document Generation operation", "1 credit", True), ("Status check or webhook", "0 credits", False)]
    for i, (lbl, cost, uses) in enumerate(callers):
        y = 5.3 - i * 1.25
        box(ax, 0.5, y, 4.3, 0.95, ORANGE_SOFT if uses else PANEL, ORANGE if uses else LINE, lw=1.6, r=0.08)
        ax.text(0.75, y + 0.6, lbl, fontsize=13.5, weight="bold", color=INK, va="center")
        ax.text(0.75, y + 0.27, cost, fontsize=12.5, color=ORANGE if uses else MUTED, va="center", weight="bold")
        if uses:
            ax.add_patch(FancyArrowPatch((4.85, y + 0.47), (6.55, 3.7), arrowstyle="-|>", mutation_scale=18, color=ORANGE, lw=1.8))
    box(ax, 6.6, 2.4, 3.6, 2.6, "white", ORANGE, lw=2.5, r=0.15)
    ax.text(8.4, 4.25, "Shared pool", ha="center", fontsize=17, weight="bold", color=INK)
    ax.text(8.4, 3.65, "5,000 or 15,000", ha="center", fontsize=15, color=ORANGE, weight="bold")
    ax.text(8.4, 3.2, "credits a year", ha="center", fontsize=13, color=MUTED)
    ax.text(8.4, 2.7, "Alerts before it runs out", ha="center", fontsize=11.5, color=MUTED)
    ax.add_patch(FancyArrowPatch((10.25, 3.7), (11.0, 3.7), arrowstyle="-|>", mutation_scale=18, color=INK, lw=1.8))
    box(ax, 11.05, 4.15, 4.45, 1.55, PANEL, LINE, r=0.08)
    ax.text(11.3, 5.3, "Generate, then sign", fontsize=13.5, weight="bold", color=INK)
    ax.text(11.3, 4.85, "1 + 5 = 6 credits per document", fontsize=12.5, color=INK)
    ax.text(11.3, 4.45, "About 833 a year on Startup, 2,500 on Business", fontsize=11, color=MUTED)
    box(ax, 11.05, 1.7, 4.45, 2.15, "white", INK, lw=1.4, r=0.08)
    ax.text(11.3, 3.45, "At zero credits", fontsize=13.5, weight="bold", color=INK)
    ax.text(11.3, 3.0, "Calls that need credits stop", fontsize=12, color=INK)
    ax.text(11.3, 2.5, "HTTP 403", fontsize=12, color=INK, family="monospace", weight="bold")
    ax.text(11.3, 2.0, "until credits renew or you upgrade", fontsize=11, color=MUTED)
    ax.text(0.5, 0.35, "Per-operation rates from our pricing page. HTTP 403 is the status a live call returned on an empty pool. Totals are our arithmetic.",
            fontsize=11, color=MUTED)
    finish(fig, "diagram-foxit-credit-pool.png")


# D05: what happens at the cap
def d05():
    fig = plt.figure(figsize=(16, 7.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 7.4); ax.axis("off")
    ax.text(0.5, 6.85, "What happens when you pass the allowance", fontsize=24, weight="bold", color=INK)
    ax.text(0.5, 6.4, "Sending keeps going and the bill moves, or the bill is capped and sending stops", fontsize=14, color=MUTED)
    rows = [
        ("DocuSign", "Keeps sending", "API-plan overage rate not published; the contract sets the cost", BLUE),
        ("Dropbox Sign", "Keeps sending", "Automatic upgrade to the next tier, which stays in place (alert at 80%)", BLUE),
        ("Adobe Acrobat Sign", "Keeps sending", "Over-use settled by contract", BLUE),
        ("PandaDoc", "Depends on plan", "API Developer: $4 per extra document. Starter and Business: API creation pauses", GRAY),
        ("Foxit eSign API", "Stops", 'Calls that need credits stop (HTTP 403) until renewal or upgrade', ORANGE),
    ]
    for i, (name, outcome, detail, col) in enumerate(rows):
        y = 5.3 - i * 1.0
        ax.text(0.5, y + 0.33, name, fontsize=14, weight="bold", color=INK, va="center")
        box(ax, 3.7, y, 2.6, 0.66, col, r=0.08)
        ax.text(5.0, y + 0.33, outcome, ha="center", va="center", fontsize=13, weight="bold", color="white")
        ax.add_patch(FancyArrowPatch((6.4, y + 0.33), (7.1, y + 0.33), arrowstyle="-|>", mutation_scale=16, color=MUTED, lw=1.5))
        ax.text(7.25, y + 0.33, detail, va="center", fontsize=12, color=INK)
    ax.text(0.5, 0.35, "Vendor terms checked 27 Oct 2026. Foxit response from a live call on an exhausted account, 4 Nov 2026.",
            fontsize=11, color=MUTED)
    finish(fig, "diagram-cap-behavior.png")


if __name__ == "__main__":
    d01(); d02(); d03(); d04(); d05()
