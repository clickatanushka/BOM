# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import mm
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
# )
# from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
# from io import BytesIO
# from quote_generator import Quotation


# # ── Colours ──────────────────────────────────────────────────────────────────
# INK       = colors.HexColor("#0f0f0f")
# INK2      = colors.HexColor("#444444")
# INK3      = colors.HexColor("#888888")
# ACCENT    = colors.HexColor("#1a4fd6")
# DANGER    = colors.HexColor("#e8401c")
# SUCCESS   = colors.HexColor("#1a7a4a")
# LIGHT_BG  = colors.HexColor("#f9f8f6")
# WARN_BG   = colors.HexColor("#fff3f0")
# GRAND_BG  = colors.HexColor("#f0f4ff")
# WHITE     = colors.white
# BORDER    = colors.HexColor("#e0ddd6")

# W, H = A4
# MARGIN = 20 * mm
# CONTENT_W = W - 2 * MARGIN


# def euro(val: float) -> str:
#     return f"€ {val:,.2f}"


# def make_styles():
#     base = getSampleStyleSheet()
#     def s(name, **kw):
#         return ParagraphStyle(name, parent=base["Normal"], **kw)

#     return {
#         "sender_line":  s("sender_line",  fontSize=8,  textColor=INK3, fontName="Helvetica"),
#         "company_name": s("company_name", fontSize=13, textColor=INK,  fontName="Helvetica-Bold"),
#         "address":      s("address",      fontSize=10, textColor=INK2, fontName="Helvetica", leading=14),
#         "meta_label":   s("meta_label",   fontSize=9,  textColor=INK3, fontName="Helvetica"),
#         "meta_value":   s("meta_value",   fontSize=9,  textColor=INK,  fontName="Helvetica"),
#         "heading":      s("heading",      fontSize=22, textColor=INK,  fontName="Helvetica", spaceBefore=6),
#         "body":         s("body",         fontSize=10, textColor=INK2, fontName="Helvetica", leading=16),
#         "th":           s("th",           fontSize=8,  textColor=INK3, fontName="Helvetica-Bold"),
#         "td":           s("td",           fontSize=9,  textColor=INK,  fontName="Helvetica"),
#         "td_right":     s("td_right",     fontSize=9,  textColor=INK,  fontName="Helvetica", alignment=TA_RIGHT),
#         "total_label":  s("total_label",  fontSize=9,  textColor=INK2, fontName="Helvetica"),
#         "total_value":  s("total_value",  fontSize=9,  textColor=INK,  fontName="Helvetica", alignment=TA_RIGHT),
#         "grand_label":  s("grand_label",  fontSize=11, textColor=INK,  fontName="Helvetica-Bold"),
#         "grand_value":  s("grand_value",  fontSize=11, textColor=INK,  fontName="Helvetica-Bold", alignment=TA_RIGHT),
#         "foot":         s("foot",         fontSize=8,  textColor=INK3, fontName="Helvetica", leading=12),
#         "foot_strong":  s("foot_strong",  fontSize=8,  textColor=INK,  fontName="Helvetica-Bold"),
#         "warn":         s("warn",         fontSize=8,  textColor=DANGER,fontName="Helvetica"),
#     }


# def export_pdf(quote: Quotation) -> bytes:
#     buf = BytesIO()
#     doc = SimpleDocTemplate(
#         buf, pagesize=A4,
#         leftMargin=MARGIN, rightMargin=MARGIN,
#         topMargin=MARGIN, bottomMargin=MARGIN,
#         title=f"Quotation {quote.quote_number}",
#         author=quote.sender_company,
#     )
#     st = make_styles()
#     story = []

#     # ── Sender line ───────────────────────────────────────────────────────────
#     story.append(Paragraph(f"{quote.sender_company} · {quote.sender_address}", st["sender_line"]))
#     story.append(Spacer(1, 6 * mm))

