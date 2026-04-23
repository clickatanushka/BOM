import pandas as pd
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BOMRow:
    pos: float
    reference: str
    declared_qty: int
    actual_ref_count: int
    description: str
    manufacturer: Optional[str] = None
    mpn: Optional[str] = None
    is_smt: bool = True  # False = THT
    qty_match: bool = True
    mismatch_diff: int = 0


@dataclass
class ParsedBOM:
    rows: List[BOMRow] = field(default_factory=list)
    filename: str = ""
    total_smt_qty: int = 0
    total_tht_qty: int = 0
    total_components: int = 0
    mismatch_count: int = 0
    errors: List[str] = field(default_factory=list)


# Columns we try to match — order matters (first match wins)
COLUMN_ALIASES = {
    "pos":   ["pos", "pos.", "position", "item", "no.", "nr", "lfd"],
    "ref":   ["referenz-us (1814a)", "referenz", "reference", "ref", "designator", "refdes", "bauteil"],
    "qty":   ["qty", "qty.", "quantity", "menge", "anzahl", "count"],
    "desc":  ["text", "description", "bezeichnung", "beschreibung", "bauteilbeschreibung", "value"],
    "mfr":   ["manufacturer", "hersteller", "mfr", "vendor"],
    "mpn":   ["mpn", "mfr. part no", "manufacturer part", "teilenummer", "part number"],
}

THT_PREFIXES = {"J", "P", "X", "CN", "TB", "SW", "S", "BT", "F", "TR"}


def count_references(ref_str: str) -> int:
    if not ref_str or str(ref_str).strip() == "":
        return 0
    parts = [r.strip() for r in str(ref_str).split(",") if r.strip()]
    return len(parts)


def is_tht_component(ref: str) -> bool:
    ref = str(ref).strip()
    for prefix in THT_PREFIXES:
        if ref.upper().startswith(prefix):
            return True
    return False


def find_column(df_columns: list, aliases: list) -> Optional[str]:
    cols_lower = {c.lower().strip(): c for c in df_columns}
    for alias in aliases:
        if alias in cols_lower:
            return cols_lower[alias]
    return None


def detect_header_row(raw: list) -> int:
    keywords = {"pos", "pos.", "ref", "qty", "qty.", "menge", "anzahl",
                "referenz", "designator", "description", "text"}
    for i, row in enumerate(raw[:15]):
        row_lower = [str(c).lower().strip() for c in row if c is not None and str(c).strip()]
        if len(set(row_lower) & keywords) >= 2:
            return i
    return 0


def parse_bom(filepath: str, filename: str) -> ParsedBOM:
    result = ParsedBOM(filename=filename)

    try:
        if filename.endswith(".csv"):
            df_raw = pd.read_csv(filepath, header=None)
        else:
            df_raw = pd.read_excel(filepath, header=None, engine="openpyxl")
    except Exception as e:
        result.errors.append(f"Could not read file: {e}")
        return result

    raw = df_raw.values.tolist()
    header_idx = detect_header_row(raw)
    df = pd.DataFrame(raw[header_idx + 1:], columns=raw[header_idx])

    # Clean column names
    df.columns = [str(c).strip() if c is not None else f"col_{i}" for i, c in enumerate(df.columns)]

    # Map columns
    col_pos  = find_column(df.columns, COLUMN_ALIASES["pos"])
    col_ref  = find_column(df.columns, COLUMN_ALIASES["ref"])
    col_qty  = find_column(df.columns, COLUMN_ALIASES["qty"])
    col_desc = find_column(df.columns, COLUMN_ALIASES["desc"])
    col_mfr  = find_column(df.columns, COLUMN_ALIASES["mfr"])
    col_mpn  = find_column(df.columns, COLUMN_ALIASES["mpn"])

    if not col_ref or not col_qty:
        result.errors.append("Could not find Reference or Qty columns. Check column headers.")
        return result

    for _, row in df.iterrows():
        try:
            ref_val = row.get(col_ref, "")
            qty_val = row.get(col_qty, None)
            pos_val = row.get(col_pos, 0) if col_pos else 0

            if pd.isna(ref_val) or str(ref_val).strip() == "":
                continue
            if pd.isna(qty_val):
                continue

            ref_str = str(ref_val).strip().replace("\n", ", ")
            declared_qty = int(float(str(qty_val).replace(",", ".")))
            actual_count = count_references(ref_str)

            if declared_qty <= 0 and actual_count == 0:
                continue

            desc = str(row.get(col_desc, "")).strip().replace("\n", " ")[:120] if col_desc else ""
            mfr  = str(row.get(col_mfr, "")).strip() if col_mfr else None
            mpn  = str(row.get(col_mpn, "")).strip() if col_mpn else None

            tht = is_tht_component(ref_str.split(",")[0].strip())
            match = actual_count == declared_qty
            diff = actual_count - declared_qty

            try:
                pos = float(str(pos_val).strip()) if pos_val else 0
            except Exception:
                pos = 0

            bom_row = BOMRow(
                pos=pos,
                reference=ref_str,
                declared_qty=declared_qty,
                actual_ref_count=actual_count,
                description=desc,
                manufacturer=mfr if mfr and mfr != "nan" else None,
                mpn=mpn if mpn and mpn != "nan" else None,
                is_smt=not tht,
                qty_match=match,
                mismatch_diff=diff,
            )
            result.rows.append(bom_row)

            if not match:
                result.mismatch_count += 1

            if tht:
                result.total_tht_qty += declared_qty
            else:
                result.total_smt_qty += declared_qty

        except Exception as e:
            continue

    result.total_components = len(result.rows)
    return result
