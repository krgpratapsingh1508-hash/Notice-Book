import html
import io
import json
import os
import urllib.request
from datetime import date, datetime

import streamlit as st

DATA_FILE = "khata.json"
HOME = "🏠 सबका हिसाब"
KIND_LABELS = {"diya": "🔴 मैंने दिए", "mila": "🟢 मुझे मिले"}

st.set_page_config(page_title="खाता बुक", page_icon="📒", layout="centered")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

/* ---------- पीछे का बैकग्राउंड ---------- */
.stApp {
    background:
        radial-gradient(1100px 560px at 8% -10%, #dbe4ff 0%, transparent 60%),
        radial-gradient(900px 500px at 100% 0%, #fde2f3 0%, transparent 55%),
        radial-gradient(1000px 600px at 50% 115%, #d5f5ea 0%, transparent 55%),
        #f6f7fd;
    background-attachment: fixed;
}
.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp button,
.stApp input, .stApp textarea, .hero, .stat, .pcard, .tbl-wrap {
    font-family: 'Poppins', 'Noto Sans Devanagari', sans-serif;
}
.block-container {max-width: 820px; padding-top: 2.2rem; padding-bottom: 4rem;}
footer {visibility: hidden;}

/* ---------- हल्की थीम ज़बरदस्ती (config फ़ाइल के बिना) ---------- */
:root {color-scheme: light;}
[data-testid="stHeader"] {background: transparent;}
.stApp, [data-testid="stSidebar"] {color: #1f2340;}
.stApp [data-testid="stMarkdownContainer"] p, .stApp label, .stApp label p,
.stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stExpander"] summary, .stApp [data-testid="stExpander"] summary p,
.stApp [role="radiogroup"] p, .stApp h2, .stApp h3 {color: #1f2340 !important;}
.stApp input, .stApp textarea {color: #1f2340 !important; -webkit-text-fill-color: #1f2340;}
.stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"],
.stApp [data-baseweb="textarea"], .stApp [data-baseweb="select"] > div {
    background: #fff !important; border-color: rgba(99,102,241,.25) !important;
}
.stApp [data-baseweb="select"] div {color: #1f2340 !important;}
.stApp button[data-testid="stBaseButton-secondary"],
.stApp button[data-testid="stBaseButton-secondaryFormSubmit"],
.stApp [data-testid="stPopoverButton"] {background: #fff; color: #1f2340;}
.stApp button[data-testid^="stBaseButton-primary"] p {color: #fff !important;}
[data-testid="stFileUploaderDropzone"] {background: #fff;}
[data-testid="stFileUploaderDropzone"] * {color: #1f2340 !important;}

/* ---------- साइडबार ---------- */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,.72);
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(99,102,241,.15);
}
[data-testid="stSidebar"] h1 {
    background: linear-gradient(90deg, #4338ca, #db2777);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    font-weight: 800;
}

/* ---------- शीर्षक ---------- */
.stApp h1 {
    background: linear-gradient(90deg, #4338ca, #db2777);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    font-weight: 800; letter-spacing: -.5px;
}
.stApp h3 {color: #312e81; font-weight: 700;}

/* ---------- बटन ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    border-radius: 12px; font-weight: 600; border: 1px solid rgba(99,102,241,.3);
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px); box-shadow: 0 6px 16px rgba(79,70,229,.2);
    border-color: #6366f1; color: #4338ca;
}
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; border: none;
}
button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    color: #fff; box-shadow: 0 8px 20px rgba(124,58,237,.35);
}

/* ---------- फॉर्म / एक्सपैंडर ---------- */
[data-testid="stExpander"], [data-testid="stForm"] {
    background: rgba(255,255,255,.8); border-radius: 16px;
    border: 1px solid rgba(99,102,241,.18); box-shadow: 0 6px 20px rgba(67,56,202,.07);
}

/* ---------- ऊपर का बड़ा कार्ड ---------- */
.hero {position: relative; overflow: hidden; padding: 24px 26px; border-radius: 22px;
       color: #fff; margin-bottom: 20px; box-shadow: 0 14px 34px rgba(0,0,0,.18);}
.hero::after {content: ""; position: absolute; right: -50px; top: -60px; width: 200px; height: 200px;
              border-radius: 50%; background: rgba(255,255,255,.14);}
.hero::before {content: ""; position: absolute; right: 70px; bottom: -80px; width: 170px; height: 170px;
               border-radius: 50%; background: rgba(255,255,255,.09);}
.hero.get  {background: linear-gradient(135deg, #10b981, #047857);}
.hero.owe  {background: linear-gradient(135deg, #fb7185, #be123c);}
.hero.even {background: linear-gradient(135deg, #6366f1, #4338ca);}
.hero .h-name {font-size: 1.1rem; font-weight: 600; opacity: .95;}
.hero .h-label {font-size: .9rem; opacity: .85; margin-top: 12px;}
.hero .h-amt {font-size: 2.7rem; font-weight: 800; line-height: 1.1;}
.hero .h-sub {display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; position: relative; z-index: 1;}
.hero .h-sub span {background: rgba(255,255,255,.2); padding: 5px 12px; border-radius: 999px;
                   font-size: .8rem; font-weight: 500;}

/* ---------- होम के बॉक्स ---------- */
.stat {padding: 18px 20px; border-radius: 18px; background: #fff;
       box-shadow: 0 8px 24px rgba(67,56,202,.1); border-top: 5px solid;}
.stat.green {border-top-color: #10b981;}
.stat.red {border-top-color: #f43f5e;}
.stat .s-label {font-size: .82rem; color: #6b7094; font-weight: 500;}
.stat .s-val {font-size: 1.8rem; font-weight: 800;}
.stat.green .s-val {color: #059669;}
.stat.red .s-val {color: #e11d48;}

.pcard {display: flex; justify-content: space-between; align-items: center; background: #fff;
        padding: 15px 20px; border-radius: 16px; margin-bottom: 4px;
        box-shadow: 0 6px 18px rgba(67,56,202,.08); border-left: 6px solid #6366f1;}
.pcard.get {border-left-color: #10b981;}
.pcard.owe {border-left-color: #f43f5e;}
.pcard .p-name {font-weight: 700; font-size: 1.05rem; color: #1f2340;}
.pcard .p-status {font-size: .8rem; color: #6b7094;}
.pcard .p-amt {font-weight: 800; font-size: 1.2rem; text-align: right; color: #6b7094;}
.pcard.get .p-amt {color: #059669;}
.pcard.owe .p-amt {color: #e11d48;}

/* ---------- हिसाब की तालिका ---------- */
.tbl-wrap {background: #fff; border-radius: 20px; overflow-x: auto;
           box-shadow: 0 12px 32px rgba(67,56,202,.13); border: 1px solid rgba(99,102,241,.15);
           margin-bottom: 14px;}
table.ledger {width: 100%; border-collapse: collapse; font-size: .92rem; min-width: 560px;
              font-variant-numeric: tabular-nums;}
.ledger thead th {background: linear-gradient(135deg, #4338ca, #7c3aed); color: #fff;
                  padding: 13px 14px; text-align: left; font-weight: 600; white-space: nowrap;}
.ledger th.r, .ledger td.r {text-align: right;}
.ledger tbody td {padding: 11px 14px; border-bottom: 1px solid #eef0fb; color: #1f2340;}
.ledger tbody tr:nth-child(even) {background: #f8f9ff;}
.ledger tbody tr:hover {background: #eef2ff;}
.ledger td.sn {color: #8b8fb0; font-weight: 600; width: 46px;}
.ledger td.note {color: #5b6085; max-width: 220px; word-break: break-word;}
.ledger td.out {color: #e11d48; font-weight: 700;}
.ledger td.in {color: #059669; font-weight: 700;}
.ledger td.bal {font-weight: 700; white-space: nowrap;}
.ledger td.bal.get {color: #059669;}
.ledger td.bal.owe {color: #e11d48;}
.tag {font-size: .68rem; padding: 2px 8px; border-radius: 999px; margin-left: 6px; font-weight: 600;}
.tag.get {background: #d1fae5; color: #047857;}
.tag.owe {background: #ffe4e6; color: #be123c;}
.ledger tfoot td {background: #eef2ff; font-weight: 800; padding: 13px 14px;
                  border-top: 2px solid #c7d2fe; color: #312e81;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------- सहायक फ़ंक्शन ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            for v in d.values():
                v.sort(key=lambda e: e["date"])
            return d
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def balance(entries):
    """धनात्मक = मुझे लेना है, ऋणात्मक = मुझे देना है।"""
    return sum(e["amount"] if e["type"] == "diya" else -e["amount"] for e in entries)


def totals(entries):
    diya = sum(e["amount"] for e in entries if e["type"] == "diya")
    mila = sum(e["amount"] for e in entries if e["type"] == "mila")
    return diya, mila


def inr(x):
    """भारतीय तरीका: 1,23,456"""
    x = abs(x)
    whole, frac = f"{x:.2f}".split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])
    return f"₹{whole}" + ("" if frac == "00" else f".{frac}")


def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d-%m-%Y")
    except ValueError:
        return iso


def esc(s):
    return html.escape(str(s))


def sort_entries(entries):
    entries.sort(key=lambda e: e["date"])  # तारीख के हिसाब से क्रम (बराबर तारीख में पुराना पहले)


def bal_cell(b):
    if b > 0:
        return "get", f'{inr(b)}<span class="tag get">लेना</span>'
    if b < 0:
        return "owe", f'{inr(b)}<span class="tag owe">देना</span>'
    return "", "₹0"


def ledger_html(entries):
    rows, run, t_d, t_m = [], 0.0, 0.0, 0.0
    for i, e in enumerate(entries):
        a = e["amount"]
        if e["type"] == "diya":
            run += a
            t_d += a
            out, inn = inr(a), "—"
        else:
            run -= a
            t_m += a
            out, inn = "—", inr(a)
        cls, cell = bal_cell(run)
        note = esc(e["note"]) if e["note"] else "—"
        rows.append(
            f'<tr><td class="sn">{i + 1}</td><td>{fmt_date(e["date"])}</td>'
            f'<td class="note">{note}</td><td class="r out">{out}</td>'
            f'<td class="r in">{inn}</td><td class="r bal {cls}">{cell}</td></tr>'
        )
    fcls, fcell = bal_cell(run)
    foot = (
        f'<tr><td colspan="3">कुल</td><td class="r out">{inr(t_d)}</td>'
        f'<td class="r in">{inr(t_m)}</td><td class="r bal {fcls}">{fcell}</td></tr>'
    )
    return (
        '<div class="tbl-wrap"><table class="ledger"><thead><tr>'
        '<th>क्र.</th><th>तारीख</th><th>विवरण</th>'
        '<th class="r">दिए (₹)</th><th class="r">मिले (₹)</th><th class="r">बाकी</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody><tfoot>{foot}</tfoot></table></div>'
    )


# ---------- Excel / PDF बनाने वाले फ़ंक्शन ----------
FONT_DIR = "khata_fonts"
FONT_URLS = {
    "Hind-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/hind/Hind-Regular.ttf",
    "Hind-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/hind/Hind-Bold.ttf",
}


def ensure_fonts():
    """हिंदी फ़ॉन्ट (Hind) एक बार डाउनलोड होकर khata_fonts/ में रहता है।"""
    os.makedirs(FONT_DIR, exist_ok=True)
    paths = {}
    for fname, url in FONT_URLS.items():
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path) or os.path.getsize(path) < 10000:
            urllib.request.urlretrieve(url, path)
        paths[fname] = path
    return paths


def ledger_rows(entries):
    """(क्र., तारीख, विवरण, दिए, मिले, बाकी) की सूची + कुल।"""
    run, t_d, t_m, rows = 0.0, 0.0, 0.0, []
    for i, e in enumerate(entries, 1):
        a = e["amount"]
        if e["type"] == "diya":
            run += a
            t_d += a
        else:
            run -= a
            t_m += a
        rows.append((i, e["date"], e["note"], a if e["type"] == "diya" else None,
                     a if e["type"] == "mila" else None, run))
    return rows, t_d, t_m, run


def make_excel(name, entries):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    rows, t_d, t_m, bal = ledger_rows(entries)
    wb = Workbook()
    ws = wb.active
    ws.title = "खाता"[:31]
    ws.sheet_view.showGridLines = False

    indigo = PatternFill("solid", fgColor="4338CA")
    light = PatternFill("solid", fgColor="EEF2FF")
    zebra = PatternFill("solid", fgColor="F8F9FF")
    thin = Side(style="thin", color="E0E4F5")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    money = '"₹"#,##0.00'

    ws.merge_cells("A1:F1")
    ws["A1"] = f"📒 खाता बुक — {name}"
    ws["A1"].font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    ws["A1"].fill = indigo
    ws["A1"].alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:F2")
    if bal > 0:
        status = f"आपको लेना है: {inr(bal)}"
    elif bal < 0:
        status = f"आपको देना है: {inr(bal)}"
    else:
        status = "हिसाब बराबर"
    ws["A2"] = f"{status}   |   रिपोर्ट की तारीख: {date.today().strftime('%d-%m-%Y')}"
    ws["A2"].font = Font(size=11, bold=True, color="312E81")
    ws["A2"].fill = light
    ws["A2"].alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[2].height = 22

    heads = ["क्र.", "तारीख", "विवरण", "दिए (₹)", "मिले (₹)", "बाकी (₹)"]
    for c, h in enumerate(heads, 1):
        cell = ws.cell(row=4, column=c, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = indigo
        cell.border = border
        cell.alignment = Alignment(horizontal="center" if c < 3 else "right" if c > 3 else "left",
                                   vertical="center")
    ws.row_dimensions[4].height = 22

    r = 5
    for n, d, note, out, inn, run in rows:
        try:
            dval = date.fromisoformat(d)
        except ValueError:
            dval = d
        vals = [n, dval, note or "", out, inn, run]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v)
            cell.border = border
            if n % 2 == 0:
                cell.fill = zebra
        ws.cell(row=r, column=1).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=2).number_format = "DD-MM-YYYY"
        ws.cell(row=r, column=2).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=3).alignment = Alignment(wrap_text=True, vertical="top")
        for c in (4, 5, 6):
            ws.cell(row=r, column=c).number_format = money
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="right")
        ws.cell(row=r, column=4).font = Font(color="E11D48", bold=True)
        ws.cell(row=r, column=5).font = Font(color="059669", bold=True)
        ws.cell(row=r, column=6).font = Font(
            bold=True, color="059669" if run > 0 else "E11D48" if run < 0 else "000000")
        r += 1

    ws.cell(row=r, column=1, value="कुल")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=3)
    ws.cell(row=r, column=4, value=t_d)
    ws.cell(row=r, column=5, value=t_m)
    ws.cell(row=r, column=6, value=bal)
    for c in range(1, 7):
        cell = ws.cell(row=r, column=c)
        cell.fill = light
        cell.font = Font(bold=True, color="312E81")
        cell.border = Border(top=Side(style="medium", color="4338CA"), bottom=thin, left=thin, right=thin)
        if c >= 4:
            cell.number_format = money
            cell.alignment = Alignment(horizontal="right")
    ws.cell(row=r + 1, column=6, value="(+) लेना / (−) देना").font = Font(size=9, italic=True, color="6B7094")
    ws.cell(row=r + 1, column=6).alignment = Alignment(horizontal="right")

    for col, w in zip("ABCDEF", (7, 13, 38, 15, 15, 16)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def make_pdf(name, entries):
    from fpdf import FPDF
    from fpdf.fonts import FontFace

    fonts = ensure_fonts()
    rows, t_d, t_m, bal = ledger_rows(entries)

    INK = (20, 24, 40)          # मुख्य काला-नीला टेक्स्ट
    MUTED = (90, 96, 120)       # हल्का टेक्स्ट
    NAVY = (30, 41, 90)         # हेडर
    RED = (176, 24, 44)         # गहरा लाल (देना / दिए)
    GREEN = (4, 120, 87)        # गहरा हरा (लेना / मिले)
    LINE = (200, 205, 225)
    ZEBRA = (244, 246, 251)
    TOTAL = (226, 232, 248)
    WHITE = (255, 255, 255)

    if bal > 0:
        tint, accent = (236, 250, 242), GREEN
        headline = f"आपको {inr(bal)} लेना है"
    elif bal < 0:
        tint, accent = (254, 241, 242), RED
        headline = f"आपको {inr(bal)} देना है"
    else:
        tint, accent = (238, 242, 255), NAVY
        headline = "हिसाब बराबर है"

    class PDF(FPDF):
        def footer(self):
            self.set_y(-14)
            self.set_font("Hind", "", 9)
            self.set_text_color(*MUTED)
            self.cell(100, 8, f"खाता बुक  •  {date.today().strftime('%d-%m-%Y')}")
            self.cell(0, 8, f"पृष्ठ {self.page_no()} / {{nb}}", align="R")

    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.add_font("Hind", "", fonts["Hind-Regular.ttf"])
    pdf.add_font("Hind", "B", fonts["Hind-Bold.ttf"])
    pdf.set_text_shaping(True)  # देवनागरी मात्राएँ सही जुड़ें (uharfbuzz चाहिए)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, margin=18)
    pdf.set_margins(14, 14, 14)
    pdf.add_page()

    # ---- शीर्षक (सादा, सफ़ेद पेज) ----
    pdf.set_text_color(*NAVY)
    pdf.set_font("Hind", "B", 22)
    pdf.cell(0, 10, "खाता बुक", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*MUTED)
    pdf.set_font("Hind", "", 10.5)
    pdf.cell(0, 6, f"तारीख: {date.today().strftime('%d-%m-%Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.6)
    pdf.line(14, pdf.get_y() + 2, 196, pdf.get_y() + 2)

    # ---- सारांश बॉक्स: हल्की पृष्ठभूमि, गहरा टेक्स्ट ----
    y = pdf.get_y() + 8
    pdf.set_fill_color(*tint)
    pdf.set_draw_color(*LINE)
    pdf.set_line_width(0.3)
    pdf.rect(14, y, 182, 32, style="DF", round_corners=True)
    pdf.set_xy(20, y + 4)
    pdf.set_text_color(*INK)
    pdf.set_font("Hind", "B", 15)
    pdf.cell(100, 8, name)
    pdf.set_xy(20, y + 14)
    pdf.set_text_color(*accent)
    pdf.set_font("Hind", "B", 17)
    pdf.cell(105, 10, headline)
    pdf.set_font("Hind", "", 10.5)
    pdf.set_text_color(*INK)
    for k, txt in enumerate((f"कुल दिए:  {inr(t_d)}", f"कुल मिले:  {inr(t_m)}", f"कुल एंट्री:  {len(rows)}")):
        pdf.set_xy(125, y + 4 + k * 8)
        pdf.cell(65, 7, txt, align="R")

    # ---- तालिका ----
    pdf.set_y(y + 40)
    pdf.set_text_color(*NAVY)
    pdf.set_font("Hind", "B", 13)
    pdf.cell(0, 8, "हिसाब की तालिका", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.set_fill_color(*WHITE)
    pdf.set_text_color(*INK)
    pdf.set_font("Hind", "", 10.5)

    def fs(color=INK, bold=False, fill=WHITE):
        return FontFace(emphasis="BOLD" if bold else None, color=color, fill_color=fill)

    def bal_text(v):
        return inr(v) + (" (लेना)" if v > 0 else " (देना)" if v < 0 else "")

    def bal_color(v):
        return GREEN if v > 0 else RED if v < 0 else INK

    with pdf.table(
        col_widths=(10, 25, 49, 29, 29, 40),
        text_align=("CENTER", "CENTER", "LEFT", "RIGHT", "RIGHT", "RIGHT"),
        line_height=7.5,
        borders_layout="HORIZONTAL_LINES",
        first_row_as_headings=True,
        headings_style=FontFace(emphasis="BOLD", color=WHITE, fill_color=NAVY),
        padding=(1.6, 2),
        repeat_headings=1,
    ) as table:
        h = table.row()
        for t in ("क्र.", "तारीख", "विवरण", "दिए (₹)", "मिले (₹)", "बाकी"):
            h.cell(t)
        for n, d, note, out, inn, run in rows:
            bg = WHITE if n % 2 else ZEBRA
            r = table.row()
            r.cell(str(n), style=fs(MUTED, False, bg))
            r.cell(fmt_date(d), style=fs(INK, False, bg))
            r.cell(note or "—", style=fs(INK, False, bg))
            r.cell(inr(out) if out else "—", style=fs(RED if out else MUTED, bool(out), bg))
            r.cell(inr(inn) if inn else "—", style=fs(GREEN if inn else MUTED, bool(inn), bg))
            r.cell(bal_text(run), style=fs(bal_color(run), True, bg))
        r = table.row()
        r.cell("कुल", colspan=3, align="L", style=fs(NAVY, True, TOTAL))
        r.cell(inr(t_d), style=fs(RED, True, TOTAL))
        r.cell(inr(t_m), style=fs(GREEN, True, TOTAL))
        r.cell(bal_text(bal), style=fs(bal_color(bal), True, TOTAL))

    # ---- समझने के लिए छोटा नोट ----
    pdf.ln(5)
    pdf.set_x(14)
    pdf.set_text_color(*MUTED)
    pdf.set_font("Hind", "", 9.5)
    pdf.multi_cell(
        182, 5.5,
        "दिए = आपने दिए  |  मिले = आपको मिले\n"
        "बाकी (लेना) = सामने वाले से आपको लेना है  |  बाकी (देना) = आपको सामने वाले को देना है",
    )

    return bytes(pdf.output())


def goto(target):
    st.session_state.pending_nav = target
    st.rerun()


# ---------- स्टेट ----------
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "edit" not in st.session_state:
    st.session_state.edit = None
if "nav" not in st.session_state:
    st.session_state.nav = HOME
if "pending_nav" in st.session_state:
    st.session_state.nav = st.session_state.pop("pending_nav")

data = st.session_state.data
if st.session_state.nav != HOME and st.session_state.nav not in data:
    st.session_state.nav = HOME

# ---------- साइडबार ----------
st.sidebar.title("📒 खाता बुक")

with st.sidebar.form("add_person", clear_on_submit=True):
    new_name = st.text_input("नया व्यक्ति जोड़ें", placeholder="नाम लिखिए")
    if st.form_submit_button("➕ जोड़ें", use_container_width=True, type="primary"):
        name = new_name.strip()
        if not name:
            st.sidebar.warning("नाम लिखिए।")
        elif name in data or name == HOME:
            st.sidebar.warning("यह नाम पहले से है।")
        else:
            data[name] = []
            save_data(data)
            goto(name)

choice = st.sidebar.radio(
    "किसका खाता?", [HOME] + sorted(data.keys(), key=str.lower), key="nav"
)

st.sidebar.divider()
st.sidebar.download_button(
    "💾 बैकअप डाउनलोड",
    data=json.dumps(data, ensure_ascii=False, indent=2),
    file_name="khata_backup.json",
    mime="application/json",
    use_container_width=True,
)
uploaded = st.sidebar.file_uploader("बैकअप वापस डालें", type="json")
if uploaded is not None and st.sidebar.button("♻️ रिस्टोर करें", use_container_width=True):
    try:
        restored = json.load(uploaded)
        for v in restored.values():
            sort_entries(v)
        st.session_state.data = restored
        save_data(restored)
        goto(HOME)
    except (json.JSONDecodeError, AttributeError, KeyError):
        st.sidebar.error("फ़ाइल सही नहीं है।")

# =====================================================
# होम पेज
# =====================================================
if choice == HOME:
    st.title("📒 सबका हिसाब")

    if not data:
        st.info("अभी कोई व्यक्ति नहीं है। साइडबार से नया नाम जोड़ें।")
    else:
        to_receive = sum(max(balance(e), 0) for e in data.values())
        to_pay = sum(max(-balance(e), 0) for e in data.values())

        c1, c2 = st.columns(2)
        c1.markdown(
            f'<div class="stat green"><div class="s-label">कुल लेना है</div>'
            f'<div class="s-val">{inr(to_receive)}</div></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="stat red"><div class="s-label">कुल देना है</div>'
            f'<div class="s-val">{inr(to_pay)}</div></div>',
            unsafe_allow_html=True,
        )

        st.write("")
        q = st.text_input("🔍 नाम खोजें", placeholder="नाम लिखिए...")

        people = [n for n in sorted(data, key=str.lower) if q.lower() in n.lower()]
        if not people:
            st.caption("कोई नाम नहीं मिला।")
        for n in people:
            b = balance(data[n])
            if b > 0:
                cls, status = "get", "आपको लेना है"
            elif b < 0:
                cls, status = "owe", "आपको देना है"
            else:
                cls, status = "", "हिसाब बराबर ✅"
            col_card, col_btn = st.columns([5, 1], vertical_alignment="center")
            col_card.markdown(
                f'<div class="pcard {cls}"><div><div class="p-name">{esc(n)}</div>'
                f'<div class="p-status">{status} • {len(data[n])} एंट्री</div></div>'
                f'<div class="p-amt">{inr(b) if b else "—"}</div></div>',
                unsafe_allow_html=True,
            )
            if col_btn.button("खोलें", key=f"open_{n}", use_container_width=True):
                goto(n)

# =====================================================
# व्यक्ति का पेज
# =====================================================
else:
    name = choice
    entries = data[name]
    b = balance(entries)
    t_diya, t_mila = totals(entries)

    if b > 0:
        cls, label = "get", "आपको लेना है"
    elif b < 0:
        cls, label = "owe", "आपको देना है"
    else:
        cls, label = "even", "हिसाब बराबर ✅"

    st.markdown(
        f'<div class="hero {cls}"><div class="h-name">👤 {esc(name)}</div>'
        f'<div class="h-label">{label}</div>'
        f'<div class="h-amt">{inr(b) if b else "₹0"}</div>'
        f'<div class="h-sub"><span>🔴 कुल दिए: {inr(t_diya)}</span>'
        f'<span>🟢 कुल मिले: {inr(t_mila)}</span>'
        f'<span>📄 {len(entries)} एंट्री</span></div></div>',
        unsafe_allow_html=True,
    )

    # ---- नई एंट्री ----
    with st.expander("➕ नई एंट्री", expanded=not entries):
        with st.form("add_entry", clear_on_submit=True):
            kind = st.radio(
                "क्या हुआ?", list(KIND_LABELS), format_func=KIND_LABELS.get, horizontal=True
            )
            c1, c2 = st.columns(2)
            amount = c1.number_input("राशि (₹)", min_value=0.0, step=10.0, format="%.2f")
            when = c2.date_input("तारीख", value=date.today())
            note = st.text_input("नोट (वैकल्पिक)", placeholder="जैसे: दुकान का सामान")
            if st.form_submit_button("✅ सेव करें", use_container_width=True, type="primary"):
                if amount <= 0:
                    st.warning("राशि 0 से ज़्यादा होनी चाहिए।")
                else:
                    entries.append(
                        {
                            "date": when.isoformat(),
                            "type": kind,
                            "amount": float(amount),
                            "note": note.strip(),
                        }
                    )
                    sort_entries(entries)
                    save_data(data)
                    st.session_state.pop(f"sel_{name}", None)
                    st.rerun()

    # ---- तालिका ----
    st.subheader("📜 हिसाब की तालिका")

    if not entries:
        st.caption("अभी कोई एंट्री नहीं है।")
    else:
        st.markdown(ledger_html(entries), unsafe_allow_html=True)

        # ---- बदलें / हटाएं ----
        editing = st.session_state.edit
        is_editing_here = bool(editing) and editing[0] == name and editing[1] < len(entries)

        with st.expander("✏️ एंट्री बदलें / हटाएं", expanded=is_editing_here):

            def label_for(i):
                e = entries[i]
                kind_txt = "दिए" if e["type"] == "diya" else "मिले"
                txt = f"#{i + 1} • {fmt_date(e['date'])} • {kind_txt} {inr(e['amount'])}"
                return txt + (f" • {e['note']}" if e["note"] else "")

            default_idx = editing[1] if is_editing_here else 0
            sel = st.selectbox(
                "कौन सी एंट्री?",
                list(range(len(entries))),
                index=default_idx,
                format_func=label_for,
                key=f"sel_{name}",
            )

            b1, b2 = st.columns(2)
            if b1.button("✏️ बदलें", use_container_width=True, key=f"editbtn_{name}"):
                st.session_state.edit = (name, sel)
                st.rerun()
            with b2.popover("🗑️ हटाएं", use_container_width=True):
                st.write("पक्का हटाना है?")
                if st.button("हाँ, हटाओ", key=f"del_{name}", type="primary"):
                    entries.pop(sel)
                    save_data(data)
                    st.session_state.edit = None
                    st.session_state.pop(f"sel_{name}", None)
                    st.rerun()

            if is_editing_here:
                i = editing[1]
                e = entries[i]
                with st.form(f"edit_form_{name}_{i}"):
                    st.markdown(f"**✏️ एंट्री #{i + 1} बदलें**")
                    k = st.radio(
                        "क्या हुआ?",
                        list(KIND_LABELS),
                        index=0 if e["type"] == "diya" else 1,
                        format_func=KIND_LABELS.get,
                        horizontal=True,
                    )
                    c1, c2 = st.columns(2)
                    amt = c1.number_input(
                        "राशि (₹)", min_value=0.0, step=10.0, value=float(e["amount"]), format="%.2f"
                    )
                    try:
                        dflt = date.fromisoformat(e["date"])
                    except ValueError:
                        dflt = date.today()
                    dt = c2.date_input("तारीख", value=dflt)
                    nt = st.text_input("नोट", value=e["note"])
                    s1, s2 = st.columns(2)
                    save = s1.form_submit_button("💾 सेव", use_container_width=True, type="primary")
                    cancel = s2.form_submit_button("✖️ रद्द करें", use_container_width=True)
                if save:
                    if amt <= 0:
                        st.warning("राशि 0 से ज़्यादा होनी चाहिए।")
                    else:
                        entries[i] = {
                            "date": dt.isoformat(),
                            "type": k,
                            "amount": float(amt),
                            "note": nt.strip(),
                        }
                        sort_entries(entries)
                        save_data(data)
                        st.session_state.edit = None
                        st.session_state.pop(f"sel_{name}", None)
                        st.rerun()
                if cancel:
                    st.session_state.edit = None
                    st.rerun()

        # ---- Excel / PDF ----
        st.write("")
        d1, d2 = st.columns(2)
        safe = "".join(ch if ch.isalnum() or ch in " _-" else "_" for ch in name).strip() or "khata"
        d1.download_button(
            "📊 Excel डाउनलोड",
            make_excel(name, entries),
            file_name=f"{safe}_khata.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        try:
            pdf_bytes = make_pdf(name, entries)
        except Exception as ex:  # फ़ॉन्ट/लाइब्रेरी न मिले तो बाकी ऐप चलता रहे
            pdf_bytes = None
            d2.button("📄 PDF डाउनलोड", disabled=True, use_container_width=True)
            st.caption(f"PDF नहीं बन पाई: {ex}")
        if pdf_bytes:
            d2.download_button(
                "📄 PDF डाउनलोड",
                pdf_bytes,
                file_name=f"{safe}_khata.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )

    # ---- व्यक्ति की सेटिंग ----
    with st.expander("⚙️ नाम बदलें / व्यक्ति हटाएं"):
        new_n = st.text_input("नया नाम", value=name, key=f"rename_{name}")
        if st.button("नाम बदलें"):
            nn = new_n.strip()
            if not nn:
                st.warning("नाम खाली नहीं हो सकता।")
            elif nn != name and (nn in data or nn == HOME):
                st.warning("यह नाम पहले से है।")
            elif nn != name:
                data[nn] = data.pop(name)
                save_data(data)
                st.session_state.edit = None
                goto(nn)

        st.divider()
        st.caption("इस व्यक्ति का पूरा हिसाब हट जाएगा।")
        with st.popover(f"🗑️ {name} को हटाएं"):
            st.write("पक्का हटाना है? यह वापस नहीं आएगा।")
            if st.button("हाँ, हटा दो", key="del_person", type="primary"):
                del data[name]
                save_data(data)
                st.session_state.edit = None
                goto(HOME)