#     # ── Two-column header: Recipient | Sender ─────────────────────────────────
#     left_block = [
#         [Paragraph(quote.recipient_company, st["company_name"])],
#         [Paragraph(quote.recipient_address.replace("\n", "<br/>"), st["address"])],
#     ]
#     right_block = [
#         [Paragraph(quote.sender_company, ParagraphStyle("rb", parent=st["company_name"], alignment=TA_RIGHT))],
#         [Paragraph(quote.sender_address, ParagraphStyle("ra", parent=st["address"], alignment=TA_RIGHT))],
#     ]
#     header_tbl = Table(
#         [[
#             Table(left_block,  colWidths=[CONTENT_W * 0.5]),
#             Table(right_block, colWidths=[CONTENT_W * 0.5]),
#         ]],
#         colWidths=[CONTENT_W * 0.5, CONTENT_W * 0.5],
#     )
#     header_tbl.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0)]))
#     story.append(header_tbl)
#     story.append(Spacer(1, 8 * mm))

#     # ── Meta row ──────────────────────────────────────────────────────────────
#     meta_data = [
#         [Paragraph("Quote No.", st["meta_label"]), Paragraph("Date", st["meta_label"]),
#          Paragraph("Valid Until", st["meta_label"]), Paragraph("Components", st["meta_label"])],
#         [Paragraph(quote.quote_number, st["meta_value"]),
#          Paragraph(quote.date.strftime("%d.%m.%Y"), st["meta_value"]),
#          Paragraph(quote.valid_until.strftime("%d.%m.%Y"), st["meta_value"]),
#          Paragraph(f"{quote.total_component_types} types / {quote.total_smt_qty + quote.total_tht_qty} pcs", st["meta_value"])],
#     ]
#     meta_tbl = Table(meta_data, colWidths=[CONTENT_W/4]*4)
#     meta_tbl.setStyle(TableStyle([
#         ("LEFTPADDING",  (0,0), (-1,-1), 0),
#         ("BOTTOMPADDING",(0,0), (-1,-1), 3),
#         ("LINEBELOW",    (0,1), (-1,1), 0.5, BORDER),
#     ]))
#     story.append(meta_tbl)
#     story.append(Spacer(1, 8 * mm))

#     # ── Mismatch warning ──────────────────────────────────────────────────────
#     if quote.mismatch_count > 0:
#         mismatches = [r for r in quote.bom_rows if not r.qty_match]
#         warn_text = f"⚠  {quote.mismatch_count} BOM mismatch(es) detected: " + \
#                     " | ".join([f"Pos {r.pos}: declared {r.declared_qty}, found {r.actual_ref_count}" for r in mismatches[:5]])
#         story.append(Paragraph(warn_text, st["warn"]))
#         story.append(Spacer(1, 4 * mm))

#     # ── Heading & greeting ────────────────────────────────────────────────────
#     story.append(Paragraph("Quotation", st["heading"]))
#     story.append(Spacer(1, 4 * mm))
#     story.append(Paragraph("Dear Sir or Madam,", st["body"]))
#     story.append(Spacer(1, 3 * mm))
#     story.append(Paragraph(
#         f"Thank you for your inquiry. Based on the submitted Bill of Materials "
#         f"(<b>{quote.total_smt_qty + quote.total_tht_qty} components</b>, "
#         f"<b>{quote.total_component_types} line items</b>), we are pleased to "
#         f"submit the following quotation for PCB assembly services.",
#         st["body"]
#     ))
#     story.append(Spacer(1, 6 * mm))

#     # ── Line items table ──────────────────────────────────────────────────────
#     tbl_data = [[
#         Paragraph("Pos.", st["th"]),
#         Paragraph("Service / Description", st["th"]),
#         Paragraph("Qty.", st["th"]),
#         Paragraph("Unit", st["th"]),
#         Paragraph("Unit Price", ParagraphStyle("thr", parent=st["th"], alignment=TA_RIGHT)),
#         Paragraph("Total", ParagraphStyle("thr", parent=st["th"], alignment=TA_RIGHT)),
#     ]]

#     for item in quote.line_items:
#         tbl_data.append([
#             Paragraph(str(item.pos), st["td"]),
#             Paragraph(item.description, st["td"]),
#             Paragraph(f"{item.qty:g}", st["td_right"]),
#             Paragraph(item.unit, st["td"]),
#             Paragraph(euro(item.unit_price), st["td_right"]),
#             Paragraph(euro(item.total), st["td_right"]),
#         ])

