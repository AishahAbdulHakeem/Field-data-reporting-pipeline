import pandas as pd
import streamlit as st

from utils import clean_uploaded_table, dataframe_to_excel_bytes

st.set_page_config(page_title="Field Data Cleaner", page_icon="🧼", layout="wide")

st.title("🧼 Field Data Cleaner")
st.write(
    "Upload one CSV or Excel file. The app standardizes column names, removes completely empty rows, "
    "flags empty cells, previews the cleaned data, and exports a cleaned Excel file."
)

uploaded_file = st.file_uploader("Upload one CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    try:
        cleaned_df, summary = clean_uploaded_table(uploaded_file)

        st.success("File cleaned successfully.")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Original Rows", summary["original_rows"])
        col2.metric("Rows After Cleaning", summary["cleaned_rows"])
        col3.metric("Empty Rows Removed", summary["removed_empty_rows"])
        col4.metric("Rows With Empty Cells", summary["rows_with_empty_cells"])

        st.subheader("Cleaned Data Preview")
        st.dataframe(cleaned_df.head(100), use_container_width=True)

        empty_rows = cleaned_df[cleaned_df["Has Empty Cells"] == True]
        if not empty_rows.empty:
            with st.expander(f"Rows flagged with empty cells ({len(empty_rows)})", expanded=False):
                st.dataframe(empty_rows, use_container_width=True)
        else:
            st.info("No empty cells were found after removing fully empty rows.")

        output_bytes = dataframe_to_excel_bytes(cleaned_df)
        output_name = uploaded_file.name.rsplit(".", 1)[0] + "_cleaned.xlsx"

        st.download_button(
            "⬇️ Download Cleaned Excel File",
            data=output_bytes,
            file_name=output_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as exc:
        st.error(f"Could not clean file: {exc}")
else:
    st.info("Upload a single CSV or Excel file to begin.")
