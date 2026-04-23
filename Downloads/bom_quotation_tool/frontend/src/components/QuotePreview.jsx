// QuotePreview.jsx
// This component renders a live HTML preview of the quotation
// (same layout as the PDF output) so the user can review before downloading.

const euro = (val) =>
  '€ ' + Number(val).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export default function QuotePreview({ quote, costs, config }) {
  if (!quote || !costs) return null

  const today = new Date().toLocaleDateString('en-GB')
  const validUntil = new Date(Date.now() + config.validity_days * 86400000).toLocaleDateString('en-GB')

  return (
    <div className="quote-preview">
      <div className="qp-header">
        <div className="qp-title">QUOTATION PREVIEW</div>
        <span style={{ fontSize: 11, fontFamily: 'var(--mono)', color: 'var(--ink3)' }}>
          scroll to review · use Export buttons to download
        </span>
      </div>

      <div className="quote-doc">
        {/* Sender line */}
        <div style={{ fontSize: 11, color: '#888', fontFamily: 'var(--mono)', marginBottom: 20 }}>
          {config.company_name} · {config.company_address}
        </div>

        {/* Two-column header */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, marginBottom: 24 }}>
          <div>
            <div style={{ fontSize: 10, color: '#888', fontFamily: 'var(--mono)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6 }}>Recipient</div>
            <div style={{ fontSize: 14, fontWeight: 600 }}>{config._recipient_company || 'Recipient GmbH'}</div>
            <div style={{ fontSize: 12, color: '#666', whiteSpace: 'pre-line' }}>{config._recipient_address || ''}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontWeight: 600, fontSize: 13 }}>{config.company_name}</div>
            <div style={{ fontSize: 12, color: '#666' }}>{config.company_address}</div>
          </div>
        </div>

        {/* Meta */}
        <div style={{ display: 'flex', gap: 32, marginBottom: 24, borderBottom: '1px solid #e0ddd6', paddingBottom: 12 }}>
          {[
            ['Quote No.', config.quote_number],
            ['Date', today],
            ['Valid Until', validUntil],
            ['Components', `${quote.total_component_types} types / ${quote.total_smt_qty + quote.total_tht_qty} pcs`],
          ].map(([label, val]) => (
            <div key={label}>
              <div style={{ fontSize: 9, color: '#888', fontFamily: 'var(--mono)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{label}</div>
              <div style={{ fontSize: 12, fontFamily: 'var(--mono)' }}>{val}</div>
            </div>
          ))}
        </div>

        {/* Heading */}
        <div style={{ fontSize: 24, fontWeight: 300, letterSpacing: '-0.02em', marginBottom: 8 }}>Quotation</div>
        <div style={{ fontSize: 13, color: '#444', lineHeight: 1.7, marginBottom: 20 }}>
          Dear Sir or Madam,<br /><br />
          Thank you for your inquiry. Based on the submitted Bill of Materials (
          <strong>{quote.total_smt_qty + quote.total_tht_qty} components</strong>,{' '}
          <strong>{quote.total_component_types} line items</strong>), we are pleased to submit the following
          quotation for PCB assembly services.
        </div>

        {/* Line items table */}
        <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 20, fontSize: 12 }}>
          <thead>
            <tr>
              {['Pos.', 'Service / Description', 'Qty.', 'Unit', 'Unit Price', 'Total'].map((h, i) => (
                <th key={h} style={{
                  borderBottom: '2px solid #0f0f0f', padding: '8px 10px',
                  textAlign: i >= 2 ? 'right' : 'left',
                  fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase',
                  fontWeight: 500, color: '#444'
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {costs.line_items.map((item, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? '#fff' : '#f9f8f6' }}>
                <td style={{ padding: '8px 10px', fontFamily: 'var(--mono)', borderBottom: '1px solid #f0ede8' }}>{item.pos}</td>
                <td style={{ padding: '8px 10px', borderBottom: '1px solid #f0ede8' }}>{item.description}</td>
                <td style={{ padding: '8px 10px', textAlign: 'right', fontFamily: 'var(--mono)', borderBottom: '1px solid #f0ede8' }}>{item.qty}</td>
                <td style={{ padding: '8px 10px', fontFamily: 'var(--mono)', borderBottom: '1px solid #f0ede8' }}>{item.unit}</td>
                <td style={{ padding: '8px 10px', textAlign: 'right', fontFamily: 'var(--mono)', borderBottom: '1px solid #f0ede8' }}>{euro(item.unit_price)}</td>
                <td style={{ padding: '8px 10px', textAlign: 'right', fontFamily: 'var(--mono)', fontWeight: 500, borderBottom: '1px solid #f0ede8' }}>{euro(item.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Totals */}
        <div style={{ marginLeft: 'auto', width: 300, marginBottom: 24 }}>
          {[
            ['Assembly Net',                     costs.net_assembly,    false, '#f9f8f6', '#444'],
            [`Margin (${config.margin_percent}%)`, costs.margin_amount, false, '#f9f8f6', '#444'],
            ['Net Price',                         costs.net_with_margin, false, '#eef3ff', '#1a4fd6'],
            [`VAT (${config.vat_percent}%)`,      costs.vat_amount,     false, '#f9f8f6', '#444'],
            ['QUOTATION TOTAL',                   costs.grand_total,    true,  '#1a4fd6', '#fff'],
          ].map(([label, val, bold, bg, color]) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between',
              padding: '8px 10px', background: bg,
              borderTop: bold ? '2px solid #0f0f0f' : '1px solid #e0ddd6',
              borderBottom: bold ? '2px solid #0f0f0f' : 'none',
            }}>
              <span style={{ fontSize: bold ? 13 : 12, fontWeight: bold ? 600 : 400, color, fontFamily: 'var(--mono)' }}>{label}</span>
              <span style={{ fontSize: bold ? 13 : 12, fontWeight: bold ? 600 : 400, color, fontFamily: 'var(--mono)' }}>{euro(val)}</span>
            </div>
          ))}
        </div>

        {/* Footer text */}
        <div style={{ fontSize: 12, color: '#444', lineHeight: 1.7, marginBottom: 20 }}>
          <strong>Payment Terms:</strong> {config.payment_terms}.<br />
          We look forward to your feedback and remain available for any questions at any time.
        </div>
        <div style={{ fontSize: 13, marginBottom: 32 }}>
          Kind regards,<br /><br />
          <strong>{config.company_name}</strong>
        </div>

        {/* Company footer */}
        <div style={{ borderTop: '1px solid #e0ddd6', paddingTop: 14, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
          {[
            { title: config.company_name, lines: ['Managing Director Name', config.company_hrb, `VAT ID: ${config.company_vat_id}`] },
            { title: 'Bank Details', lines: [`Bank: ${config.company_bank}`, `IBAN: ${config.company_iban}`] },
            { title: 'Contact', lines: [config.company_email, config.company_website, config.company_phone] },
          ].map(col => (
            <div key={col.title} style={{ fontSize: 10, fontFamily: 'var(--mono)', lineHeight: 1.8, color: '#888' }}>
              <strong style={{ color: '#0f0f0f', display: 'block', marginBottom: 4 }}>{col.title}</strong>
              {col.lines.map(l => <div key={l}>{l}</div>)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