#     col_widths = [12*mm, CONTENT_W - 12*mm - 18*mm - 16*mm - 28*mm - 28*mm, 18*mm, 16*mm, 28*mm, 28*mm]
#     items_tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)
#     items_tbl.setStyle(TableStyle([
#         ("LINEBELOW",    (0, 0), (-1, 0),  1.0, INK),
#         ("LINEBELOW",    (0, 1), (-1, -1), 0.3, BORDER),
#         ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LIGHT_BG]),
#         ("LEFTPADDING",  (0, 0), (-1, -1), 4),
#         ("RIGHTPADDING", (0, 0), (-1, -1), 4),
#         ("TOPPADDING",   (0, 0), (-1, -1), 5),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
#         ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
#         ("ALIGN",        (2, 0), (5, -1), "RIGHT"),
#     ]))
#     story.append(items_tbl)
#     story.append(Spacer(1, 6 * mm))

#     # ── Totals block (right-aligned) ──────────────────────────────────────────
#     totals_data = [
#         [Paragraph("Assembly Net",                st["total_label"]), Paragraph(euro(quote.net_assembly),    st["total_value"])],
#         [Paragraph(f"Margin ({quote.margin_percent:.0f}%)", st["total_label"]), Paragraph(euro(quote.margin_amount), st["total_value"])],
#         [Paragraph("Net Price",                   st["total_label"]), Paragraph(euro(quote.net_with_margin), st["total_value"])],
#         [Paragraph(f"VAT ({quote.vat_percent:.0f}%)", st["total_label"]), Paragraph(euro(quote.vat_amount), st["total_value"])],
#         [Paragraph("QUOTATION TOTAL",             st["grand_label"]), Paragraph(euro(quote.grand_total),     st["grand_value"])],
#     ]
#     totals_tbl = Table(totals_data, colWidths=[45*mm, 30*mm], hAlign="RIGHT")
#     totals_tbl.setStyle(TableStyle([
#         ("LINEABOVE",    (0, 2), (-1, 2), 0.5, BORDER),
#         ("LINEABOVE",    (0, 4), (-1, 4), 1.0, INK),
#         ("LINEBELOW",    (0, 4), (-1, 4), 1.0, INK),
#         ("BACKGROUND",   (0, 4), (-1, 4), GRAND_BG),
#         ("LEFTPADDING",  (0, 0), (-1, -1), 6),
#         ("RIGHTPADDING", (0, 0), (-1, -1), 6),
#         ("TOPPADDING",   (0, 0), (-1, -1), 4),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
#         ("ALIGN",        (1, 0), (1, -1), "RIGHT"),
#     ]))
#     story.append(totals_tbl)
#     story.append(Spacer(1, 8 * mm))

#     # ── Footer text ───────────────────────────────────────────────────────────
#     story.append(Paragraph(f"<b>Payment Terms:</b> {quote.payment_terms}.", st["body"]))
#     story.append(Spacer(1, 3 * mm))
#     story.append(Paragraph("We look forward to your feedback and remain available for any questions at any time.", st["body"]))
#     story.append(Spacer(1, 8 * mm))
#     story.append(Paragraph("Kind regards,", st["body"]))
#     story.append(Spacer(1, 6 * mm))
#     story.append(Paragraph(f"<b>{quote.sender_company}</b>", st["body"]))
#     story.append(Spacer(1, 16 * mm))

#     # ── Company footer ────────────────────────────────────────────────────────
#     story.append(HRFlowable(width=CONTENT_W, thickness=0.5, color=BORDER))
#     story.append(Spacer(1, 3 * mm))

