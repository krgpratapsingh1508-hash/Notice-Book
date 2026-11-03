import json
import os
from datetime import date

import pandas as pd
import streamlit as st

DATA_FILE = "khata.json"

st.set_page_config(page_title="Khata Book", page_icon="📒", layout="centered")


# ---------- Data load / save ----------
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
    """Positive = samne wale se lena hai, Negative = mujhe dena hai."""
    total = 0.0
    for e in entries:
        if e["type"] == "diya":
            total += e["amount"]
        else:
            total -= e["amount"]
    return total


def fmt(amount):
    return f"₹{abs(amount):,.2f}"


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# ---------- Sidebar ----------
st.sidebar.title("📒 Khata Book")

with st.sidebar.form("add_person", clear_on_submit=True):
    new_name = st.text_input("Naya vyakti jodein")
    if st.form_submit_button("➕ Jodein"):
        name = new_name.strip()
        if not name:
            st.sidebar.warning("Naam likhiye.")
        elif name in data:
            st.sidebar.warning("Ye naam pehle se hai.")
        else:
            data[name] = []
            save_data(data)
            st.rerun()

page_options = ["🏠 Sabka Hisab"] + sorted(data.keys())
choice = st.sidebar.radio("Kiska khata dekhna hai?", page_options)

st.sidebar.divider()
st.sidebar.download_button(
    "💾 Backup download karein",
    data=json.dumps(data, ensure_ascii=False, indent=2),
    file_name="khata_backup.json",
    mime="application/json",
)
uploaded = st.sidebar.file_uploader("Backup wapas daalein", type="json")
if uploaded is not None and st.sidebar.button("Restore karein"):
    try:
        st.session_state.data = json.load(uploaded)
        save_data(st.session_state.data)
        st.rerun()
    except json.JSONDecodeError:
        st.sidebar.error("File sahi nahi hai.")

# ---------- Home page ----------
if choice == "🏠 Sabka Hisab":
    st.title("🏠 Sabka Hisab")

    if not data:
        st.info("Abhi koi vyakti nahi hai. Sidebar se naya naam jodein.")
    else:
        rows = []
        to_receive = 0.0
        to_pay = 0.0
        for name, entries in data.items():
            b = balance(entries)
            if b > 0:
                to_receive += b
                status = "Mujhe lena hai"
            elif b < 0:
                to_pay += -b
                status = "Mujhe dena hai"
            else:
                status = "Hisab barabar"
            rows.append({"Naam": name, "Status": status, "Rakam (₹)": abs(b)})

        c1, c2 = st.columns(2)
        c1.metric("Kul lena hai", fmt(to_receive))
        c2.metric("Kul dena hai", fmt(to_pay))

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ---------- Person page ----------
else:
    name = choice
    entries = data[name]
    st.title(f"👤 {name}")

    b = balance(entries)
    if b > 0:
        st.success(f"{name} se aapko lena hai: **{fmt(b)}**")
    elif b < 0:
        st.error(f"Aapko {name} ko dena hai: **{fmt(b)}**")
    else:
        st.info("Hisab barabar hai ✅")

    st.subheader("Nayi entry")
    with st.form("add_entry", clear_on_submit=True):
        kind = st.radio(
            "Kya hua?",
            ["Maine paise diye (udhar)", "Mujhe paise mile (wapas / unhone diye)"],
            horizontal=False,
        )
        amount = st.number_input("Rakam (₹)", min_value=0.0, step=10.0, format="%.2f")
        when = st.date_input("Tareekh", value=date.today())
        note = st.text_input("Note (optional)")
        if st.form_submit_button("✅ Save karein"):
            if amount <= 0:
                st.warning("Rakam 0 se zyada honi chahiye.")
            else:
                entries.append(
                    {
                        "date": when.isoformat(),
                        "type": "diya" if kind.startswith("Maine") else "mila",
                        "amount": float(amount),
                        "note": note.strip(),
                    }
                )
                save_data(data)
                st.rerun()

    st.subheader("Hisab ki list")
    if not entries:
        st.caption("Abhi koi entry nahi hai.")
    else:
        running = 0.0
        rows = []
        for i, e in enumerate(entries):
            running += e["amount"] if e["type"] == "diya" else -e["amount"]
            rows.append(
                {
                    "#": i + 1,
                    "Tareekh": e["date"],
                    "Diya (₹)": e["amount"] if e["type"] == "diya" else None,
                    "Mila (₹)": e["amount"] if e["type"] == "mila" else None,
                    "Note": e["note"],
                    "Baaki (₹)": running,
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with st.expander("🗑️ Entry delete karein"):
            idx = st.number_input(
                "Entry number (#)", min_value=1, max_value=len(entries), step=1
            )
            if st.button("Delete"):
                entries.pop(int(idx) - 1)
                save_data(data)
                st.rerun()

    with st.expander("⚠️ Is vyakti ko hatayein"):
        st.write("Iska poora hisab delete ho jayega.")
        if st.button(f"{name} ko hatayein"):
            del data[name]
            save_data(data)
            st.rerun()
