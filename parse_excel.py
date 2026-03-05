#!/usr/bin/env python3
"""
Parse the CyFun2025 Self-Assessment Excel file and extract structured data as JSON.
"""

import json
import sys
from pathlib import Path

import openpyxl

EXCEL_FILE = Path(__file__).parent / "CyFun2025_Self-Assessment_tool_ESSENTIAL_v3.1.xlsx"
OUTPUT_FILE = Path(__file__).parent / "data.json"

FUNCTION_SHEETS = ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"]

ASSURANCE_HIERARCHY = {"Basic": 1, "Important": 2, "Essential": 3}


def safe_cell_value(row_tuple, col_index):
    """Safely get a cell value handling merged cells."""
    if col_index >= len(row_tuple):
        return None
    cell = row_tuple[col_index]
    return cell


def parse_function_sheet(ws, sheet_name):
    """Parse a function sheet (GOVERN, IDENTIFY, etc.) and return structured data."""
    categories = []
    current_category = None
    current_subcategory = None

    for row in ws.iter_rows(min_row=3, max_row=ws.max_row, values_only=True):
        col_a = row[0] if len(row) > 0 else None  # Category
        col_c = row[2] if len(row) > 2 else None  # Key Measure flag
        col_d = row[3] if len(row) > 3 else None  # Subcategory
        col_e = row[4] if len(row) > 4 else None  # Assurance level
        col_f = row[5] if len(row) > 5 else None  # Requirement

        # New category
        if col_a and isinstance(col_a, str) and col_a.strip():
            current_category = {
                "name": col_a.strip(),
                "subcategories": [],
            }
            categories.append(current_category)

        # New subcategory
        if col_d and isinstance(col_d, str) and col_d.strip():
            raw_sub = col_d.strip()
            if ":" in raw_sub:
                sub_code, sub_desc = raw_sub.split(":", 1)
                sub_code = sub_code.strip()
                sub_desc = sub_desc.strip()
            else:
                sub_code = raw_sub
                sub_desc = ""

            current_subcategory = {
                "code": sub_code,
                "description": sub_desc,
                "requirements": [],
            }
            if current_category:
                current_category["subcategories"].append(current_subcategory)

        # Requirement row
        if col_e and col_f and isinstance(col_f, str) and col_f.strip():
            is_key_measure = bool(col_c and str(col_c).strip().lower() == "key measure")
            requirement = {
                "assurance_level": col_e.strip() if isinstance(col_e, str) else str(col_e),
                "requirement": col_f.strip(),
                "key_measure": is_key_measure,
            }
            if current_subcategory:
                current_subcategory["requirements"].append(requirement)

    return categories


def parse_maturity_levels(wb):
    """Parse the Maturity Levels sheet."""
    ws = wb["Maturity Levels"]
    levels = []
    for row in ws.iter_rows(min_row=2, max_row=6, values_only=True):
        if row[0] and row[1] is not None:
            levels.append({
                "name": str(row[0]).strip(),
                "value": row[1],
                "documentation": str(row[2]).strip() if row[2] else "",
                "implementation": str(row[3]).strip() if row[3] else "",
            })
    return levels