#     foot_data = [[
#         Table([
#             [Paragraph(quote.sender_company, st["foot_strong"])],
#             [Paragraph(f"Managing Director Name", st["foot"])],
#             [Paragraph(f"{quote.sender_hrb}", st["foot"])],
#             [Paragraph(f"VAT ID: {quote.sender_vat_id}", st["foot"])],
#         ]),
#         Table([
#             [Paragraph("Bank Details", st["foot_strong"])],
#             [Paragraph(f"Bank: {quote.sender_bank}", st["foot"])],
#             [Paragraph(f"IBAN: {quote.sender_iban}", st["foot"])],
#         ]),
#         Table([
#             [Paragraph("Contact", st["foot_strong"])],
#             [Paragraph(quote.sender_email, st["foot"])],
#             [Paragraph(quote.sender_website, st["foot"])],
#             [Paragraph(quote.sender_phone, st["foot"])],
#         ]),
#     ]]
#     foot_tbl = Table(foot_data, colWidths=[CONTENT_W/3]*3)
#     foot_tbl.setStyle(TableStyle([
#         ("VALIGN",      (0,0), (-1,-1), "TOP"),
#         ("LEFTPADDING", (0,0), (-1,-1), 0),
#     ]))
#     story.append(foot_tbl)

#     doc.build(story)
#     return buf.getvalue()


from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from io import BytesIO
from quote_generator import Quotation

INK      = colors.HexColor("#0f0f0f")
INK2     = colors.HexColor("#444444")
INK3     = colors.HexColor("#888888")
DANGER   = colors.HexColor("#e8401c")
LIGHT_BG = colors.HexColor("#f9f8f6")
GRAND_BG = colors.HexColor("#f0f4ff")
SUCCESS  = colors.HexColor("#e8f5e9")
SUCCESS2 = colors.HexColor("#2e7d32")
WHITE    = colors.white
BORDER   = colors.HexColor("#e0ddd6")

W, H      = A4
MARGIN    = 20 * mm
CONTENT_W = W - 2 * MARGIN

# ── All text in both languages ────────────────────────────────────────────────
TEXT = {
    "en": {
        "title":         "Quotation",
        "subtitle":      "Angebot",
        "greeting_name": "Dear {name},",           # used when name is provided
        "greeting":      "To whom it may concern,", # used when no name
        "intro":         "Thank you for your inquiry. Based on the submitted Bill of Materials (<b>{total} components</b>, <b>{types} line items</b>), we are pleased to submit the following quotation for PCB assembly services.",
        "quote_no":      "Quote No.",
        "date":          "Date",
        "valid_until":   "Valid Until",
        "components":    "Components",
        "pos":           "Pos.",
        "service":       "Service / Description",
        "qty":           "Qty.",
        "unit":          "Unit",
        "total_col":     "Total",
        "assembly_net":  "Assembly Net",
        "margin":        "Margin",
        "net_price":     "Net Price",
        "vat":           "VAT",
        "grand_total":   "QUOTATION TOTAL",
        "payment_label": "Payment Terms",
        "closing":       "We look forward to your feedback and remain available for any questions at any time.",
        "regards":       "Kind regards,",
        "bank":          "Bank Details",
        "contact":       "Contact",
        "qa_title":      "Product Verification & Quality Assurance",
        "qa_body":       "All assemblies undergo a structured quality verification process prior to delivery:<br/><br/>• <b>Visual Inspection (VI):</b> 100% manual inspection of all solder joints and component placement.<br/>• <b>Automated Optical Inspection (AOI):</b> Machine-based optical scan of all SMT components.<br/>• <b>Electrical Testing (ICT/FCT):</b> Functional and in-circuit testing performed on all boards.<br/>• <b>Quality Documentation:</b> Inspection records, test reports, and certificates provided upon request.<br/>• <b>Traceability:</b> Full component traceability (batch/lot numbers) maintained throughout production.",
        "warn":          "BOM mismatch(es) detected",
    },
    "de": {
        "title":         "Angebot",
        "subtitle":      "Quotation",
        "greeting_name": "Sehr geehrte/r {name},",
        "greeting":      "Sehr geehrte Damen und Herren,",
        "intro":         "Vielen Dank für Ihre Anfrage. Basierend auf der eingereichten Stückliste (<b>{total} Bauteile</b>, <b>{types} Positionen</b>) unterbreiten wir Ihnen hiermit folgendes Angebot für PCB-Bestückungsdienstleistungen.",
        "quote_no":      "Angebotsnr.",
        "date":          "Datum",
        "valid_until":   "Gültig bis",
        "components":    "Bauteile",
        "pos":           "Pos.",
        "service":       "Leistung / Beschreibung",
        "qty":           "Menge",
        "unit":          "Einheit",
        "total_col":     "Gesamt",
        "assembly_net":  "Netto Bestückung",
        "margin":        "Marge",
        "net_price":     "Nettopreis",
        "vat":           "MwSt.",
        "grand_total":   "ANGEBOTSBETRAG",
        "payment_label": "Zahlungsbedingungen",
        "closing":       "Wir freuen uns auf Ihre Rückmeldung und stehen Ihnen jederzeit für Rückfragen zur Verfügung.",
        "regards":       "Mit freundlichen Grüßen,",
        "bank":          "Bankverbindung",
        "contact":       "Kontakt",
        "qa_title":      "Produktverifikation & Qualitätssicherung",
        "qa_body":       "Alle Baugruppen durchlaufen vor der Auslieferung einen strukturierten Qualitätssicherungsprozess:<br/><br/>• <b>Sichtprüfung (VI):</b> 100% manuelle Prüfung aller Lötstellen und Bauteilbestückung.<br/>• <b>Automatische optische Inspektion (AOI):</b> Maschinengestützte optische Prüfung aller SMT-Bauteile.<br/>• <b>Elektrische Prüfung (ICT/FCT):</b> Funktions- und In-Circuit-Test aller Platinen.<br/>• <b>Qualitätsdokumentation:</b> Prüfprotokolle, Testberichte und Zertifikate auf Anfrage.<br/>• <b>Rückverfolgbarkeit:</b> Vollständige Bauteil-Rückverfolgbarkeit während der Produktion.",
        "warn":          "BOM-Abweichung(en) festgestellt",
    }
}


