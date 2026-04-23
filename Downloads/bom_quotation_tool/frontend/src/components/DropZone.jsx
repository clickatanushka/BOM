import { useRef, useState } from 'react'

export default function DropZone({ onFile, loading }) {
  const [drag, setDrag] = useState(false)
  const inputRef = useRef()

  const handle = (file) => {
    if (!file) return
    const ok = ['.xlsx', '.xls', '.csv'].some(ext => file.name.toLowerCase().endsWith(ext))
    if (!ok) { alert('Please upload an .xlsx, .xls, or .csv file.'); return }
    onFile(file)
  }

  return (
    <div
      className={`drop-zone ${drag ? 'drag' : ''}`}
      onClick={() => inputRef.current.click()}
      onDragOver={e => { e.preventDefault(); setDrag(true) }}
      onDragLeave={() => setDrag(false)}
      onDrop={e => { e.preventDefault(); setDrag(false); handle(e.dataTransfer.files[0]) }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        style={{ display: 'none' }}
        onChange={e => handle(e.target.files[0])}
      />
      <div className="drop-icon">{loading ? '⏳' : '📄'}</div>
      <div className="drop-title">{loading ? 'Parsing BOM...' : 'Drop your BOM file here'}</div>
      <div className="drop-sub">supports .xlsx / .xls / .csv</div>
    </div>
  )
}
