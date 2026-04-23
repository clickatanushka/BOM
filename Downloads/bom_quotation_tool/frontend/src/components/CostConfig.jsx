function Field({ label, id, value, onChange, type = 'text', step }) {
  return (
    <div className="config-row">
      <label className="config-label">{label}</label>
      <input id={id} type={type} step={step} value={value}
        onChange={e => onChange(e.target.value)} />
    </div>
  )
}

function CostField({ label, field, config, setConfig, step = '0.01' }) {
  return (
    <div className="cost-item">
      <label>{label}</label>
      <input type="number" step={step} value={config[field]}
        onChange={e => setConfig(prev => ({ ...prev, [field]: parseFloat(e.target.value) || 0 }))} />
    </div>
  )
}

export default function CostConfig({ config, setConfig }) {
  const upd = (key) => (val) => setConfig(prev => ({ ...prev, [key]: val }))

  return (
    <>
      <div className="config-section">
        <div className="config-label">Company Info</div>
        <Field label="Company Name"   value={config.company_name}    onChange={upd('company_name')} />
        <Field label="Address"        value={config.company_address}  onChange={upd('company_address')} />
        <Field label="Email"          value={config.company_email}    onChange={upd('company_email')} />
        <Field label="Quote Number"   value={config.quote_number}     onChange={upd('quote_number')} />
        <Field label="Valid (days)"   value={config.validity_days}    onChange={v => setConfig(p => ({ ...p, validity_days: parseInt(v)||30 }))} type="number" step="1" />
      </div>

      <hr className="section-divider" />

      <div className="config-section">
        <div className="config-label">Recipient</div>
        <Field label="Company"  value={config._recipient_company || ''} onChange={upd('_recipient_company')} />
        <Field label="Address"  value={config._recipient_address || ''} onChange={upd('_recipient_address')} />
      </div>

      <hr className="section-divider" />

      <div className="config-section">
        <div className="config-label">Assembly Costs</div>
        <div className="cost-grid">
          <CostField label="SMT / pcs (€)"   field="smt_cost_per_component"    config={config} setConfig={setConfig} />
          <CostField label="THT / pcs (€)"   field="tht_cost_per_component"    config={config} setConfig={setConfig} />
          <CostField label="Setup hrs"        field="setup_hours"               config={config} setConfig={setConfig} step="0.5" />
          <CostField label="Hourly rate (€)"  field="hourly_rate"               config={config} setConfig={setConfig} step="1" />
          <CostField label="QA hrs"           field="qa_hours"                  config={config} setConfig={setConfig} step="0.5" />
          <CostField label="Prog / unit (€)"  field="programming_cost_per_unit" config={config} setConfig={setConfig} />
          <CostField label="Order proc (€)"   field="order_processing_cost"     config={config} setConfig={setConfig} step="5" />
          <CostField label="QA doc (€)"       field="qa_documentation_cost"     config={config} setConfig={setConfig} step="10" />
        </div>
      </div>

      <hr className="section-divider" />

      <div className="config-section">
        <div className="config-label">Pricing</div>
        <div className="cost-grid">
          <CostField label="Margin %"  field="margin_percent" config={config} setConfig={setConfig} step="1" />
          <CostField label="VAT %"     field="vat_percent"    config={config} setConfig={setConfig} step="1" />
        </div>
      </div>
    </>
  )
}
