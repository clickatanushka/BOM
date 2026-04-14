"""
test_pipeline.py
Run this to verify the full backend pipeline works before launching the app.

Usage:
    cd backend
    python test_pipeline.py path/to/your_bom.xlsx
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import CostConfig
from bom_parser import parse_bom
from cost_engine import calculate_costs
from quote_generator import build_quotation
from pdf_exporter import export_pdf
from excel_exporter import export_excel


def run_test(bom_path: str):
    print(f"\n{'='*60}")
    print(f"  BOM → QUOTATION PIPELINE TEST")
    print(f"{'='*60}\n")

    # 1. Parse
    print(f"[1] Parsing BOM: {bom_path}")
    bom = parse_bom(bom_path, os.path.basename(bom_path))

    if bom.errors:
        print(f"  ⚠ Errors: {bom.errors}")
    print(f"  ✓ {bom.total_components} component types parsed")
    print(f"  ✓ SMT qty: {bom.total_smt_qty}  |  THT qty: {bom.total_tht_qty}")
    print(f"  {'⚠' if bom.mismatch_count else '✓'} Mismatches: {bom.mismatch_count}")

    if bom.mismatch_count:
        for r in bom.rows:
            if not r.qty_match:
                print(f"    Pos {r.pos}: declared {r.declared_qty}, found {r.actual_ref_count} refs")

    # 2. Costs
    print(f"\n[2] Calculating costs...")
    cfg = CostConfig()
    costs = calculate_costs(bom, cfg)

    for item in costs.line_items:
        print(f"  {item.pos}. {item.description:<45} {item.qty:>6} {item.unit:<6}  €{item.total:>8.2f}")

    print(f"\n  {'Assembly Net':<52} €{costs.net_assembly:>8.2f}")
    print(f"  {'Margin (' + str(cfg.margin_percent) + '%)':<52} €{costs.margin_amount:>8.2f}")
    print(f"  {'Net with Margin':<52} €{costs.net_with_margin:>8.2f}")
    print(f"  {'VAT (' + str(cfg.vat_percent) + '%)':<52} €{costs.vat_amount:>8.2f}")
    print(f"  {'QUOTATION TOTAL':<52} €{costs.grand_total:>8.2f}")

    # 3. Build quotation object
    print(f"\n[3] Building quotation...")
    quote = build_quotation(bom, costs, cfg)
    print(f"  ✓ Quote {quote.quote_number}  |  Date: {quote.date}  |  Valid: {quote.valid_until}")

    # 4. Export PDF
    print(f"\n[4] Exporting PDF...")
    pdf_bytes = export_pdf(quote)
    out_pdf = f"test_output_{quote.quote_number}.pdf"
    with open(out_pdf, "wb") as f:
        f.write(pdf_bytes)
    print(f"  ✓ PDF saved: {out_pdf}  ({len(pdf_bytes):,} bytes)")

    # 5. Export Excel
    print(f"\n[5] Exporting Excel...")
    xlsx_bytes = export_excel(quote)
    out_xlsx = f"test_output_{quote.quote_number}.xlsx"
    with open(out_xlsx, "wb") as f:
        f.write(xlsx_bytes)
    print(f"  ✓ Excel saved: {out_xlsx}  ({len(xlsx_bytes):,} bytes)")

    print(f"\n{'='*60}")
    print(f"  ALL TESTS PASSED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pipeline.py path/to/bom.xlsx")
        sys.exit(1)
    run_test(sys.argv[1])