def euro(val: float) -> str:
    return f"€ {val:,.2f}"


def make_styles():
    base = getSampleStyleSheet()
    def s(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)
    return {
        "sender_line":  s("sender_line",  fontSize=8,  textColor=INK3,    fontName="Helvetica"),
        "company_name": s("company_name", fontSize=13, textColor=INK,     fontName="Helvetica-Bold"),
        "address":      s("address",      fontSize=10, textColor=INK2,    fontName="Helvetica", leading=14),
        "meta_label":   s("meta_label",   fontSize=9,  textColor=INK3,    fontName="Helvetica"),
        "meta_value":   s("meta_value",   fontSize=9,  textColor=INK,     fontName="Helvetica"),
        "heading":      s("heading",      fontSize=22, textColor=INK,     fontName="Helvetica-Bold", spaceBefore=4),
        "heading_sub":  s("heading_sub",  fontSize=12, textColor=INK3,    fontName="Helvetica",     spaceBefore=0),
        "body":         s("body",         fontSize=10, textColor=INK2,    fontName="Helvetica",     leading=16),
        "th":           s("th",           fontSize=8,  textColor=INK3,    fontName="Helvetica-Bold"),
        "th_r":         s("th_r",         fontSize=8,  textColor=INK3,    fontName="Helvetica-Bold", alignment=TA_RIGHT),
        "td":           s("td",           fontSize=9,  textColor=INK,     fontName="Helvetica"),
        "td_right":     s("td_right",     fontSize=9,  textColor=INK,     fontName="Helvetica",     alignment=TA_RIGHT),
        "total_label":  s("total_label",  fontSize=9,  textColor=INK2,    fontName="Helvetica"),
        "total_value":  s("total_value",  fontSize=9,  textColor=INK,     fontName="Helvetica",     alignment=TA_RIGHT),
        "grand_label":  s("grand_label",  fontSize=11, textColor=INK,     fontName="Helvetica-Bold"),
        "grand_value":  s("grand_value",  fontSize=11, textColor=INK,     fontName="Helvetica-Bold", alignment=TA_RIGHT),
        "qa_title":     s("qa_title",     fontSize=10, textColor=SUCCESS2, fontName="Helvetica-Bold", spaceBefore=4),
        "qa_body":      s("qa_body",      fontSize=9,  textColor=INK2,    fontName="Helvetica",     leading=15),
        "foot":         s("foot",         fontSize=8,  textColor=INK3,    fontName="Helvetica",     leading=12),
        "foot_strong":  s("foot_strong",  fontSize=8,  textColor=INK,     fontName="Helvetica-Bold"),
        "warn":         s("warn",         fontSize=8,  textColor=DANGER,   fontName="Helvetica"),
    }


