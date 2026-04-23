# BOM → Quotation Tool

AI-powered quotation generator. Upload a BOM Excel file, get a professional PDF quotation.

## Project Structure

```
bom_quotation_tool/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── bom_parser.py        # Parse Excel/CSV BOM files
│   ├── cost_engine.py       # Assembly cost + margin logic
│   ├── quote_generator.py   # Build quotation data model
│   ├── pdf_exporter.py      # Export to PDF
│   ├── excel_exporter.py    # Export to Excel
│   ├── config.py            # Default cost config
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── DropZone.jsx
│   │   │   ├── BOMTable.jsx
│   │   │   ├── CostConfig.jsx
│   │   │   ├── QuotePreview.jsx
│   │   │   └── MismatchBanner.jsx
│   │   ├── api.js
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## How It Works

1. Upload BOM (.xlsx or .csv)
2. Parser extracts: Pos, Reference, Qty, Description
3. Mismatch check: count refs vs declared qty
4. Cost engine calculates assembly costs
5. Export PDF or Excel quotation
