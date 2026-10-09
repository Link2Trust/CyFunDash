# Core Components

The project is a single-page-style web dashboard consisting of 7 files (one offline data pipeline script and 6 runtime files), plus the source Excel file and Docker deployment assets at the project root:

**1. parse_excel.py** — Data Extraction Pipeline

- Responsibility: Offline ETL script that reads the CyFun2025 Excel workbook and produces data.json.
- Key functions:
	- parse_function_sheet(ws) — Iterates rows of the 6 NIST CSF function sheets (GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND, RECOVER), extracting a hierarchy of categories → subcategories → requirements. Detects key measures via "Key Measure" text in column C.
	- parse_summary(wb) — Reads the "ESSENTIAL Summary" sheet for the 22 category target maturities (rows 5–26, identified by a trailing category code such as `(GV.OC)`), the target total maturity (cell H4), and the 29 key measures from 3 column groups (L-N, S-U, Z-AB). Uses a regex pattern (^[A-Z]{2}\.[A-Z]{2}-\d) to filter header rows from actual KM codes.
	- _normalize_km_code(code) — Corrects a typo in the source workbook (`ID.AM-03-3` → `ID.AM-03.3`) so every key-measure code can be matched to its requirement.
	- parse_maturity_levels(wb) — Extracts the 5 maturity level definitions with documentation/implementation descriptions.
- Dependency: openpyxl
- Output: data.json (~111 KB) — a flat JSON structure with functions, summary, key_measures, maturity_levels, statistics, and assurance_levels.

**2. utils.js** — Shared Module

- Responsibility: Pure helper functions shared between `index.html` and `summary.html` via ES module import (`import { ... } from './utils.js'`).
- Exports: `avgOrNull(arr)`, `escapeHtml(str)` (pure string escaping of `& < > " '`, safe for HTML content and attribute values), `effectiveScore(scores, reqId, type)` (N/A or invalid → 1), `collectSubScores(sub, fnName, ci, si, maxLevel, ctx)` — the last being the scoring engine used by both pages.

**3. disclaimer.html** — Disclaimer & User Guide

- Responsibility: Static informational page. No JavaScript. Displays the tool disclaimer, CCB/CyFun framework description, and 8 numbered directions for use (assurance levels, structure, assessment method, scoring, summary, features, excluded measures, management aspects).
- Navigation: Links to index.html and summary.html via shared header nav.

**4. index.html** — Controls Page

- Responsibility: Interactive assessment interface where users assign maturity scores per control.
- Key JS functions:
	- init() (async) — Bootstraps the page: loads saved scores, renders stats/functions, restores assurance level.
	- loadScores() (async) — Loads state from scores.json (server file) first, falls back to localStorage.
	- saveScores() / saveToServer() — Dual-write to localStorage + debounced POST /save (500ms).
	- setScore(reqId, type, value) — Updates a single doc/impl score, persists, re-renders.
	- updateAllScores() — Recalculates all subcategory (min) and category (average) scores, updating DOM elements.
	- applyFilters() — Applies assurance level, key-measures-only, management-aspects-only, and search text filters; hides non-matching controls via CSS class toggling. Search matches the requirement text plus its subcategory code/description (same rule as `matchesSearch()` used for the counts).
	- toggleKeyMeasures() / toggleManagementAspects() — Toggle KM/MA filter state, re-run applyFilters() and renderStats().
	- MA_CODES — Constant Set of 15 management aspect requirement codes. isManagementAspect(req) checks membership.
	- renderFunctions() — Builds the full DOM tree: collapsible function sections → categories → subcategories → requirement rows with maturity dropdowns.
- reqId convention: "FUNCTION-catIdx-subIdx-reqIdx" (e.g. "GOVERN-0-1-3") used as the universal key for scores.

**5. summary.html** — Summary/Dashboard Page

- Responsibility: Read-only dashboard showing aggregate maturity scores, threshold compliance, and key measure status.
- Key JS functions:
	- computeCategoryScores() — Walks all functions/categories/subcategories, filters by assurance level, computes subcategory scores (min of requirements), category scores (average of subcategories), and overall category score (min of doc, impl).
	- renderOverview() — Computes total maturity (average of all category scores), renders the SVG circular gauge, and evaluates three threshold checks (KM ≥ target, category ≥ target, total ≥ target).
	- renderKeyMeasures() — Groups KMs by function (GOVERN→RECOVER order), filters by assurance level, renders scores.
   	- computeFunctionScores() / renderRadarChart() — Averages category doc/impl/target scores per function and draws the Function Maturity Radar as inline SVG (documentation, implementation, and dashed target polygons).
	- findReqId(kmCode) — Resolves a key-measure code (e.g. `PR.AA-01.1`) to its reqId via an exact-match lookup built once from `data.json` (`buildReqIdLookup()`).
	- isReqInLevel(reqId) / getReqData(reqId) — Helper to resolve a reqId back to its requirement object and check assurance level membership.
