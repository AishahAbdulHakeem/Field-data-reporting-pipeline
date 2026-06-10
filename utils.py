import re
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names into readable title-case labels."""
    df = df.copy()
    df.columns = [
        str(col)
        .strip()
        .replace("_", " ")
        .replace("-", " ")
        .title()
        for col in df.columns
    ]
    return df


def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that are completely empty."""
    return df.dropna(how="all").reset_index(drop=True)


def add_visit_metadata(df: pd.DataFrame, farm_name: str, visit_date: str) -> pd.DataFrame:
    """Attach farm and visit metadata to a cleaned dataset."""
    df = df.copy()
    if "Farm Name" not in df.columns:
        df.insert(0, "Farm Name", farm_name)
    else:
        df["Farm Name"] = df["Farm Name"].fillna(farm_name)

    if "Visit Date" not in df.columns:
        df.insert(1, "Visit Date", visit_date)
    else:
        df["Visit Date"] = df["Visit Date"].fillna(visit_date)
    return df


def read_tabular_file(file_path: str) -> pd.DataFrame:
    """Read CSV or Excel files into a dataframe."""
    suffix = Path(file_path).suffix.lower()
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    if suffix == ".csv":
        for encoding in ["utf-8", "utf-16", "latin1"]:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except UnicodeDecodeError:
                continue
        return pd.read_csv(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def clean_basic(file_path: str, farm_name: str, visit_date: str) -> pd.DataFrame:
    """General cleaning pass used by all demo workflows."""
    df = read_tabular_file(file_path)
    df = remove_empty_rows(df)
    df = standardize_columns(df)
    df = add_visit_metadata(df, farm_name, visit_date)
    return df


def safe_sheet_name(name: str) -> str:
    """Excel sheet names have a 31-character limit and cannot include some symbols."""
    cleaned = re.sub(r"[\\/*?:\[\]]", "", name)
    return cleaned[:31]


def write_sheet(df: pd.DataFrame, workbook_path: str, sheet_name: str) -> None:
    """Write or replace a sheet in an Excel workbook."""
    sheet_name = safe_sheet_name(sheet_name)

    try:
        with pd.ExcelWriter(
            workbook_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace",
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def add_binary_flag(df: pd.DataFrame, source_col: str, output_col: str, positive_values: list) -> pd.DataFrame:
    """Create a 1/0 indicator column from a source column."""
    df = df.copy()
    if source_col in df.columns:
        df[output_col] = df[source_col].apply(lambda x: 1 if x in positive_values else 0)
    return df