def export_pdf(quote: Quotation, lang: str = "en") -> bytes:
    T = TEXT[lang]
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"{T['title']} {quote.quote_number}",
        author=quote.sender_company,
    )
    st = make_styles()
    story = []

    # Sender line
    story.append(Paragraph(f"{quote.sender_company} · {quote.sender_address}", st["sender_line"]))
    story.append(Spacer(1, 6 * mm))

    # Two-column header
    left_block  = [[Paragraph(quote.recipient_company, st["company_name"])],
                   [Paragraph(quote.recipient_address.replace("\n", "<br/>"), st["address"])]]
    right_block = [[Paragraph(quote.sender_company,
                              ParagraphStyle("rb", parent=st["company_name"], alignment=TA_RIGHT))],
                   [Paragraph(quote.sender_address,
                              ParagraphStyle("ra", parent=st["address"], alignment=TA_RIGHT))]]
    header_tbl = Table(
        [[Table(left_block,  colWidths=[CONTENT_W * 0.5]),
          Table(right_block, colWidths=[CONTENT_W * 0.5])]],
        colWidths=[CONTENT_W * 0.5, CONTENT_W * 0.5],
    )
    header_tbl.setStyle(TableStyle([
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 8 * mm))

    # Meta row
    total_qty = quote.total_smt_qty + quote.total_tht_qty
    meta_data = [
        [Paragraph(T["quote_no"],    st["meta_label"]),
         Paragraph(T["date"],        st["meta_label"]),
         Paragraph(T["valid_until"], st["meta_label"]),
         Paragraph(T["components"],  st["meta_label"])],
        [Paragraph(quote.quote_number,                     st["meta_value"]),
         Paragraph(quote.date.strftime("%d.%m.%Y"),        st["meta_value"]),
         Paragraph(quote.valid_until.strftime("%d.%m.%Y"), st["meta_value"]),
         Paragraph(f"{quote.total_component_types} / {total_qty} pcs", st["meta_value"])],
    ]
    meta_tbl = Table(meta_data, colWidths=[CONTENT_W / 4] * 4)
    meta_tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ("LINEBELOW",    (0,1), (-1,1),  0.5, BORDER),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 8 * mm))

    # Mismatch warning
    if quote.mismatch_count > 0:
        mismatches = [r for r in quote.bom_rows if not r.qty_match]
        warn_text = (f"⚠  {quote.mismatch_count} {T['warn']}: "
                     + " | ".join([f"Pos {r.pos}: {r.declared_qty} ≠ {r.actual_ref_count}" for r in mismatches[:5]]))
        story.append(Paragraph(warn_text, st["warn"]))
        story.append(Spacer(1, 4 * mm))

    # Dual language heading
    story.append(Paragraph(T["title"],    st["heading"]))
    story.append(Paragraph(T["subtitle"], st["heading_sub"]))
    story.append(Spacer(1, 5 * mm))

    # ── Greeting — uses recipient name if provided, fallback otherwise ─────────
    if quote.recipient_name and quote.recipient_name.strip():
        greeting = T["greeting_name"].format(name=quote.recipient_name.strip())
    else:
        greeting = T["greeting"]
    story.append(Paragraph(greeting, st["body"]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        T["intro"].format(total=total_qty, types=quote.total_component_types),
        st["body"]
    ))
    story.append(Spacer(1, 6 * mm))

    # ── Line items table — NO unit price column ───────────────────────────────
    tbl_data = [[
        Paragraph(T["pos"],       st["th"]),
        Paragraph(T["service"],   st["th"]),
        Paragraph(T["qty"],       st["th_r"]),
        Paragraph(T["unit"],      st["th"]),
        Paragraph(T["total_col"], st["th_r"]),
    ]]
    for item in quote.line_items:
        tbl_data.append([
            Paragraph(str(item.pos),    st["td"]),
            Paragraph(item.description, st["td"]),
            Paragraph(f"{item.qty:g}",  st["td_right"]),
            Paragraph(item.unit,        st["td"]),
            Paragraph(euro(item.total), st["td_right"]),
        ])

    col_widths = [12*mm, CONTENT_W - 12*mm - 18*mm - 18*mm - 32*mm, 18*mm, 18*mm, 32*mm]
    items_tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("LINEBELOW",     (0,0), (-1,0),  1.0, INK),
        ("LINEBELOW",     (0,1), (-1,-1), 0.3, BORDER),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN",         (2,0), (-1,-1), "RIGHT"),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 6 * mm))

    # Totals
    totals_data = [
        [Paragraph(T["assembly_net"],                           st["total_label"]), Paragraph(euro(quote.net_assembly),    st["total_value"])],
        [Paragraph(f"{T['margin']} ({quote.margin_percent:.0f}%)", st["total_label"]), Paragraph(euro(quote.margin_amount),   st["total_value"])],
        [Paragraph(T["net_price"],                              st["total_label"]), Paragraph(euro(quote.net_with_margin), st["total_value"])],
        [Paragraph(f"{T['vat']} ({quote.vat_percent:.0f}%)",   st["total_label"]), Paragraph(euro(quote.vat_amount),      st["total_value"])],
        [Paragraph(T["grand_total"],                            st["grand_label"]), Paragraph(euro(quote.grand_total),     st["grand_value"])],
    ]
    totals_tbl = Table(totals_data, colWidths=[55*mm, 32*mm], hAlign="RIGHT")
    totals_tbl.setStyle(TableStyle([
        ("LINEABOVE",    (0,2), (-1,2), 0.5, BORDER),
        ("LINEABOVE",    (0,4), (-1,4), 1.0, INK),
        ("LINEBELOW",    (0,4), (-1,4), 1.0, INK),
        ("BACKGROUND",   (0,4), (-1,4), GRAND_BG),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("ALIGN",        (1,0), (1,-1),  "RIGHT"),
    ]))
    story.append(totals_tbl)
    story.append(Spacer(1, 8 * mm))

    # Quality Assurance section
    qa_tbl = Table(
        [[Paragraph(T["qa_title"], st["qa_title"])],
         [Paragraph(T["qa_body"],  st["qa_body"])]],
        colWidths=[CONTENT_W],
    )
    qa_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), SUCCESS),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LINEABOVE",    (0,0), (-1,0),  1.0, SUCCESS2),
        ("LINEBELOW",    (0,-1),(-1,-1), 1.0, SUCCESS2),
    ]))
    story.append(qa_tbl)
    story.append(Spacer(1, 8 * mm))

    # Closing
    story.append(Paragraph(f"<b>{T['payment_label']}:</b> {quote.payment_terms}.", st["body"]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(T["closing"], st["body"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(T["regards"], st["body"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(f"<b>{quote.sender_company}</b>", st["body"]))
    story.append(Spacer(1, 16 * mm))

    # Footer
    story.append(HRFlowable(width=CONTENT_W, thickness=0.5, color=BORDER))
    story.append(Spacer(1, 3 * mm))
    foot_data = [[
        Table([[Paragraph(quote.sender_company,              st["foot_strong"])],
               [Paragraph("Managing Director",               st["foot"])],
               [Paragraph(quote.sender_hrb,                  st["foot"])],
               [Paragraph(f"VAT ID: {quote.sender_vat_id}", st["foot"])]]),
        Table([[Paragraph(T["bank"],                         st["foot_strong"])],
               [Paragraph(f"Bank: {quote.sender_bank}",     st["foot"])],
               [Paragraph(f"IBAN: {quote.sender_iban}",     st["foot"])]]),
        Table([[Paragraph(T["contact"],                      st["foot_strong"])],
               [Paragraph(quote.sender_email,                st["foot"])],
               [Paragraph(quote.sender_website,              st["foot"])],
               [Paragraph(quote.sender_phone,                st["foot"])]]),
    ]]
    foot_tbl = Table(foot_data, colWidths=[CONTENT_W / 3] * 3)
    foot_tbl.setStyle(TableStyle([
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(foot_tbl)

    doc.build(story)
    return buf.getvalue()