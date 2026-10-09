# CyFun Dashboard — Project Rules

## Project Overview
CyFun® 2025 CyberFundamentals Self-Assessment Dashboard. A vanilla HTML/CSS/JS web app with a Python data parser and HTTP server. No frameworks, no build step.

## Key Files
- `parse_excel.py` — Reads the Excel workbook, outputs `data.json`. Depends on `openpyxl`.
- `data.json` — Generated file. Never edit manually; regenerate with `python3 parse_excel.py`.
- `index.html` — Controls page (single-file with embedded CSS and JS).
- `summary.html` — Summary dashboard (single-file with embedded CSS and JS).
- `disclaimer.html` — Disclaimer & User Guide page (static, no JS).
- `utils.js` — Shared pure functions imported by both HTML pages via ES module: `avgOrNull`, `escapeHtml` (string-based, escapes quotes), `effectiveScore(scores, reqId, type)`, `collectSubScores`.
- `server.py` — Python HTTP server (default `127.0.0.1:8088`, override via `HOST`/`PORT` env vars; Docker sets `HOST=0.0.0.0`). Serves static files + validated `POST /save` endpoint.
- `scores.json` — Persisted assessment state (scores + assurance level). Written by server.

## Conventions
- **reqId format**: `"FUNCTION-catIdx-subIdx-reqIdx"` (e.g. `"GOVERN-0-1-3"`). Used as keys in the scores object and as DOM element ID suffixes.
- **Assurance levels**: Basic (1), Important (2), Essential (3). Selection is cumulative.
- **Maturity values**: `'0'` = N/A, `'1'`–`'5'` = maturity levels. Stored as strings in the scores object.
- **N/A default**: Unscored controls default to effective score of 1.
- **Scoring**: Subcategory = min of requirements. Category = average of subcategories. Total = average of categories. KM score = min(doc, impl).
- **Level-dependent targets**: Basic (total: 2.5, category: 2.5), Important (total: 3, category: 3), Essential (total: 3.5, category: 3).
- **Key Measures**: Controls marked as key measures carry a `★ KM` badge. The `keyMeasuresOnly` toggle filters to KM controls only.
- **Management Aspects**: 15 specific controls are tagged as management aspects (`⚙ MA` badge). Defined in `MA_CODES` Set in `index.html`. The `managementAspectsOnly` toggle filters to MA controls only, respecting the assurance level filter. Codes: GV.RM-01.1, GV.RM-02.1, GV.RM-03.2, GV.RR-02.1, GV.RR-02.2, GV.SC-01.1, ID.RA-05.2, ID.RA-05.3, ID.RA-06.1, ID.IM-03.9, ID.IM-04.1, ID.IM-04.2, PR.IR-04.1, DE.AE-04.1, RC.CO-03.1.

## Development
- Start server: `python3 server.py` (port 8088).
- CSS is inline in each HTML file. JS is inline in each HTML file **plus** `utils.js` (shared module, imported via `<script type="module">`).
- State is dual-written to `localStorage` and `POST /save` (debounced 500ms). Both pages load from `scores.json` first, falling back to `localStorage`.
- The source Excel file is `CyFun2025_Self-Assessment_tool_ESSENTIAL_v3.1.xlsx`. `parse_excel.py` normalises the workbook's `ID.AM-03-3` key-measure typo to `ID.AM-03.3`; after changing the parser, re-run it and commit the regenerated `data.json`.
- Key-measure codes are resolved to reqIds by exact code match (`findReqId` in `summary.html`); never use prefix matching (`X.1` vs `X.10`).
- Docker deployment: `docker compose up --build -d` (port 8088). `Dockerfile`, `docker-compose.yml`, `.dockerignore` are at the project root. See `docker/INSTALL.md` for end-user distribution.

## Testing
- No test framework. Verify JS syntax with: `sed -n '/<script/,/<\/script>/p' <file> | sed '1d;$d' | node --input-type=module --check`
- Manual browser testing at `http://localhost:8088`.
