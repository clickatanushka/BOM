import { useState, useEffect } from 'react'
import DropZone from './components/DropZone'
import BOMTable from './components/BOMTable'
import MismatchBanner from './components/MismatchBanner'
import CostConfig from './components/CostConfig'
import { parseBOM, generateQuotation, getDefaultConfig, downloadBlob } from './api'
import './styles.css'

const DEFAULT_CONFIG = {
  smt_cost_per_component: 0.35,
  tht_cost_per_component: 0.65,
  setup_hours: 3,
  hourly_rate: 70,
  qa_hours: 2,
  programming_cost_per_unit: 1.0,
  order_processing_cost: 60,
  qa_documentation_cost: 0,
  margin_percent: 15,
  vat_percent: 19,
  company_name: 'Acme Electronics GmbH',
  company_address: 'Musterstraße 123, 12345 Berlin',
  company_email: 'info@acme-electronics.de',
  company_website: 'www.acme-electronics.de',
  company_phone: '+49 123 4567 8910',
  company_hrb: 'HRB 123456',
  company_vat_id: 'DE123456789',
  company_iban: 'DE12 3456 7890 1234 5678 90',
  company_bank: 'Musterbank',
  payment_terms: 'Net 14 days from invoice date',
  validity_days: 30,
  quote_number: 'Q-2026-001',
  _recipient_company: 'Recipient GmbH',
  _recipient_address: 'Sample Street 123\n12345 Berlin',
  _recipient_name: '',          // ← person's name for salutation
}

// All UI labels in both languages
const UI = {
  en: {
    app_title:        'BOM → QUOTATION GENERATOR',
    no_bom:           'No BOM loaded',
    export_pdf:       '↓ Export PDF Quotation',
    export_excel:     '↓ Export Excel Quotation',
    load_new:         'Load New BOM',
    generating:       'Generating...',
    success:          '✓ Quotation generated and downloaded successfully.',
    lang_label:       'Language / Sprache',
    company_info:     'Company Info',
    company_name:     'Company Name',
    address:          'Address',
    email:            'Email',
    quote_number:     'Quote Number',
    valid_days:       'Valid (days)',
    recipient:        'Recipient',
    recipient_co:     'Company',
    recipient_addr:   'Address',
    recipient_name:   'Contact Person Name',  // ← NEW
    assembly_costs:   'Assembly Costs',
    pricing:          'Pricing',
    margin:           'Margin %',
    vat:              'VAT %',
  },
  de: {
    app_title:        'BOM → ANGEBOTS-GENERATOR',
    no_bom:           'Keine BOM geladen',
    export_pdf:       '↓ Angebot als PDF exportieren',
    export_excel:     '↓ Angebot als Excel exportieren',
    load_new:         'Neue BOM laden',
    generating:       'Wird generiert...',
    success:          '✓ Angebot erfolgreich generiert und heruntergeladen.',
    lang_label:       'Language / Sprache',
    company_info:     'Firmendaten',
    company_name:     'Firmenname',
    address:          'Adresse',
    email:            'E-Mail',
    quote_number:     'Angebotsnummer',
    valid_days:       'Gültigkeit (Tage)',
    recipient:        'Empfänger',
    recipient_co:     'Firma',
    recipient_addr:   'Adresse',
    recipient_name:   'Ansprechpartner Name',  // ← NEW
    assembly_costs:   'Bestückungskosten',
    pricing:          'Preisgestaltung',
    margin:           'Marge %',
    vat:              'MwSt. %',
  }
}