- Level-dependent targets via LEVEL_TARGETS constant: Basic (total: 2.5, category: 2.5), Important (total: 3, category: 3), Essential (total: 3.5, category: 3).

**6. server.py** — Custom HTTP Server

- Responsibility: Static file serving + single POST /save endpoint for score persistence.
- Extends SimpleHTTPRequestHandler with a CyFunHandler class.
- Validates incoming JSON (object with an object `scores` and a `level` of Basic/Important/Essential; body ≤ 5 MB; 400/413 otherwise), then writes it to scores.json in place (no rename, so single-file Docker bind mounts work). Unknown POST paths return 404.
- Configured via `HOST` (default `127.0.0.1`) and `PORT` (default `8088`) environment variables. The Dockerfile sets `HOST=0.0.0.0`.
- Sends `Cache-Control: no-cache` on all responses and suppresses 2xx/3xx request logging.

**7. scores.json** — Persisted State

- Structure: { "scores": { "<reqId>": { "doc": "<0-5>", "impl": "<0-5>" }, ... }, "level": "<Basic|Important|Essential>" }
- Written by server.py on POST /save, read by both HTML pages on load.


# Component Interactions

Excel file ──[parse_excel.py]──► data.json (static, one-time)
                                   │
                                   ▼
          ┌──────────── GET /data.json ────────────┐
          │                                        │
     index.html                              summary.html
     (Controls)                              (Summary)
          │                                        │
          ├── GET /scores.json (on load) ◄─────────┤
          ├── POST /save (on every change) ──► server.py ──► scores.json
          └── localStorage (fallback r/w) ─────────┘

- Data flow: parse_excel.py is run once to generate data.json. Both pages fetch data.json at startup for the control hierarchy and metadata.
- State sharing: The Controls page writes scores + level to both localStorage and POST /save. The Summary page reads from scores.json (with ?_=timestamp cache-bust) on load, falling back to localStorage. There is no live sync between the two pages — the Summary page reflects whatever was last saved when it was loaded.
- No framework: Pure vanilla HTML/CSS/JS. No build step, no bundling, no templating engine.


# Deployment Architecture

**Option A — Docker (recommended for distribution)**
- Requires Docker Desktop.
- `docker compose up --build -d` (run from project root) — `Dockerfile`, `docker-compose.yml`, and `.dockerignore` are at the project root. Builds a Python 3.12-slim image, copies runtime files only, starts on port 8088 (`HOST=0.0.0.0`).
- `scores.json` is bind-mounted for persistence across container restarts. The file must exist on the host beforehand, otherwise Docker creates a directory in its place.
- For end-user distribution, export image as `cyfundash.tar.gz` and provide `docker/INSTALL.md`.

**Option B — Local Python**
- Python 3.x with openpyxl (`pip install openpyxl`).
- Run `python3 parse_excel.py` to generate `data.json`, then `python3 server.py`.
- Open http://localhost:8088 in a browser. The server listens on localhost only unless `HOST` is set (e.g. `HOST=0.0.0.0 python3 server.py`).

No build step, no framework. The entire application is a set of static files served by a single-file Python HTTP server. The server's only dynamic behavior is the POST /save endpoint. There is no database — scores.json is the sole persistence mechanism.


# Runtime Behavior

**Initialization (Controls page)**

1. Browser loads index.html, which fetches data.json.
2. init() (async) calls loadScores() — attempts GET /scores.json first; on 404 or error, reads localStorage.
3. Restores assurance level from the saved state (scores.json, mirrored into localStorage) or defaults to Essential.
4. renderFunctions() builds the full DOM tree from data.json.
5. setLevel() applies the cumulative assurance level filter, triggering applyFilters() and renderStats().

# User interaction

- Score change: Dropdown onchange → setScore() → updates scores object → saveScores() (writes localStorage + debounced POST /save) → updateAllScores() recalculates all subcategory/category scores and updates DOM.
- Filter change: Level buttons / KM toggle / MA toggle / search input → applyFilters() → iterates all requirement DOM nodes, toggling .filtered-out CSS class. Empty subcategories, categories, and function sections are also hidden.

# Initialization (Summary page)

1. Fetches data.json, then loadSaved() fetches scores.json (or falls back to localStorage).
2. computeCategoryScores() walks the full hierarchy, filtering by assurance level.
3. renderCategoryTable(), renderKeyMeasures(), renderOverview(), renderRadarChart() build the dashboard sections (category table, key measures table, gauge + thresholds, radar chart).
4. All computation is client-side; the summary page is fully read-only.

# Error handling

- Fetch failures show inline error messages in the DOM (red text in the main content area or table body).
- POST /save failures are silently caught (catch(() => {})) — localStorage acts as the safety net.
- Invalid /save payloads return HTTP 400 (or 413 if too large) and I/O errors return HTTP 500, all with a JSON error body.

	
