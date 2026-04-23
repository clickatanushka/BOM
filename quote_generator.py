from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional
from config import CostConfig
from bom_parser import ParsedBOM, BOMRow
from cost_engine import CostBreakdown, LineItem


@dataclass
class Quotation:
    # Header
    quote_number: str
    date: date
    valid_until: date

    # Parties
    sender_company: str
    sender_address: str
    sender_email: str
    sender_website: str
    sender_phone: str
    sender_hrb: str
    sender_vat_id: str
    sender_iban: str
    sender_bank: str

    recipient_company: str = "Recipient GmbH"
    recipient_address: str = "Sample Street 123\n12345 Berlin"

    # BOM summary
    bom_filename: str = ""
    total_component_types: int = 0
    total_smt_qty: int = 0
    total_tht_qty: int = 0
    mismatch_count: int = 0
    bom_rows: List[BOMRow] = field(default_factory=list)

    # Costs
    line_items: List[LineItem] = field(default_factory=list)
    net_assembly: float = 0.0
    margin_amount: float = 0.0
    margin_percent: float = 0.0
    net_with_margin: float = 0.0
    vat_amount: float = 0.0
    vat_percent: float = 0.0
    grand_total: float = 0.0

    # Terms
    payment_terms: str = "Net 14 days from invoice date"


def build_quotation(
    bom: ParsedBOM,
    costs: CostBreakdown,
    cfg: CostConfig,
    recipient_company: str = "Recipient GmbH",
    recipient_address: str = "Sample Street 123\n12345 Berlin",
) -> Quotation:
    today = date.today()
    valid_until = today + timedelta(days=cfg.validity_days)

    return Quotation(
        quote_number=cfg.quote_number,
        date=today,
        valid_until=valid_until,
        sender_company=cfg.company_name,
        sender_address=cfg.company_address,
        sender_email=cfg.company_email,
        sender_website=cfg.company_website,
        sender_phone=cfg.company_phone,
        sender_hrb=cfg.company_hrb,
        sender_vat_id=cfg.company_vat_id,
        sender_iban=cfg.company_iban,
        sender_bank=cfg.company_bank,
        recipient_company=recipient_company,
        recipient_address=recipient_address,
        bom_filename=bom.filename,
        total_component_types=bom.total_components,
        total_smt_qty=bom.total_smt_qty,
        total_tht_qty=bom.total_tht_qty,
        mismatch_count=bom.mismatch_count,
        bom_rows=bom.rows,
        line_items=costs.line_items,
        net_assembly=costs.net_assembly,
        margin_amount=costs.margin_amount,
        margin_percent=costs.margin_percent,
        net_with_margin=costs.net_with_margin,
        vat_amount=costs.vat_amount,
        vat_percent=costs.vat_percent,
        grand_total=costs.grand_total,
        payment_terms=cfg.payment_terms,
    )