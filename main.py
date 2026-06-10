import os
import re
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import streamlit as st

from utils import clean_basic, write_sheet

BASE_CLEAN_DIR = "Cleaned"
os.makedirs(BASE_CLEAN_DIR, exist_ok=True)


def parse_zip_name(zip_filename: str):
    """Parse ZIP names like Farm_Name_YYYYMMDD.zip into farm name and visit date."""
    stem = Path(zip_filename).stem
    match = re.match(r"^(?P<farm>.+)_(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})$", stem)
    if not match:
        return "Demo Farm", pd.Timestamp.today().strftime("%Y-%m-%d")

    farm_name = match.group("farm").replace("_", " ").title()
    visit_date = f"{match.group('yyyy')}-{match.group('mm')}-{match.group('dd')}"
    return farm_name, visit_date


def detect_workflow(file_name: str) -> str:
    """Detect workflow type from a file name."""
    name = file_name.lower()
    if "udder" in name:
        return "Udder Hygiene"
    if "teat" in name and "scor" in name:
        return "Teat Scoring"
    if "teat" in name:
        return "Teat Hygiene"
    if "stall" in name:
        return "Stall Evaluation"
    if "strip" in name or "yield" in name:
        return "Strip Yields"
    return "General Cleaned Data"


def clean_uploaded_file(file_path: str, farm_name: str, visit_date: str):
    """Clean a file and return workflow name plus cleaned dataframe."""
    workflow = detect_workflow(Path(file_path).name)
    df = clean_basic(file_path, farm_name, visit_date)
    df["Source File"] = Path(file_path).name
    df["Workflow"] = workflow
    return workflow, df


def process_zip(uploaded_zip) -> tuple[str, list[tuple[str, pd.DataFrame]], list[str]]:
    farm_name, visit_date = parse_zip_name(uploaded_zip.name)
    safe_visit = visit_date.replace("-", "_")
    output_workbook = os.path.join(BASE_CLEAN_DIR, f"{farm_name} {safe_visit} Cleaned Summary.xlsx")
    processed = []
    errors = []

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, uploaded_zip.name)
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp)

        files = [
            os.path.join(root, file_name)
            for root, _, file_names in os.walk(tmp)
            for file_name in file_names
            if file_name.lower().endswith((".csv", ".xlsx", ".xls"))
        ]

        if not files:
            errors.append("No CSV or Excel files were found in the uploaded ZIP.")
            return output_workbook, processed, errors

        for file_path in files:
            try:
                workflow, df = clean_uploaded_file(file_path, farm_name, visit_date)
                sheet_name = workflow
                write_sheet(df, output_workbook, sheet_name)
                processed.append((workflow, df))
            except Exception as exc:
                errors.append(f"Could not process {Path(file_path).name}: {exc}")

    return output_workbook, processed, errors


st.set_page_config(page_title="Field Data Reporting Pipeline", page_icon="🧼", layout="wide")

st.title("🧼 Field Data Reporting Pipeline")
st.write(
    "Upload a ZIP of raw CSV or Excel files. The app cleans the files, adds visit metadata, "
    "standardizes columns, previews the cleaned data, and generates a downloadable Excel workbook."
)

uploaded_zip = st.file_uploader("Upload a ZIP file", type="zip")

if uploaded_zip:
    with st.spinner("Cleaning uploaded files..."):
        output_workbook, processed, errors = process_zip(uploaded_zip)

    if errors:
        st.warning("Some files could not be processed.")
        for error in errors:
            st.write(f"- {error}")

    if processed:
        st.success(f"Processed {len(processed)} file(s).")

        for workflow, df in processed:
            with st.expander(f"Preview: {workflow} ({len(df)} rows)", expanded=False):
                st.dataframe(df.head(50), use_container_width=True)

        with open(output_workbook, "rb") as f:
            st.download_button(
                "⬇️ Download Cleaned Excel Workbook",
                data=f.read(),
                file_name=os.path.basename(output_workbook),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
else:
    st.info("Upload a ZIP file to begin. For best results, name it like `Demo_Farm_20250601.zip`.")
