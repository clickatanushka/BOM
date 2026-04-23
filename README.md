# BOM → Quotation Tool

An AI-powered quotation generator for PCB assembly. Upload a Bill of Materials (BOM) Excel file and get a professional PDF/Excel quotation automatically — with cost calculation, margin, VAT, and mismatch checking built in.

---

## What It Does

- Parses BOM files (.xlsx, .xls, .csv)
- Detects SMT vs THT components automatically
- Checks if reference count matches declared quantity (mismatch detection)
- Calculates assembly costs (SMT, THT, programming, setup, QA, order processing)
- Adds margin and VAT
- Exports a professional PDF or Excel quotation

---

## Tech Stack

| Layer    | Technology          |
|----------|---------------------|
| Backend  | Python, FastAPI      |
| Parser   | pandas, openpyxl    |
| PDF      | ReportLab           |
| Frontend | React, Vite         |
| API      | REST (JSON)         |

---

## Project Structure

```
bom_quotation_tool/
├── backend/
│   ├── main.py              # FastAPI app — all API endpoints
│   ├── bom_parser.py        # Reads and parses BOM Excel/CSV files
│   ├── cost_engine.py       # Calculates SMT/THT/setup/QA/margin/VAT costs
│   ├── quote_generator.py   # Builds the quotation data model
│   ├── pdf_exporter.py      # Generates PDF using ReportLab
│   ├── excel_exporter.py    # Generates Excel with 2 sheets
│   ├── config.py            # Default cost configuration (Pydantic model)
│   ├── test_pipeline.py     # CLI test — run without the UI
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── index.html           # App entry point
    ├── package.json         # Node dependencies
    ├── vite.config.js       # Vite config + API proxy
    └── src/
        ├── main.jsx         # React entry point
        ├── App.jsx          # Main app component
        ├── api.js           # All API calls in one place
        ├── styles.css       # Global styles
        └── components/
            ├── DropZone.jsx       # File upload area
            ├── BOMTable.jsx       # Parsed BOM table with mismatch highlights
            ├── CostConfig.jsx     # Sidebar — all editable cost fields
            ├── MismatchBanner.jsx # Warning banner for qty mismatches
            └── QuotePreview.jsx   # Live HTML preview of the quotation
```

---

## Prerequisites

Install these before anything else:

| Tool       | Version  | Download                        |
|------------|----------|---------------------------------|
| Python     | 3.12+    | https://python.org              |
| Node.js    | 18+      | https://nodejs.org              |
| Git        | any      | https://git-scm.com             |
| VS Code    | any      | https://code.visualstudio.com   |

Check they are installed:
```bash
python --version
node --version
npm --version
git --version
```

---

## Setup — Step by Step

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOURUSERNAME/bom-quotation-tool.git
cd bom-quotation-tool
```

---

### Step 2 — Set up the Backend

```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate it:
```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

You should see `(venv)` in your terminal.

Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> If you are on Python 3.14+ and pandas fails to install, run:
> ```bash
> pip install pandas --pre
> ```

---

### Step 3 — Test the Backend (no UI needed)

Run the pipeline test with your BOM file:
```bash
python test_pipeline.py "/path/to/your_bom.xlsx"
```

Expected output:
```
[1] Parsing BOM: your_bom.xlsx
  ✓ 27 component types parsed
  ✓ SMT qty: 28  |  THT qty: 5
  ✓ Mismatches: 0

[2] Calculating costs...
  1. SMT Component Assembly     28 pcs    €  9.80
  ...
  QUOTATION TOTAL               €  617.26

[4] Exporting PDF...
  ✓ PDF saved: test_output_Q-2026-001.pdf

[5] Exporting Excel...
  ✓ Excel saved: test_output_Q-2026-001.xlsx

ALL TESTS PASSED
```

---

### Step 4 — Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

Test it in your browser: http://localhost:8000
You should see: `{"message": "BOM Quotation Tool API", "version": "1.0.0"}`

---

### Step 5 — Set up the Frontend

Open a **new terminal** (keep the backend running in the first one):

```bash
cd frontend
npm install
```

Start the frontend:
```bash
npm run dev
```

You should see:
```
VITE ready in 145ms
➜ Local: http://localhost:5173/
```

---

### Step 6 — Open the App

Open your browser and go to:
```
http://localhost:5173
```

You will see the BOM Quotation Tool with a dark sidebar on the left and upload area on the right.

---

## Every Time You Work On It

You need **2 terminals** open at the same time:

**Terminal 1 — Backend:**
```bash
cd bom_quotation_tool/backend
source venv/bin/activate        # Mac/Linux
# or
venv\Scripts\activate           # Windows

uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd bom_quotation_tool/frontend
npm run dev
```

Then open **http://localhost:5173**

---

## How to Use the App

1. Fill in your **company details** in the left sidebar
2. Adjust **assembly costs** (SMT rate, THT rate, hourly rate, etc.)
3. Set your **margin %** and **VAT %**
4. **Drag and drop** your BOM `.xlsx` file into the upload area
5. The app will:
   - Parse all components
   - Show SMT/THT counts
   - Highlight any mismatches in red
6. Click **Export PDF Quotation** or **Export Excel Quotation**
7. The file downloads automatically

---

## BOM File Format

Your BOM file must have these columns (names can vary — the parser auto-detects them):

| Column      | Required | Examples of accepted names                          |
|-------------|----------|-----------------------------------------------------|
| Position    | No       | Pos, Pos., Position, Item                           |
| Reference   | Yes      | Reference, Ref, Referenz, Designator, Referenz-US   |
| Quantity    | Yes      | Qty, Qty., Quantity, Menge, Anzahl                  |
| Description | No       | Text, Description, Bezeichnung, Value               |
| Manufacturer| No       | Manufacturer, Hersteller, Mfr                       |
| MPN         | No       | MPN, Part Number, Teilenummer                       |

The header row can be anywhere in the first 15 rows — the parser scans and finds it automatically.

---

## Mismatch Detection

The app counts the number of references in each cell and compares to the declared quantity:

```
Reference cell:  "C1, C2, C3"   → 3 items counted
Declared Qty:     4
Result:           ✗ MISMATCH — difference of -1
```

### How to fix a mismatch:

| Situation | Fix |
|---|---|
| Reference is missing a component | Add the missing ref to the reference cell |
| Qty is wrong | Correct the Qty in your BOM file |
| Component was removed but ref not deleted | Remove the ref from the cell |

The app still generates the quotation even with mismatches — it uses the declared Qty for cost calculation. Mismatches are warnings only.

---

## SMT vs THT Detection

Components are classified by their reference prefix:

| Prefix | Type | Examples |
|--------|------|---------|
| C      | SMT  | C1, C2, C47 |
| R      | SMT  | R1, R10 |
| U      | SMT  | U1, U3 |
| Q      | SMT  | Q1, Q2 |
| D      | SMT  | D1, D4 |
| L      | SMT  | L1, L2 |
| J      | THT  | J1, J2 |
| P      | THT  | P1 |
| SW     | THT  | SW1, SW2 |
| BT     | THT  | BT1 |
| CN     | THT  | CN1 |

To customize this list, open `backend/bom_parser.py` and edit:
```python
THT_PREFIXES = {"J", "P", "CN", "TB", "BT", "TR"}
```

---

## Cost Configuration

All costs are editable in the sidebar and sent to the backend with each request:

| Field | Default | Description |
|---|---|---|
| SMT cost/pcs | €0.35 | Per SMT component placed by machine |
| THT cost/pcs | €0.65 | Per THT component hand soldered |
| Setup hours | 3 hrs | Machine setup and material preparation |
| Hourly rate | €70 | Rate for engineer hours |
| QA hours | 2 hrs | Quality verification time |
| Programming | €1.00 | Firmware programming per unit |
| Order processing | €60 | Flat fee for order handling |
| QA documentation | €0 | Optional quality docs cost |
| Margin % | 15% | Profit margin added to net cost |
| VAT % | 19% | Tax added to net + margin |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/parse` | Upload and parse a BOM file |
| POST | `/api/generate?filename=X` | Generate PDF or Excel quotation |
| GET | `/api/default-config` | Get default cost configuration |

API docs available at: http://localhost:8000/docs

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `Could not find Reference or Qty columns` | Column headers not recognized | Add your column name to `COLUMN_ALIASES` in `bom_parser.py` |
| `pandas install fails` | Python version too new | Run `pip install pandas --pre` |
| `White blank page` | `index.html` in wrong folder | Copy it from `public/` to `frontend/` root |
| `404 on API calls` | Backend not running | Start `uvicorn main:app --reload --port 8000` |
| `CORS error` | Frontend URL not whitelisted | Add your URL to `allow_origins` in `main.py` |
| `0 components parsed` | Wrong file path or wrong sheet | Check sheet name is `BOM` or parser reads first sheet |

---

## Future Features (Roadmap)

- [ ] Component price lookup via Octopart / Mouser API
- [ ] Multi-board quantity (price for 10 boards, 50 boards, etc.)
- [ ] Customer login and quote history
- [ ] Email quotation directly to customer
- [ ] Supplier comparison (cheapest MPN across distributors)
- [ ] Save and edit quotes before sending

---

## Author

Built as Project 1 of the AI Tools Knowledge Base.
Stack: Python · FastAPI · React · ReportLab · pandas · openpyxl
