export default function MismatchBanner({ rows }) {
  const mismatches = rows.filter(r => !r.qty_match)
  if (mismatches.length === 0) return null

  return (
    <div className="mismatch-banner">
      <span>⚠</span>
      <div>
        <strong>{mismatches.length} Qty mismatch(es) detected in BOM</strong>
        <div className="mismatch-list">
          {mismatches.map(r => (
            <div key={r.pos}>
              · Pos {r.pos}: declared <b>{r.declared_qty}</b> but found <b>{r.actual_ref_count}</b> references
              (diff: {r.mismatch_diff > 0 ? '+' : ''}{r.mismatch_diff})
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
