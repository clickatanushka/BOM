export default function BOMTable({ bom }) {
  const totalQty = bom.rows.reduce((s, r) => s + r.declared_qty, 0)

  return (
    <div className="bom-preview">
      <div className="bom-header">
        <div className="bom-title">PARSED BOM — {bom.filename}</div>
        <div className="bom-stats">
          <div className="bom-stat">Types: <span className="val">{bom.total_components}</span></div>
          <div className="bom-stat">SMT qty: <span className="val">{bom.total_smt_qty}</span></div>
          <div className="bom-stat">THT qty: <span className="val">{bom.total_tht_qty}</span></div>
          <div className="bom-stat">Total: <span className="val">{totalQty}</span></div>
          <div className="bom-stat">Mismatches: <span className="err">{bom.mismatch_count}</span></div>
        </div>
      </div>

      {bom.errors.length > 0 && (
        <div style={{ padding: '8px 16px', background: '#fff3f0', fontSize: 12, color: '#8a2010' }}>
          {bom.errors.map((e, i) => <div key={i}>⚠ {e}</div>)}
        </div>
      )}

      <div className="tbl-wrap">
        <table>
          <thead>
            <tr>
              <th>Pos</th>
              <th>Reference(s)</th>
              <th style={{ textAlign: 'right' }}>Declared Qty</th>
              <th style={{ textAlign: 'right' }}>Ref Count</th>
              <th>Type</th>
              <th>Status</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {bom.rows.map((row, i) => (
              <tr key={i} className={!row.qty_match ? 'row-err' : ''}>
                <td>{row.pos}</td>
                <td style={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={row.reference}>
                  {row.reference}
                </td>
                <td style={{ textAlign: 'right' }}>{row.declared_qty}</td>
                <td style={{ textAlign: 'right' }}>{row.actual_ref_count}</td>
                <td>{row.is_smt ? 'SMT' : 'THT'}</td>
                <td>
                  {row.qty_match
                    ? <span className="match-ok">✓ OK</span>
                    : <span className="match-err">✗ MISMATCH ({row.mismatch_diff > 0 ? '+' : ''}{row.mismatch_diff})</span>
                  }
                </td>
                <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: '#666' }} title={row.description}>
                  {row.description}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
