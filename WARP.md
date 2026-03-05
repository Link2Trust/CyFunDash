# CyFun Dashboard — Project Rules

## Project Overview
CyFun® 2025 CyberFundamentals Self-Assessment Dashboard. A vanilla HTML/CSS/JS web app with a Python data parser and HTTP server. No frameworks, no build step.

## Key Files
- `parse_excel.py` — Reads the Excel workbook, outputs `data.json`. Depends on `openpyxl`.
- `data.json` — Generated file. Never edit manually; regenerate with `python3 parse_excel.py`.
- `index.html` — Controls page (~36 KB, single-file with embedded CSS and JS).
- `summary.html` — Summary dashboard (~24 KB, single-file with embedded CSS and JS).
- `server.py` — Python HTTP server on port 8088. Serves static files + `POST /save` endpoint.
- `scores.json` — Persisted assessment state (scores + assurance level). Written by server.

## Conventions
- **reqId format**: `"FUNCTION-catIdx-subIdx-reqIdx"` (e.g. `"GOVERN-0-1-3"`). Used as keys in the scores object and as DOM element ID suffixes.
- **Assurance levels**: Basic (1), Important (2), Essential (3). Selection is cumulative.
- **Maturity values**: `'0'` = N/A, `'1'`–`'5'` = maturity levels. Stored as strings in the scores object.
- **N/A default**: Unscored controls default to effective score of 1.
- **Scoring**: Subcategory = min of requirements. Category = average of subcategories. Total = average of categories. KM score = min(doc, impl).
- **Level-dependent targets**: Basic (total: 2.5, category: 2.5), Important (total: 3, category: 3), Essential (total: 3.5, category: 3).

## Development
- Start server: `python3 server.py` (port 8088).
- All CSS and JS are inline in the HTML files — there are no external stylesheets or script files.
- State is dual-written to `localStorage` and `POST /save` (debounced 500ms). Both pages load from `scores.json` first, falling back to `localStorage`.
- The source Excel file is `CyFun2025_Self-Assessment_tool_ESSENTIAL_v3.1.xlsx`.

## Testing
- No test framework. Verify JS syntax with: `sed -n '/<script>/,/<\/script>/p' <file> | sed '1d;$d' > /tmp/check.js && node --check /tmp/check.js`
- Manual browser testing at `http://localhost:8088`.
