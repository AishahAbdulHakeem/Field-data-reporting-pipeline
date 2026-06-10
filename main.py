# main.py

import streamlit as st
import os, tempfile, zipfile, re
import pandas as pd
from openpyxl import Workbook

import teat
import udder_hygiene
import teat_hygiene as tt
import stall_eval
import stripyields

from airtable_push import (
    AirtableClient,
    prepare_udder_rows,
    prepare_teat_rows,
    prepare_teat_scoring_rows,
    prepare_stall_eval_rows,
    prepare_strip_yields_rows,
)

# -----------------------------
# Config
# -----------------------------

BASE_CLEAN_DIR = "Cleaned"
os.makedirs(BASE_CLEAN_DIR, exist_ok=True)


# Optional Airtable integration is disabled in the public version.
at = None
VISITS_TABLE = "Visits"
FARMS_TABLE = "Farms"
VISIT_PROGRAM = "DEMO"

# -----------------------------
# Helpers
# -----------------------------

def parse_zip_name(zip_filename: str):
    """
    Expect: Farm_Name_YYYYMMDD.zip
    """
    stem = os.path.splitext(zip_filename)[0]
    m = re.match(r"^(?P<farm>.+)_(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})$", stem)
    if not m:
        return None, None

    farm = m.group("farm").replace("_", " ").title()
    date = pd.to_datetime(
        f"{m.group('yyyy')}-{m.group('mm')}-{m.group('dd')}",
        errors="coerce",
    )
    return farm, date.strftime("%Y-%m-%d") if not pd.isna(date) else None


def fill_visit_date_if_missing(df, visit_date):
    if "Visit Date" not in df.columns:
        df["Visit Date"] = visit_date
    else:
        mask = df["Visit Date"].isna() | (df["Visit Date"].astype(str).str.strip() == "")
        df.loc[mask, "Visit Date"] = visit_date
    return df


# -----------------------------
# App
# -----------------------------

st.title("🧼 Demo Dairy Data Cleaner")

uploaded_zip = st.file_uploader("Upload Farm ZIP", type="zip")

if uploaded_zip:
    farm, visit_date = parse_zip_name(uploaded_zip.name)

    if not farm or not visit_date:
        st.error("ZIP must be named: Farm_Name_YYYYMMDD.zip")
        st.stop()

    safe_visit = visit_date.replace("-", "_")
    output_workbook = os.path.join(BASE_CLEAN_DIR, f"{farm} {safe_visit} Summary.xlsx")

    if not os.path.exists(output_workbook):
        wb = Workbook()
        wb.active.title = "Init"
        wb.save(output_workbook)

    st.success(f"Farm: {farm}")
    st.success(f"Visit Date: {visit_date}")

    # -----------------------------
    # Cleaning pipeline
    # -----------------------------

    with st.spinner("Processing files..."):
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, uploaded_zip.name)
            with open(zip_path, "wb") as f:
                f.write(uploaded_zip.read())

            with zipfile.ZipFile(zip_path) as z:
                z.extractall(tmp)

            files = [
                os.path.join(r, f)
                for r, _, fs in os.walk(tmp)
                for f in fs
                if f.lower().endswith((".csv", ".xlsx", ".xls"))
            ]

            def priority(f):
                n = os.path.basename(f).lower()
                if "udder" in n:
                    return 0
                if "teat scoring" in n or "teat scores" in n:
                    return 1
                if "teat cleanliness" in n:
                    return 2
                if "stall" in n and "evaluation" in n:
                    return 3
                if "strip" in n and "yields" in n:
                    return 4
                return 99

            files.sort(key=priority)

            ts_summaries = []

            for fp in files:
                name = os.path.basename(fp).lower()

                if "udder" in name:
                    udder_hygiene.clean_udder_hygiene(fp, output_workbook, farm, visit_date)

                elif "teat scoring" in name or "teat scores" in name:
                    df = teat.clean_teat_scoring(fp, output_workbook, farm, visit_date)
                    if df is not None:
                        df["Source File"] = os.path.basename(fp)
                        ts_summaries.append(df)

                elif "teat cleanliness" in name:
                    tt.clean_teat_hygiene(fp, output_workbook, farm, visit_date)

                elif "stall" in name and "evaluation" in name:
                    stall_eval.clean_stall_evaluation(fp, output_workbook, farm, visit_date)

                elif "strip" in name and "yields" in name:
                    stripyields.clean_strip_yields(fp, output_workbook, farm, visit_date)

    st.success("Cleaning complete!")

    with open(output_workbook, "rb") as f:
        st.download_button(
            "⬇️ Download Summary Workbook",
            data=f.read(),
            file_name=os.path.basename(output_workbook),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

