from dataclasses import dataclass, field
from typing import List
from config import CostConfig
from bom_parser import ParsedBOM


@dataclass
class LineItem:
    pos: int
    description: str
    qty: float
    unit: str
    unit_price: float
    total: float


@dataclass
class CostBreakdown:
    line_items: List[LineItem] = field(default_factory=list)
    net_assembly: float = 0.0       # sum of all line items
    margin_amount: float = 0.0      # margin in €
    net_with_margin: float = 0.0    # net + margin
    vat_amount: float = 0.0         # VAT in €
    grand_total: float = 0.0        # final price incl. VAT
    margin_percent: float = 0.0
    vat_percent: float = 0.0


def calculate_costs(bom: ParsedBOM, cfg: CostConfig) -> CostBreakdown:
    items: List[LineItem] = []
    pos = 1

    # 1. SMT Assembly
    if bom.total_smt_qty > 0:
        total = bom.total_smt_qty * cfg.smt_cost_per_component
        items.append(LineItem(
            pos=pos,
            description="SMT Component Assembly (machine placed)",
            qty=bom.total_smt_qty,
            unit="pcs",
            unit_price=cfg.smt_cost_per_component,
            total=total,
        ))
        pos += 1

    # 2. THT Assembly
    if bom.total_tht_qty > 0:
        total = bom.total_tht_qty * cfg.tht_cost_per_component
        items.append(LineItem(
            pos=pos,
            description="THT Component Assembly (hand soldering)",
            qty=bom.total_tht_qty,
            unit="pcs",
            unit_price=cfg.tht_cost_per_component,
            total=total,
        ))
        pos += 1

    # 3. Programming
    prog_qty = bom.total_smt_qty
    if prog_qty > 0 and cfg.programming_cost_per_unit > 0:
        total = prog_qty * cfg.programming_cost_per_unit
        items.append(LineItem(
            pos=pos,
            description="Firmware / Component Programming",
            qty=prog_qty,
            unit="pcs",
            unit_price=cfg.programming_cost_per_unit,
            total=total,
        ))
        pos += 1

    # 4. Machine Setup & Material Prep
    if cfg.setup_hours > 0:
        total = cfg.setup_hours * cfg.hourly_rate
        items.append(LineItem(
            pos=pos,
            description="Machine Setup & Material Preparation",
            qty=cfg.setup_hours,
            unit="hrs",
            unit_price=cfg.hourly_rate,
            total=total,
        ))
        pos += 1

    # 5. Quality Verification
    if cfg.qa_hours > 0:
        total = cfg.qa_hours * cfg.hourly_rate
        items.append(LineItem(
            pos=pos,
            description="Quality Verification & Inspection",
            qty=cfg.qa_hours,
            unit="hrs",
            unit_price=cfg.hourly_rate,
            total=total,
        ))
        pos += 1

    # 6. Quality Documentation
    if cfg.qa_documentation_cost > 0:
        items.append(LineItem(
            pos=pos,
            description="Quality Documentation",
            qty=1,
            unit="lump",
            unit_price=cfg.qa_documentation_cost,
            total=cfg.qa_documentation_cost,
        ))
        pos += 1

    # 7. Order Processing
    if cfg.order_processing_cost > 0:
        items.append(LineItem(
            pos=pos,
            description="Order Processing & Project Management",
            qty=1,
            unit="lump",
            unit_price=cfg.order_processing_cost,
            total=cfg.order_processing_cost,
        ))
        pos += 1

    net = sum(i.total for i in items)
    margin_amt = net * (cfg.margin_percent / 100)
    net_with_margin = net + margin_amt
    vat_amt = net_with_margin * (cfg.vat_percent / 100)
    grand = net_with_margin + vat_amt

    return CostBreakdown(
        line_items=items,
        net_assembly=round(net, 2),
        margin_amount=round(margin_amt, 2),
        net_with_margin=round(net_with_margin, 2),
        vat_amount=round(vat_amt, 2),
        grand_total=round(grand, 2),
        margin_percent=cfg.margin_percent,
        vat_percent=cfg.vat_percent,
    )
