# from dataclasses import dataclass, field
# from datetime import date, timedelta
# from typing import List, Optional
# from config import CostConfig
# from bom_parser import ParsedBOM, BOMRow
# from cost_engine import CostBreakdown, LineItem


# @dataclass
# class Quotation:
#     # Header
#     quote_number: str
#     date: date
#     valid_until: date

#     # Parties
#     sender_company: str
#     sender_address: str
#     sender_email: str
#     sender_website: str
#     sender_phone: str
#     sender_hrb: str
#     sender_vat_id: str
#     sender_iban: str
#     sender_bank: str

#     recipient_company: str = "Recipient GmbH"
#     recipient_address: str = "Sample Street 123\n12345 Berlin"

#     # BOM summary
#     bom_filename: str = ""
#     total_component_types: int = 0
#     total_smt_qty: int = 0
#     total_tht_qty: int = 0
#     mismatch_count: int = 0
#     bom_rows: List[BOMRow] = field(default_factory=list)

#     # Costs
#     line_items: List[LineItem] = field(default_factory=list)
#     net_assembly: float = 0.0
#     margin_amount: float = 0.0
#     margin_percent: float = 0.0
#     net_with_margin: float = 0.0
#     vat_amount: float = 0.0
#     vat_percent: float = 0.0
#     grand_total: float = 0.0

#     # Terms
#     payment_terms: str = "Net 14 days from invoice date"


# def build_quotation(
#     bom: ParsedBOM,
#     costs: CostBreakdown,
#     cfg: CostConfig,
#     recipient_company: str = "Recipient GmbH",
#     recipient_address: str = "Sample Street 123\n12345 Berlin",
# ) -> Quotation:
#     today = date.today()
#     valid_until = today + timedelta(days=cfg.validity_days)

#     return Quotation(
#         quote_number=cfg.quote_number,
#         date=today,
#         valid_until=valid_until,
#         sender_company=cfg.company_name,
#         sender_address=cfg.company_address,
#         sender_email=cfg.company_email,
#         sender_website=cfg.company_website,
#         sender_phone=cfg.company_phone,
#         sender_hrb=cfg.company_hrb,
#         sender_vat_id=cfg.company_vat_id,
#         sender_iban=cfg.company_iban,
#         sender_bank=cfg.company_bank,
#         recipient_company=recipient_company,
#         recipient_address=recipient_address,
#         bom_filename=bom.filename,
#         total_component_types=bom.total_components,
#         total_smt_qty=bom.total_smt_qty,
#         total_tht_qty=bom.total_tht_qty,
#         mismatch_count=bom.mismatch_count,
#         bom_rows=bom.rows,
#         line_items=costs.line_items,
#         net_assembly=costs.net_assembly,
#         margin_amount=costs.margin_amount,
#         margin_percent=costs.margin_percent,
#         net_with_margin=costs.net_with_margin,
#         vat_amount=costs.vat_amount,
#         vat_percent=costs.vat_percent,
#         grand_total=costs.grand_total,
#         payment_terms=cfg.payment_terms,
#     )

"""
quote_generator.py — Builds the quotation data model
Matches actual ParsedBOM (bom_parser.py) and CostBreakdown (cost_engine.py) structures.
"""

from datetime import datetime, timedelta
from config import CostConfig


