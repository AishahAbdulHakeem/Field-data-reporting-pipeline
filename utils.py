import re
from pathlib import Path
from io import BytesIO

import pandas as pd

FLAG_COLUMNS = ["Has Empty Cells", "Empty Cell Count", "Empty Columns"]


def standardize_column_name(column_name) -> str:
    """Convert any column name into clean Title Case."""
    name = str(column_name).strip()
    name = re.sub(r"[_\-]+", " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.title()


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize all column names into readable Title Case labels."""
    df = df.copy()
    df.columns = [standardize_column_name(col) for col in df.columns]
    return df


def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that are completely empty."""
    return df.dropna(how="all").reset_index(drop=True)


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Read one uploaded CSV or Excel file into a dataframe."""
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(uploaded_file)

    if suffix == ".csv":
        return pd.read_csv(uploaded_file)

    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")


def flag_empty_cells(df: pd.DataFrame) -> pd.DataFrame:
    """Add row-level missing-cell flags without deleting partially complete records."""
    df = df.copy()

    missing_mask = df.isna() | df.astype(str).apply(lambda col: col.str.strip().eq(""))
    df["Has Empty Cells"] = missing_mask.any(axis=1)
    df["Empty Cell Count"] = missing_mask.sum(axis=1)
    df["Empty Columns"] = missing_mask.apply(
        lambda row: ", ".join(row.index[row].astype(str)), axis=1
    )

    return df


def remove_flag_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return cleaned data without internal review/flag columns."""
    return df.drop(columns=[col for col in FLAG_COLUMNS if col in df.columns])


def clean_uploaded_table(uploaded_file) -> tuple[pd.DataFrame, dict]:
    """Run the simplified public cleaning workflow."""
    raw_df = read_uploaded_file(uploaded_file)
    original_rows = len(raw_df)
    original_columns = len(raw_df.columns)

    cleaned_df = remove_empty_rows(raw_df)
    removed_empty_rows = original_rows - len(cleaned_df)

    cleaned_df = standardize_columns(cleaned_df)
    cleaned_df = flag_empty_cells(cleaned_df)

    summary = {
        "original_rows": original_rows,
        "cleaned_rows": len(cleaned_df),
        "removed_empty_rows": removed_empty_rows,
        "original_columns": original_columns,
        "final_columns": len(remove_flag_columns(cleaned_df).columns),
        "rows_with_empty_cells": int(cleaned_df["Has Empty Cells"].sum()) if not cleaned_df.empty else 0,
        "total_empty_cells": int(cleaned_df["Empty Cell Count"].sum()) if not cleaned_df.empty else 0,
    }

    return cleaned_df, summary


def dataframe_to_excel_bytes(df: pd.DataFrame, include_flags: bool = False) -> bytes:
    """Convert dataframe to downloadable Excel bytes.

    By default, review-only flag columns are removed from the exported file.
    """
    export_df = df.copy() if include_flags else remove_flag_columns(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, sheet_name="Cleaned Data", index=False)
    return output.getvalue()
