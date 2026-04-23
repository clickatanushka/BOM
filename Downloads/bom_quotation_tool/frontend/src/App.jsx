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
}

export default function App() {
  const [config, setConfig] = useState(DEFAULT_CONFIG)
  const [bom, setBom] = useState(null)
  const [parsing, setParsing] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const [generated, setGenerated] = useState(false)

  useEffect(() => {
    getDefaultConfig().then(cfg => setConfig(prev => ({ ...prev, ...cfg }))).catch(() => {})
  }, [])

  const handleFile = async (file) => {
    setParsing(true)
    setError(null)
    setBom(null)
    setGenerated(false)
    try {
      const result = await parseBOM(file)
      setBom(result)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to parse BOM. Check the file format.')
    } finally {
      setParsing(false)
    }
  }

  const handleGenerate = async (format) => {
    if (!bom) return
    setGenerating(true)
    setError(null)
    try {
      const blob = await generateQuotation(
        bom.filename,
        config,
        config._recipient_company,
        config._recipient_address,
        format
      )
      const ext = format === 'excel' ? 'xlsx' : 'pdf'
      downloadBlob(blob, `quotation_${config.quote_number}.${ext}`)
      setGenerated(true)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to generate quotation.')
    } finally {
      setGenerating(false)
    }
  }

  const reset = () => { setBom(null); setGenerated(false); setError(null) }

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo">
          BOM<span>→</span>QUOTE
          <div className="logo-sub">AI Quotation Tool v1.0</div>
        </div>
        <CostConfig config={config} setConfig={setConfig} />
      </div>

      <div className="main">
        <div className="topbar">
          <div className="topbar-title">BOM → QUOTATION GENERATOR</div>
          <div className={`status-pill ${bom ? 'ready' : ''}`}>
            {bom ? `✓ ${bom.filename}` : 'No BOM loaded'}
          </div>
        </div>

        <div className="content">
          {!bom && (
            <DropZone onFile={handleFile} loading={parsing} />
          )}

          {error && (
            <div className="mismatch-banner" style={{ borderColor: '#ffc7ce', background: '#fff2f2' }}>
              <span>✗</span><div>{error}</div>
            </div>
          )}

          {bom && (
            <>
              <MismatchBanner rows={bom.rows} />
              <BOMTable bom={bom} />

              <div className="btn-row">
                <button
                  className="btn btn-primary"
                  disabled={generating}
                  onClick={() => handleGenerate('pdf')}
                >
                  {generating ? 'Generating...' : '↓ Export PDF Quotation'}
                </button>
                <button
                  className="btn btn-secondary"
                  disabled={generating}
                  onClick={() => handleGenerate('excel')}
                >
                  ↓ Export Excel Quotation
                </button>
                <button className="btn btn-secondary" onClick={reset}>
                  Load New BOM
                </button>
              </div>

              {generated && (
                <div style={{ background: '#d4f5e2', border: '1px solid #6fcf97', borderRadius: 4, padding: '12px 18px', fontSize: 13, color: '#0d5c34' }}>
                  ✓ Quotation generated and downloaded successfully.
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
