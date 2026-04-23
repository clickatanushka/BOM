from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import Optional
import tempfile, os, json

from config import CostConfig
from bom_parser import parse_bom
from cost_engine import calculate_costs
from quote_generator import build_quotation
from pdf_exporter import export_pdf
from excel_exporter import export_excel

app = FastAPI(title="BOM Quotation Tool API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    config: CostConfig
    recipient_company: Optional[str] = "Recipient GmbH"
    recipient_address: Optional[str] = "Sample Street 123\n12345 Berlin"
    export_format: Optional[str] = "pdf"   # "pdf" or "excel"


class BOMRowOut(BaseModel):
    pos: float
    reference: str
    declared_qty: int
    actual_ref_count: int
    description: str
    is_smt: bool
    qty_match: bool
    mismatch_diff: int


class ParseResponse(BaseModel):
    filename: str
    rows: list[BOMRowOut]
    total_smt_qty: int
    total_tht_qty: int
    total_components: int
    mismatch_count: int
    errors: list[str]


# ── In-memory session store (replace with Redis/DB for production) ─────────────
_bom_cache: dict = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "BOM Quotation Tool API", "version": "1.0.0"}


@app.post("/api/parse", response_model=ParseResponse)
async def parse_bom_file(file: UploadFile = File(...)):
    """Upload a BOM file (xlsx or csv). Returns parsed rows + mismatch check."""
    allowed = {".xlsx", ".xls", ".csv"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}. Use xlsx, xls, or csv.")

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        bom = parse_bom(tmp_path, file.filename)
    finally:
        os.unlink(tmp_path)

    # Cache BOM for later export (keyed by filename for simplicity)
    _bom_cache[file.filename] = bom

    rows_out = [
        BOMRowOut(
            pos=r.pos,
            reference=r.reference,
            declared_qty=r.declared_qty,
            actual_ref_count=r.actual_ref_count,
            description=r.description,
            is_smt=r.is_smt,
            qty_match=r.qty_match,
            mismatch_diff=r.mismatch_diff,
        )
        for r in bom.rows
    ]

    return ParseResponse(
        filename=bom.filename,
        rows=rows_out,
        total_smt_qty=bom.total_smt_qty,
        total_tht_qty=bom.total_tht_qty,
        total_components=bom.total_components,
        mismatch_count=bom.mismatch_count,
        errors=bom.errors,
    )


@app.post("/api/generate")
async def generate_quotation(req: GenerateRequest, filename: str):
    """Generate a quotation PDF or Excel from a previously parsed BOM."""
    bom = _bom_cache.get(filename)
    if not bom:
        raise HTTPException(404, "BOM not found. Please parse a file first via /api/parse.")

    costs = calculate_costs(bom, req.config)
    quote = build_quotation(bom, costs, req.config, req.recipient_company, req.recipient_address)

    if req.export_format == "excel":
        data = export_excel(quote)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="quotation_{req.config.quote_number}.xlsx"'},
        )
    else:
        data = export_pdf(quote)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="quotation_{req.config.quote_number}.pdf"'},
        )


@app.get("/api/default-config")
def get_default_config():
    """Return the default cost configuration."""
    return CostConfig().model_dump()