export default function App() {
  const [config, setConfig]       = useState(DEFAULT_CONFIG)
  const [bom, setBom]             = useState(null)
  const [parsing, setParsing]     = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError]         = useState(null)
  const [generated, setGenerated] = useState(false)
  const [lang, setLang]           = useState('en')

  const u = UI[lang]

  useEffect(() => {
    getDefaultConfig().then(cfg => setConfig(prev => ({ ...prev, ...cfg }))).catch(() => {})
  }, [])

  const handleFile = async (file) => {
    setParsing(true); setError(null); setBom(null); setGenerated(false)
    try { setBom(await parseBOM(file)) }
    catch (e) { setError(e?.response?.data?.detail || 'Failed to parse BOM.') }
    finally { setParsing(false) }
  }

  const handleGenerate = async (format) => {
    if (!bom) return
    setGenerating(true); setError(null)
    try {
      const blob = await generateQuotation(
        bom.filename, config,
        config._recipient_company,
        config._recipient_address,
        config._recipient_name || '',   // ← pass name
        format, lang
      )
      downloadBlob(blob, `quotation_${config.quote_number}.${format === 'excel' ? 'xlsx' : 'pdf'}`)
      setGenerated(true)
    } catch (e) { setError(e?.response?.data?.detail || 'Failed to generate quotation.') }
    finally { setGenerating(false) }
  }

  const reset = () => { setBom(null); setGenerated(false); setError(null) }
  const upd   = (key) => (val) => setConfig(prev => ({ ...prev, [key]: val }))

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">BOM<span>→</span>QUOTE<div className="logo-sub">AI Quotation Tool v1.0</div></div>

        {/* Language toggle */}
        <div className="config-section">
          <div className="config-label">{u.lang_label}</div>
          <div style={{ display: 'flex', gap: 8 }}>
            {['en','de'].map(l => (
              <button key={l} onClick={() => setLang(l)} style={{
                flex:1, padding:'7px 0', fontFamily:'var(--mono)', fontSize:12,
                cursor:'pointer', borderRadius:3, border:'1px solid',
                borderColor: lang===l ? '#e8401c' : '#2a2a2a',
                background:  lang===l ? '#e8401c' : '#1a1a1a',
                color:'#fff', fontWeight: lang===l ? 600 : 400,
              }}>
                {l === 'en' ? 'EN English' : 'DE Deutsch'}
              </button>
            ))}
          </div>
        </div>

        <hr className="section-divider" />

        {/* Company info */}
        <div className="config-section">
          <div className="config-label">{u.company_info}</div>
          {[
            [u.company_name, 'company_name'],
            [u.address,      'company_address'],
            [u.email,        'company_email'],
            [u.quote_number, 'quote_number'],
          ].map(([label, key]) => (
            <div className="config-row" key={key}>
              <label className="config-label">{label}</label>
              <input value={config[key] || ''} onChange={e => upd(key)(e.target.value)} />
            </div>
          ))}
          <div className="config-row">
            <label className="config-label">{u.valid_days}</label>
            <input type="number" value={config.validity_days}
              onChange={e => setConfig(p => ({ ...p, validity_days: parseInt(e.target.value)||30 }))} />
          </div>
        </div>

        <hr className="section-divider" />

        {/* Recipient */}
        <div className="config-section">
          <div className="config-label">{u.recipient}</div>
          <div className="config-row">
            <label className="config-label">{u.recipient_co}</label>
            <input value={config._recipient_company || ''} onChange={e => upd('_recipient_company')(e.target.value)} />
          </div>
          <div className="config-row">
            <label className="config-label">{u.recipient_addr}</label>
            <input value={config._recipient_address || ''} onChange={e => upd('_recipient_address')(e.target.value)} />
          </div>
          {/* ── NEW: Contact person name field ── */}
          <div className="config-row">
            <label className="config-label">{u.recipient_name}</label>
            <input
              placeholder={lang === 'en' ? 'e.g. John Smith' : 'z.B. Max Mustermann'}
              value={config._recipient_name || ''}
              onChange={e => upd('_recipient_name')(e.target.value)}
            />
          </div>
        </div>

        <hr className="section-divider" />

        {/* Assembly costs */}
        <div className="config-section">
          <div className="config-label">{u.assembly_costs}</div>
          <div className="cost-grid">
            {[
              ['SMT / pcs (€)',  'smt_cost_per_component', '0.01'],
              ['THT / pcs (€)',  'tht_cost_per_component', '0.01'],
              ['Setup hrs',      'setup_hours',            '0.5'],
              ['Hourly (€)',     'hourly_rate',            '1'],
              ['QA hrs',         'qa_hours',               '0.5'],
              ['Prog (€)',       'programming_cost_per_unit','0.1'],
              ['Order (€)',      'order_processing_cost',  '5'],
              ['QA doc (€)',     'qa_documentation_cost',  '10'],
            ].map(([label, key, step]) => (
              <div className="cost-item" key={key}>
                <label>{label}</label>
                <input type="number" step={step} value={config[key]}
                  onChange={e => setConfig(p => ({ ...p, [key]: parseFloat(e.target.value)||0 }))} />
              </div>
            ))}
          </div>
        </div>

        <hr className="section-divider" />

        {/* Pricing */}
        <div className="config-section">
          <div className="config-label">{u.pricing}</div>
          <div className="cost-grid">
            <div className="cost-item">
              <label>{u.margin}</label>
              <input type="number" step="1" value={config.margin_percent}
                onChange={e => setConfig(p => ({ ...p, margin_percent: parseFloat(e.target.value)||0 }))} />
            </div>
            <div className="cost-item">
              <label>{u.vat}</label>
              <input type="number" step="1" value={config.vat_percent}
                onChange={e => setConfig(p => ({ ...p, vat_percent: parseFloat(e.target.value)||0 }))} />
            </div>
          </div>
        </div>
      </div>

      {/* Main area */}
      <div className="main">
        <div className="topbar">
          <div className="topbar-title">{u.app_title}</div>
          <div className={`status-pill ${bom ? 'ready' : ''}`}>
            {bom ? `✓ ${bom.filename}` : u.no_bom}
          </div>
        </div>

        <div className="content">
          {!bom && <DropZone onFile={handleFile} loading={parsing} />}

          {error && (
            <div className="mismatch-banner" style={{ borderColor:'#ffc7ce', background:'#fff2f2' }}>
              <span>✗</span><div>{error}</div>
            </div>
          )}

          {bom && (
            <>
              <MismatchBanner rows={bom.rows} />
              <BOMTable bom={bom} />
              <div className="btn-row">
                <button className="btn btn-primary" disabled={generating} onClick={() => handleGenerate('pdf')}>
                  {generating ? u.generating : u.export_pdf}
                </button>
                <button className="btn btn-secondary" disabled={generating} onClick={() => handleGenerate('excel')}>
                  {u.export_excel}
                </button>
                <button className="btn btn-secondary" onClick={reset}>{u.load_new}</button>
              </div>
              {generated && (
                <div style={{ background:'#d4f5e2', border:'1px solid #6fcf97', borderRadius:4, padding:'12px 18px', fontSize:13, color:'#0d5c34' }}>
                  {u.success}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}