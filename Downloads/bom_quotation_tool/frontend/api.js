import axios from 'axios'

const BASE = '/api'

export async function parseBOM(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await axios.post(`${BASE}/parse`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export async function generateQuotation(
  filename, config,
  recipientCompany, recipientAddress,
  recipientName,       // ← NEW
  exportFormat,
  language = 'en'
) {
  const res = await axios.post(
    `${BASE}/generate?filename=${encodeURIComponent(filename)}`,
    {
      config,
      recipient_company: recipientCompany,
      recipient_address: recipientAddress,
      recipient_name:    recipientName,    // ← NEW
      export_format:     exportFormat,
      language:          language,
    },
    { responseType: 'blob' }
  )
  return res.data
}

export async function getDefaultConfig() {
  const res = await axios.get(`${BASE}/default-config`)
  return res.data
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}