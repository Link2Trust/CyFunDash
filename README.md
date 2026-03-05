# CyFun® 2025 CyberFundamentals Dashboard

A web-based self-assessment tool for the **CyFun® 2025 CyberFundamentals** framework. It parses the official Excel workbook and provides an interactive dashboard to assign maturity scores per control and track compliance against assurance level thresholds.

## <span style="color:green">Features</span>

- **Controls page** — Browse all requirements across the 6 NIST CSF functions (GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND, RECOVER), filter by assurance level (Basic/Important/Essential), toggle key measures only, and search.
- **Maturity scoring** — Assign Documentation and Implementation maturity levels (N/A, 1–5) per control. Subcategory scores (min), category scores (average), and overall maturity are calculated automatically.
- **Summary dashboard** — Circular gauge for total maturity, threshold compliance checks, category maturity table grouped by function, and key measures table grouped by function.
- **Level-dependent targets** — Thresholds adapt to the selected assurance level:
  - Basic: total ≥ 2.5, category/KM ≥ 2.5
  - Important: total ≥ 3, category/KM ≥ 3
  - Essential: total ≥ 3.5, category/KM ≥ 3
- **Auto-save** — Scores are persisted to `scores.json` on disk (debounced) and to `localStorage` as fallback.

## Prerequisites

- Python 3.x
- `openpyxl` library

```bash
pip install openpyxl
```

## Setup

1. Place the Excel source file in the project directory:
   ```
   CyFun2025_Self-Assessment_tool_ESSENTIAL_v3.1.xlsx
   ```

2. Generate the data file:
   ```bash
   python3 parse_excel.py
   ```
   This produces `data.json` (~111 KB) containing all requirements, categories, key measures, and maturity level definitions.

3. Start the server:
   ```bash
   python3 server.py
   ```
   The dashboard is available at `http://localhost:8088`.

## Project Structure

```
cyfundash/
├── CyFun2025_Self-Assessment_tool_ESSENTIAL_v3.1.xlsx  # Source Excel workbook
├── parse_excel.py      # ETL: Excel → data.json
├── data.json           # Generated structured data (do not edit manually)
├── server.py           # HTTP server with POST /save endpoint
├── index.html          # Controls page (interactive scoring)
├── summary.html        # Summary dashboard (read-only)
├── scores.json         # Auto-saved assessment state
├── README.md
└── WARP.md
```

## Architecture

- **No build step** — Pure vanilla HTML/CSS/JS, no frameworks or bundlers.
- **Data pipeline** — `parse_excel.py` reads 6 function sheets + the ESSENTIAL Summary sheet using `openpyxl`, producing a single `data.json`.
- **Server** — `server.py` extends Python's `SimpleHTTPRequestHandler` with a `POST /save` endpoint that writes `scores.json` to disk.
- **State management** — Both pages load from `scores.json` (with cache-bust) on startup, falling back to `localStorage`. The Controls page writes to both on every change (debounced 500ms for server writes).
- **reqId convention** — Each requirement is identified as `"FUNCTION-catIdx-subIdx-reqIdx"` (e.g. `"GOVERN-0-1-3"`), used as the key in the scores object.

## Scoring Logic

- **Requirement score**: Selected maturity level (1–5). N/A defaults to 1.
- **Subcategory score**: Minimum of its requirements' effective scores (doc and impl separately).
- **Category score**: Average of subcategory scores (doc and impl separately). Overall = min(doc, impl).
- **Total maturity**: Average of all category scores.
- **Key measure score**: min(doc, impl) for that requirement.

## Usage Notes

- The assurance level selector is **cumulative** — selecting "Important" includes both Basic and Important controls.
- Scores and the selected assurance level are shared between the Controls and Summary pages via `scores.json`.
- Re-run `python3 parse_excel.py` if the source Excel file is updated.
