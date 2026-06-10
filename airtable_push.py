# airtable_push.py

import pandas as pd
import requests
from typing import Dict, Any, Iterable, List
from requests.utils import quote
import re

AIRTABLE_MAX_BATCH = 10


def _attach_visit_link(df: pd.DataFrame, visits_link_id: str | None) -> pd.DataFrame:
    if visits_link_id:
        df["Visits"] = [[visits_link_id]] * len(df)
    return df

def _chunks(items: List[Dict[str, Any]], size: int = AIRTABLE_MAX_BATCH):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _to_airtable_date(s):
    dt = pd.to_datetime(s, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.strftime("%Y-%m-%d")


def _to_percent_0_to_1(x):
    if pd.isna(x):
        return None
    try:
        v = float(x)
    except Exception:
        return None
    return v / 100 if v > 1 else v


def _normalize_group_number(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    m = re.search(r"\d+", s)
    return m.group(0) if m else s


def _normalize_text(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    s = re.sub(r"\s+", " ", s)
    if s.lower() in {"nan", "none", "null", ""}:
        return None
    return s


def _normalize_name_title(x):
    s = _normalize_text(x)
    if s is None:
        return None
    return s.title()


def _make_unique_key(*parts):
    clean = []
    for p in parts:
        if p is None:
            clean.append("")
        else:
            clean.append(str(p).strip())
    return "|".join(clean)


def _escape_airtable_str(s: str) -> str:
    # Airtable filterByFormula strings are quoted with single quotes
    # Escape single quotes by backslash
    return str(s).replace("\\", "\\\\").replace("'", "\\'")


def _make_visit_key(farm_name: str, visit_date_yyyy_mm_dd: str) -> str:
    farm_norm = _normalize_name_title(farm_name) or "Unknown Farm"
    date_norm = _to_airtable_date(visit_date_yyyy_mm_dd) if visit_date_yyyy_mm_dd else None
    return _make_unique_key(farm_norm, date_norm)

class AirtableClient:
    def __init__(self, token: str, base_id: str):
        self.base_id = base_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _url(self, table: str) -> str:
        return f"https://api.airtable.com/v0/{self.base_id}/{quote(table, safe='')}"

    def _request(self, method: str, table: str, **kwargs) -> Dict[str, Any]:
        r = requests.request(
            method,
            self._url(table),
            headers=self.headers,
            timeout=30,
            **kwargs,
        )
        r.raise_for_status()
        return r.json()

    def upsert_records(
        self,
        table: str,
        rows: Iterable[Dict[str, Any]],
        merge_fields: List[str],
        typecast: bool = True,
    ):
        recs = [{"fields": r} for r in rows]
        summary = {"ok": 0, "failed": 0, "errors": [], "last_reply": None}

        for batch in _chunks(recs, AIRTABLE_MAX_BATCH):
            payload = {
                "performUpsert": {"fieldsToMergeOn": merge_fields},
                "typecast": typecast,
                "records": batch,
            }
            try:
                data = self._request("PATCH", table, json=payload)
                summary["ok"] += len(batch)
                summary["last_reply"] = data
            except requests.HTTPError as e:
                summary["failed"] += len(batch)
                try:
                    summary["errors"].append(e.response.json())
                except Exception:
                    summary["errors"].append(
                        {"status": e.response.status_code, "text": e.response.text}
                    )

        return summary

    def find_first_record_id(self, table: str, filter_by_formula: str) -> str | None:
        params = {"filterByFormula": filter_by_formula, "maxRecords": 1}
        data = self._request("GET", table, params=params)
        recs = data.get("records", [])
        return recs[0]["id"] if recs else None

    def ensure_farm(self, farms_table: str, farm_name: str) -> str | None:
        farm_norm = _normalize_name_title(farm_name)
        if not farm_norm:
            return None
        formula = f"{{Farm Name}} = '{_escape_airtable_str(farm_norm)}'"
        existing = self.find_first_record_id(farms_table, formula)
        if existing:
            return existing

        payload = {"records": [{"fields": {"Farm Name": farm_norm}}], "typecast": True}
        data = self._request("POST", farms_table, json=payload)
        return data["records"][0]["id"]

    def ensure_visit(self, visits_table: str, farms_table: str, farm_name: str, visit_date: str, program: str = "Demo") -> str | None:
        farm_id = self.ensure_farm(farms_table, farm_name)
        visit_date_norm = _to_airtable_date(visit_date)
        visit_key = _make_visit_key(farm_name, visit_date_norm)
        formula = f"{{Visit Key}} = '{_escape_airtable_str(visit_key)}'"
        existing = self.find_first_record_id(visits_table, formula)
        if existing:
            return existing

        fields = {
            "Visit Key": visit_key,
            "Visit Date": visit_date_norm,
            "Program": program,
        }
        if farm_id:
            fields["Farm"] = [farm_id]

        payload = {"records": [{"fields": fields}], "typecast": True}
        data = self._request("POST", visits_table, json=payload)
        return data["records"][0]["id"]


def _load_sheet(workbook: str, sheet: str) -> pd.DataFrame:
    return pd.read_excel(workbook, sheet_name=sheet, engine="openpyxl")


def prepare_udder_rows(workbook: str, visits_link_id: str | None = None) -> pd.DataFrame:
    df = _load_sheet(workbook, "Udder Hygiene Summary")
    if df.empty:
        return df
    # already has Farm Name + Visit Date from your cleaner
    df["Group Number"] = df.get("Group Number").apply(_normalize_group_number)
    df["Poor Udder Hygiene Percentage"] = df.get("Poor Udder Hygiene Percentage").apply(_to_percent_0_to_1)
    df["Unique Key"] = [
        _make_unique_key(r.get("Farm Name"), _to_airtable_date(r.get("Visit Date")), r.get("Group Number"))
        for _, r in df.iterrows()
    ]
    df = _attach_visit_link(df, visits_link_id)
    return df.where(pd.notnull(df), None)


def prepare_teat_rows(workbook: str, visits_link_id: str | None = None) -> pd.DataFrame:
    df = _load_sheet(workbook, "Teat Hygiene Summary")
    if df.empty:
        return df
    df["Milker Name"] = df.get("Milker Name").apply(_normalize_name_title)
    df["Poor Teat Hygiene"] = df.get("Poor Teat Hygiene").apply(_to_percent_0_to_1)
    df["Unique Key"] = [
        _make_unique_key(r.get("Farm Name"), _to_airtable_date(r.get("Visit Date")), r.get("Milker Name"))
        for _, r in df.iterrows()
    ]
    df = _attach_visit_link(df, visits_link_id)
    return df.where(pd.notnull(df), None)


def prepare_stall_eval_rows(workbook: str, visits_link_id: str | None = None) -> pd.DataFrame:
    df = _load_sheet(workbook, "Stall Evaluation Summary")
    if df.empty:
        return df

    # normalize names
    rename = {}
    for c in df.columns:
        cc = str(c).strip().lower().replace("_", " ")
        if cc == "farm name": rename[c] = "Farm Name"
        elif cc == "visit date": rename[c] = "Visit Date"
        elif cc in ["group", "group number"]: rename[c] = "Group Number"
    df = df.rename(columns=rename)

    if "Group Number" in df.columns:
        df["Group Number"] = df["Group Number"].apply(_normalize_group_number)

    df["Unique Key"] = [
        _make_unique_key(r.get("Farm Name"), _to_airtable_date(r.get("Visit Date")), r.get("Group Number"))
        for _, r in df.iterrows()
    ]
    df = _attach_visit_link(df, visits_link_id)
    return df.where(pd.notnull(df), None)


def prepare_strip_yields_rows(workbook: str, visits_link_id: str | None = None) -> pd.DataFrame:
    df = _load_sheet(workbook, "Strip Yields Summary")
    if df.empty:
        return df

    rename = {}
    for c in df.columns:
        cc = str(c).strip().lower().replace("_", " ")
        if cc == "farm name": rename[c] = "Farm Name"
        elif cc == "visit date": rename[c] = "Visit Date"
        elif cc in ["group", "group number"]: rename[c] = "Group Number"
    df = df.rename(columns=rename)

    if "Group Number" in df.columns:
        df["Group Number"] = df["Group Number"].apply(_normalize_group_number)

    df["Unique Key"] = [
        _make_unique_key(r.get("Farm Name"), _to_airtable_date(r.get("Visit Date")), r.get("Group Number"))
        for _, r in df.iterrows()
    ]
    df = _attach_visit_link(df, visits_link_id)
    return df.where(pd.notnull(df), None)


def prepare_teat_scoring_rows(workbook: str, visits_link_id: str | None = None) -> pd.DataFrame:
    df = _load_sheet(workbook, "Teat Scoring Summary")

    # first 4 rows are summary rows added in Excel; actual header begins row 5 in the workbook.
    df = pd.read_excel(workbook, sheet_name="Teat Scoring Summary", engine="openpyxl", header=4)
    if df.empty:
        return df

    # Normalize column names while preserving readable labels
    df.columns = [str(c).strip() for c in df.columns]

    if "Farm Name" not in df.columns:
        df.insert(0, "Farm Name", None)
    if "Visit Date" not in df.columns:
        df.insert(1, "Visit Date", None)

    # If these are empty because original sheet didn't contain them, fill from rows if possible later.
    if "Milking Uid" in df.columns:
        id_col = "Milking Uid"
    elif "milking_uid" in df.columns:
        id_col = "milking_uid"
    else:
        id_col = None

    def row_key(r):
        return _make_unique_key(
            r.get("Farm Name"),
            _to_airtable_date(r.get("Visit Date")),
            r.get(id_col) if id_col else None,
        )

    df["Unique Key"] = [row_key(r) for _, r in df.iterrows()]
    df = _attach_visit_link(df, visits_link_id)
    return df.where(pd.notnull(df), None)


def df_to_airtable_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    return df.to_dict(orient="records")