def parse_summary(wb):
    """Parse the ESSENTIAL Summary sheet for category scores and key measures."""
    ws = wb["ESSENTIAL Summary"]
    categories = []
    current_function = None

    # Row 3 has target total maturity in H
    target_total = None
    for row in ws.iter_rows(min_row=3, max_row=3, values_only=True):
        target_total = row[7] if len(row) > 7 else None  # col H

    for row in ws.iter_rows(min_row=4, max_row=24, values_only=True):
        col_a = row[0] if len(row) > 0 else None
        col_b = row[1] if len(row) > 1 else None
        col_c = row[2] if len(row) > 2 else None

        if col_a and isinstance(col_a, str):
            current_function = col_a.strip()

        if col_b and isinstance(col_b, str) and col_b.strip():
            categories.append({
                "function": current_function,
                "category": col_b.strip(),
                "target_maturity": col_c if col_c else 0,
            })

    # Parse key measures from 3 column groups (L-Q, S-X, Z-AE)
    # Skip header rows by checking for valid requirement codes (e.g. "PR.AA-01.1")
    import re
    km_code_pattern = re.compile(r'^[A-Z]{2}\.[A-Z]{2}-\d')
    key_measures = []
    for row in ws.iter_rows(min_row=26, max_row=ws.max_row, values_only=True):
        # Group 1: L=11, M=12, N=13
        if len(row) > 12 and row[11] and isinstance(row[11], str):
            code = str(row[11]).strip()
            if km_code_pattern.match(code):
                key_measures.append({
                    "code": code,
                    "description": str(row[12]).strip() if row[12] else "",
                    "target_maturity": row[13] if len(row) > 13 and row[13] else 3,
                })
        # Group 2: S=18, T=19, U=20
        if len(row) > 19 and row[18] and isinstance(row[18], str):
            code = str(row[18]).strip()
            if km_code_pattern.match(code):
                key_measures.append({
                    "code": code,
                    "description": str(row[19]).strip() if row[19] else "",
                    "target_maturity": row[20] if len(row) > 20 and row[20] else 3,
                })
        # Group 3: Z=25, AA=26, AB=27
        if len(row) > 26 and row[25] and isinstance(row[25], str):
            code = str(row[25]).strip()
            if km_code_pattern.match(code):
                key_measures.append({
                    "code": code,
                    "description": str(row[26]).strip() if row[26] else "",
                    "target_maturity": row[27] if len(row) > 27 and row[27] else 3,
                })

    return {
        "categories": categories,
        "target_total_maturity": target_total if target_total else 3.5,
        "key_measures": key_measures,
    }


def main():
    print(f"Reading {EXCEL_FILE}...")
    wb = openpyxl.load_workbook(str(EXCEL_FILE), data_only=True)

    data = {
        "title": "CyFun® 2025 CyberFundamentals",
        "assurance_levels": [
            {"name": "Basic", "value": 1, "description": "Basic cybersecurity hygiene"},
            {"name": "Important", "value": 2, "description": "Standard cybersecurity controls"},
            {"name": "Essential", "value": 3, "description": "Advanced cybersecurity requirements"},
        ],
        "maturity_levels": parse_maturity_levels(wb),
        "functions": {},
    }

    summary_data = parse_summary(wb)
    data["summary"] = summary_data["categories"]
    data["target_total_maturity"] = summary_data["target_total_maturity"]
    data["key_measures"] = summary_data["key_measures"]

    for sheet_name in FUNCTION_SHEETS:
        print(f"  Parsing {sheet_name}...")
        ws = wb[sheet_name]
        data["functions"][sheet_name] = parse_function_sheet(ws, sheet_name)

    # Compute statistics
    stats = {}
    for fn_name, categories in data["functions"].items():
        fn_stats = {"Basic": 0, "Important": 0, "Essential": 0, "total": 0}
        for cat in categories:
            for sub in cat["subcategories"]:
                for req in sub["requirements"]:
                    level = req["assurance_level"]
                    if level in fn_stats:
                        fn_stats[level] += 1
                    fn_stats["total"] += 1
        stats[fn_name] = fn_stats
    data["statistics"] = stats

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nData written to {OUTPUT_FILE}")
    total = sum(s["total"] for s in stats.values())
    print(f"Total requirements extracted: {total}")
    for fn, s in stats.items():
        print(f"  {fn}: {s['total']} (Basic: {s['Basic']}, Important: {s['Important']}, Essential: {s['Essential']})")
    print(f"Key measures extracted: {len(data['key_measures'])}")
    print(f"Target total maturity: {data['target_total_maturity']}")


if __name__ == "__main__":
    main()