def generate_quote(bom, costs, cfg: CostConfig,
                   customer: dict = None, company: dict = None,
                   prepared_by: str = "Sales Team") -> dict:
    """
    Build a complete quotation dict from:
      bom    — ParsedBOM dataclass (from bom_parser.py)
      costs  — CostBreakdown dataclass (from cost_engine.py)
      cfg    — CostConfig pydantic model (from config.py)

    Returns a dict ready for pdf_exporter.export_pdf()
    """

    # ── Line items from BOMRow objects ────────────────────────────────────────
    line_items = []
    for i, row in enumerate(bom.rows):
        line_items.append({
            "position":     row.pos if row.pos else i + 1,
            "reference":    row.reference,
            "description":  row.description,
            "manufacturer": row.manufacturer or "",
            "mpn":          row.mpn or "",
            "quantity":     row.declared_qty,
            "unit_price":   0.0,   # internal only — NOT printed in PDF
            "total":        0.0,   # component prices not tracked here
            "type":         "THT" if not row.is_smt else "SMT",
            "mismatch":     not row.qty_match,
        })

    # ── Cost breakdown from CostBreakdown object ──────────────────────────────
    # We build it from costs.line_items if available, else reconstruct from cfg
    cost_breakdown = []

    if hasattr(costs, "line_items") and costs.line_items:
        for item in costs.line_items:
            # LineItem may be a dataclass or dict
            if hasattr(item, "label"):
                label  = item.description
                amount = item.amount
            else:
                label  = item.get("description", "")
                amount = item.get("amount", 0.0)
            if amount > 0:
                cost_breakdown.append({"label": label, "amount": amount})
    else:
        # Fallback: reconstruct from cfg + bom quantities
        smt = bom.total_smt_qty
        tht = bom.total_tht_qty
        entries = [
            (f"SMT Component Assembly ({smt} pcs × €{cfg.smt_cost_per_pcs:.2f})",
             smt * cfg.smt_cost_per_pcs),
            (f"THT Component Assembly ({tht} pcs × €{cfg.tht_cost_per_pcs:.2f})",
             tht * cfg.tht_cost_per_pcs),
            (f"Machine Setup ({cfg.setup_hours} hrs × €{cfg.hourly_rate:.2f}/hr)",
             cfg.setup_hours * cfg.hourly_rate),
            (f"Quality Assurance ({cfg.qa_hours} hrs × €{cfg.hourly_rate:.2f}/hr)",
             cfg.qa_hours * cfg.hourly_rate),
            ("Firmware Programming", cfg.programming_cost),
            ("Order Processing (flat fee)", cfg.order_processing_cost),
            ("QA Documentation & Reporting",
             getattr(cfg, "qa_documentation_cost", 0.0)),
        ]
        cost_breakdown = [{"label": l, "amount": a} for l, a in entries if a > 0]

    # ── Totals — use CostBreakdown fields if present ──────────────────────────
    def _get(obj, *attrs, default=0.0):
        for a in attrs:
            if hasattr(obj, a):
                return getattr(obj, a)
        return default

    subtotal      = _get(costs, "net_assembly", "subtotal", default=
                         sum(cb["amount"] for cb in cost_breakdown))
    margin_pct    = _get(costs, "margin_percent", "margin_pct", default=cfg.margin_pct)
    margin_amount = _get(costs, "margin_amount",  default=subtotal * margin_pct / 100)
    net_total     = _get(costs, "net_with_margin", "net_total",
                         default=subtotal + margin_amount)
    vat_pct       = _get(costs, "vat_percent", "vat_pct", default=cfg.vat_pct)
    vat_amount    = _get(costs, "vat_amount",  default=net_total * vat_pct / 100)
    grand_total   = _get(costs, "grand_total", default=net_total + vat_amount)

    # ── Mismatches list ───────────────────────────────────────────────────────
    mismatches = [
        {
            "position":     row.pos,
            "reference":    row.reference,
            "declared_qty": row.declared_qty,
            "counted_qty":  row.actual_ref_count,
        }
        for row in bom.rows if not row.qty_match
    ]

    # ── Quote metadata ────────────────────────────────────────────────────────
    today      = datetime.today()
    valid_date = today + timedelta(days=30)
    quote_number = f"Q-{today.year}-{str(abs(hash(str(today.date()))))[:3]:>03}"

    return {
        "quote_number":  quote_number,
        "date":          today.strftime("%d.%m.%Y"),
        "valid_until":   valid_date.strftime("%d.%m.%Y"),
        "prepared_by":   prepared_by,

        "company": company or {
            "name":    "Your Company GmbH",
            "address": "Musterstraße 1, 10115 Berlin, Germany",
            "email":   "info@yourcompany.de",
            "phone":   "+49 30 1234567",
            "website": "www.yourcompany.de",
        },
        "customer": customer or {
            "name":    "",
            "company": "",
            "address": "",
            "email":   "",
        },

        "line_items":      line_items,
        "cost_breakdown":  cost_breakdown,

        "component_total": 0.0,
        "subtotal":        subtotal,
        "margin_pct":      margin_pct,
        "margin_amount":   margin_amount,
        "net_total":       net_total,
        "vat_pct":         vat_pct,
        "vat_amount":      vat_amount,
        "grand_total":     grand_total,

        "smt_qty":         bom.total_smt_qty,
        "tht_qty":         bom.total_tht_qty,
        "mismatches":      mismatches,
    }


# Keep old name working too
build_quotation = generate_quote