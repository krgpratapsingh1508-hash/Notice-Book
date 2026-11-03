import html
import json
import os
from datetime import date, datetime

import pandas as pd
import streamlit as st

DATA_FILE = "khata.json"
HOME = "🏠 Sabka Hisab"
KIND_LABELS = {"diya": "🔴 Maine diye", "mila": "🟢 Mujhe mile"}

st.set_page_config(page_title="Khata Book", page_icon="📒", layout="centered")

CSS = """
<style>
.block-container {max-width: 760px; padding-top: 2rem;}
.hero {padding: 22px 24px; border-radius: 20px; color: #fff; margin-bottom: 18px;
       box-shadow: 0 6px 18px rgba(0,0,0,.15);}
.hero.get  {background: linear-gradient(135deg, #0f9b6c, #0a6b4d);}
.hero.owe  {background: linear-gradient(135deg, #e5484d, #a61e4d);}
.hero.even {background: linear-gradient(135deg, #4f6df5, #3b4cca);}
.hero .h-name {font-size: 1.05rem; opacity: .9;}
.hero .h-label {font-size: .9rem; opacity: .85; margin-top: 10px;}
.hero .h-amt {font-size: 2.4rem; font-weight: 800; line-height: 1.1;}
.hero .h-sub {display: flex; gap: 22px; margin-top: 14px; font-size: .85rem; opacity: .9;}

.stat {padding: 16px 18px; border-radius: 16px; border: 1px solid rgba(128,128,128,.25);
       background: rgba(128,128,128,.07);}
.stat .s-label {font-size: .8rem; opacity: .7;}
.stat .s-val {font-size: 1.6rem; font-weight: 800;}
.stat.green .s-val {color: #2fb67c;}
.stat.red .s-val {color: #e5484d;}

.entry {display: flex; justify-content: space-between; align-items: center;
        padding: 12px 16px; border-radius: 14px; margin-bottom: 4px;
        border: 1px solid rgba(128,128,128,.25); border-left: 6px solid;
        background: rgba(128,128,128,.06);}
.entry.diya {border-left-color: #e5484d;}
.entry.mila {border-left-color: #2fb67c;}
.entry .e-date {font-weight: 600; font-size: .95rem;}
.entry .e-note {font-size: .85rem; opacity: .7; margin-top: 2px;}
.entry .e-amt {font-weight: 800; font-size: 1.15rem; text-align: right;}
.entry.diya .e-amt {color: #e5484d;}
.entry.mila .e-amt {color: #2fb67c;}
.entry .e-bal {font-size: .75rem; opacity: .65; text-align: right; margin-top: 2px;}

.pcard {display: flex; justify-content: space-between; align-items: center;
        padding: 14px 18px; border-radius: 16px; margin-bottom: 4px;
        border: 1px solid rgba(128,128,128,.25); border-left: 6px solid #4f6df5;
        background: rgba(128,128,128,.06);}
.pcard.get {border-left-color: #2fb67c;}
.pcard.owe {border-left-color: #e5484d;}
.pcard .p-name {font-weight: 700; font-size: 1.05rem;}
.pcard .p-status {font-size: .8rem; opacity: .7;}
.pcard .p-amt {font-weight: 800; font-size: 1.2rem; text-align: right;}
.pcard.get .p-amt {color: #2fb67c;}
.pcard.owe .p-amt {color: #e5484d;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Helpers ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def balance(entries):
    """Positive = mujhe lena hai, Negative = mujhe dena hai."""
    return sum(e["amount"] if e["type"] == "diya" else -e["amount"] for e in entries)


def totals(entries):
    diya = sum(e["amount"] for e in entries if e["type"] == "diya")
    mila = sum(e["amount"] for e in entries if e["type"] == "mila")
    return diya, mila


def inr(x):
    """Indian style grouping: 1,23,456"""
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
        return datetime.fromisoformat(iso).strftime("%d %b %Y")
    except ValueError:
        return iso


def esc(s):
    return html.escape(str(s))


def goto(target):
    st.session_state.pending_nav = target
    st.rerun()


# ---------- State ----------
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

# ---------- Sidebar ----------
st.sidebar.title("📒 Khata Book")

with st.sidebar.form("add_person", clear_on_submit=True):
    new_name = st.text_input("Naya vyakti jodein", placeholder="Naam likhiye")
    if st.form_submit_button("➕ Jodein", use_container_width=True):
        name = new_name.strip()
        if not name:
            st.sidebar.warning("Naam likhiye.")
        elif name in data or name == HOME:
            st.sidebar.warning("Ye naam pehle se hai.")
        else:
            data[name] = []
            save_data(data)
            goto(name)

choice = st.sidebar.radio(
    "Kiska khata?", [HOME] + sorted(data.keys(), key=str.lower), key="nav"
)

st.sidebar.divider()
st.sidebar.download_button(
    "💾 Backup download",
    data=json.dumps(data, ensure_ascii=False, indent=2),
    file_name="khata_backup.json",
    mime="application/json",
    use_container_width=True,
)
uploaded = st.sidebar.file_uploader("Backup wapas daalein", type="json")
if uploaded is not None and st.sidebar.button("♻️ Restore karein", use_container_width=True):
    try:
        st.session_state.data = json.load(uploaded)
        save_data(st.session_state.data)
        goto(HOME)
    except json.JSONDecodeError:
        st.sidebar.error("File sahi nahi hai.")

# =====================================================
# HOME PAGE
# =====================================================
if choice == HOME:
    st.title("📒 Sabka Hisab")

    if not data:
        st.info("Abhi koi vyakti nahi hai. Sidebar se naya naam jodein.")
    else:
        to_receive = sum(max(balance(e), 0) for e in data.values())
        to_pay = sum(max(-balance(e), 0) for e in data.values())

        c1, c2 = st.columns(2)
        c1.markdown(
            f'<div class="stat green"><div class="s-label">Kul lena hai</div>'
            f'<div class="s-val">{inr(to_receive)}</div></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="stat red"><div class="s-label">Kul dena hai</div>'
            f'<div class="s-val">{inr(to_pay)}</div></div>',
            unsafe_allow_html=True,
        )

        st.write("")
        q = st.text_input("🔍 Naam khojein", placeholder="Naam likhiye...")

        people = [n for n in sorted(data, key=str.lower) if q.lower() in n.lower()]
        if not people:
            st.caption("Koi naam nahi mila.")
        for n in people:
            b = balance(data[n])
            if b > 0:
                cls, status = "get", "Aapko lena hai"
            elif b < 0:
                cls, status = "owe", "Aapko dena hai"
            else:
                cls, status = "", "Hisab barabar ✅"
            col_card, col_btn = st.columns([5, 1], vertical_alignment="center")
            col_card.markdown(
                f'<div class="pcard {cls}"><div><div class="p-name">{esc(n)}</div>'
                f'<div class="p-status">{status} • {len(data[n])} entry</div></div>'
                f'<div class="p-amt">{inr(b) if b else "—"}</div></div>',
                unsafe_allow_html=True,
            )
            if col_btn.button("Kholein", key=f"open_{n}", use_container_width=True):
                goto(n)

# =====================================================
# PERSON PAGE
# =====================================================
else:
    name = choice
    entries = data[name]
    b = balance(entries)
    t_diya, t_mila = totals(entries)

    if b > 0:
        cls, label = "get", "Aapko lena hai"
    elif b < 0:
        cls, label = "owe", "Aapko dena hai"
    else:
        cls, label = "even", "Hisab barabar ✅"

    st.markdown(
        f'<div class="hero {cls}"><div class="h-name">👤 {esc(name)}</div>'
        f'<div class="h-label">{label}</div>'
        f'<div class="h-amt">{inr(b) if b else "₹0"}</div>'
        f'<div class="h-sub"><span>🔴 Kul diye: {inr(t_diya)}</span>'
        f'<span>🟢 Kul mile: {inr(t_mila)}</span></div></div>',
        unsafe_allow_html=True,
    )

    # ---- Add entry ----
    with st.expander("➕ Nayi entry", expanded=not entries):
        with st.form("add_entry", clear_on_submit=True):
            kind = st.radio(
                "Kya hua?", list(KIND_LABELS), format_func=KIND_LABELS.get, horizontal=True
            )
            c1, c2 = st.columns(2)
            amount = c1.number_input("Rakam (₹)", min_value=0.0, step=10.0, format="%.2f")
            when = c2.date_input("Tareekh", value=date.today())
            note = st.text_input("Note (optional)", placeholder="Jaise: dukaan ka saman")
            if st.form_submit_button("✅ Save karein", use_container_width=True):
                if amount <= 0:
                    st.warning("Rakam 0 se zyada honi chahiye.")
                else:
                    entries.append(
                        {
                            "date": when.isoformat(),
                            "type": kind,
                            "amount": float(amount),
                            "note": note.strip(),
                        }
                    )
                    save_data(data)
                    st.rerun()

    # ---- List ----
    st.subheader("📜 Hisab ki list")

    if not entries:
        st.caption("Abhi koi entry nahi hai.")
    else:
        flt = st.radio(
            "Dikhayein",
            ["Sab", "Diye", "Mile"],
            horizontal=True,
            label_visibility="collapsed",
        )

        # running balance (purani se nayi tak)
        running, run_list = 0.0, []
        for e in entries:
            running += e["amount"] if e["type"] == "diya" else -e["amount"]
            run_list.append(running)

        order = list(range(len(entries)))[::-1]  # nayi entry sabse upar
        shown = 0
        for i in order:
            e = entries[i]
            if flt == "Diye" and e["type"] != "diya":
                continue
            if flt == "Mile" and e["type"] != "mila":
                continue
            shown += 1

            # ---- Edit mode ----
            if st.session_state.edit == (name, i):
                with st.form(f"edit_form_{i}"):
                    st.markdown(f"**✏️ Entry #{i + 1} badlein**")
                    k = st.radio(
                        "Kya hua?",
                        list(KIND_LABELS),
                        index=0 if e["type"] == "diya" else 1,
                        format_func=KIND_LABELS.get,
                        horizontal=True,
                    )
                    c1, c2 = st.columns(2)
                    amt = c1.number_input(
                        "Rakam (₹)", min_value=0.0, step=10.0, value=float(e["amount"]), format="%.2f"
                    )
                    try:
                        dflt = date.fromisoformat(e["date"])
                    except ValueError:
                        dflt = date.today()
                    dt = c2.date_input("Tareekh", value=dflt)
                    nt = st.text_input("Note", value=e["note"])
                    b1, b2 = st.columns(2)
                    save = b1.form_submit_button("💾 Save", use_container_width=True)
                    cancel = b2.form_submit_button("✖️ Cancel", use_container_width=True)
                if save:
                    if amt <= 0:
                        st.warning("Rakam 0 se zyada honi chahiye.")
                    else:
                        entries[i] = {
                            "date": dt.isoformat(),
                            "type": k,
                            "amount": float(amt),
                            "note": nt.strip(),
                        }
                        save_data(data)
                        st.session_state.edit = None
                        st.rerun()
                if cancel:
                    st.session_state.edit = None
                    st.rerun()
                continue

            # ---- Normal card ----
            sign = "−" if e["type"] == "diya" else "+"
            tag = "diya" if e["type"] == "diya" else "mila"
            note_html = f'<div class="e-note">{esc(e["note"])}</div>' if e["note"] else ""
            rb = run_list[i]
            bal_txt = f"Baaki: {inr(rb)}" if rb else "Baaki: ₹0"
            col_card, col_edit, col_del = st.columns([8, 1, 1], vertical_alignment="center")
            col_card.markdown(
                f'<div class="entry {tag}"><div><div class="e-date">{fmt_date(e["date"])}</div>'
                f"{note_html}</div><div><div class=\"e-amt\">{sign} {inr(e['amount'])}</div>"
                f'<div class="e-bal">{bal_txt}</div></div></div>',
                unsafe_allow_html=True,
            )
            if col_edit.button("✏️", key=f"edit_{name}_{i}", help="Badlein"):
                st.session_state.edit = (name, i)
                st.rerun()
            with col_del.popover("🗑️", help="Delete"):
                st.write("Pakka delete karein?")
                if st.button("Haan, delete", key=f"del_{name}_{i}", type="primary"):
                    entries.pop(i)
                    save_data(data)
                    st.session_state.edit = None
                    st.rerun()

        if shown == 0:
            st.caption("Is filter me koi entry nahi hai.")

        # ---- CSV download ----
        df = pd.DataFrame(
            [
                {
                    "Tareekh": e["date"],
                    "Type": "Diya" if e["type"] == "diya" else "Mila",
                    "Rakam": e["amount"],
                    "Note": e["note"],
                    "Baaki": run_list[i],
                }
                for i, e in enumerate(entries)
            ]
        )
        st.download_button(
            "⬇️ Is khate ki CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{name}_khata.csv",
            mime="text/csv",
        )

    # ---- Person settings ----
    with st.expander("⚙️ Naam badlein / Vyakti hatayein"):
        new_n = st.text_input("Naya naam", value=name, key=f"rename_{name}")
        if st.button("Naam badlein"):
            nn = new_n.strip()
            if not nn:
                st.warning("Naam khaali nahi ho sakta.")
            elif nn != name and (nn in data or nn == HOME):
                st.warning("Ye naam pehle se hai.")
            elif nn != name:
                data[nn] = data.pop(name)
                save_data(data)
                st.session_state.edit = None
                goto(nn)

        st.divider()
        st.caption("Is vyakti ka poora hisab delete ho jayega.")
        with st.popover(f"🗑️ {name} ko hatayein"):
            st.write("Pakka hatana hai? Ye wapas nahi aayega.")
            if st.button("Haan, hata do", key="del_person", type="primary"):
                del data[name]
                save_data(data)
                st.session_state.edit = None
                goto(HOME)
