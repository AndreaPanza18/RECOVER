import { useState, useCallback } from 'react'
import './App.css'
import NavBar from './components/NavBar.jsx'
import FileDropZone from './components/FileDropZone.jsx'
import { Loader2, Upload } from 'lucide-react'

function App() {
  const [activeTool, setActiveTool] = useState('extract')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [rawText, setRawText] = useState('')
  const [results, setResults] = useState(null)
  const [provider, setProvider] = useState('llama')

  // ─────────────────────────────────────────────
  const handleTabChange = (tool) => {
    setActiveTool(tool)
    setResults(null)
    setRawText('')
    setFile(null)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    const files = e.dataTransfer.files
    if (files[0]) handleFileUpload(files[0])
  }, [])

  const onDragOver = (e) => e.preventDefault()

  const handleFileUpload = (f) => {
    setFile(f)
    setResults(null)
    const reader = new FileReader()
    reader.onload = (e) => setRawText(e.target.result)
    reader.readAsText(f)
  }

  const handleAction = async () => {
    if (!file) return
    setLoading(true)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('provider', provider)

    const endpoint = activeTool === 'extract' ? '/extract' : '/userstory'

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()

      if (activeTool === 'extract') {
        setResults({
          functional: data.functional || [],
          non_functional: data.non_functional || [],
        })
      } else {
        setResults(data.userstories || [])
      }
    } catch (err) {
      console.error(err)
      alert('Errore backend')
    } finally {
      setLoading(false)
    }
  }

  const downloadResults = () => {
    if (!results) return
    let lines = []

    if (activeTool === 'extract') {
      const { functional, non_functional } = results
      lines.push('=== FUNCTIONAL REQUIREMENTS ===\n')
      functional?.forEach((r) => {
        lines.push(`Sentence: ${r.sentence}`)
        r.requirements.forEach((req) => lines.push(` - ${req}`))
        lines.push('')
      })
      lines.push('\n=== NON FUNCTIONAL REQUIREMENTS ===\n')
      non_functional?.forEach((r) => {
        lines.push(`Sentence: ${r.sentence}`)
        r.requirements.forEach((req) => lines.push(` - ${req}`))
        lines.push('')
      })
    } else {
      results.forEach((r) => {
        lines.push(`Requirement: ${r.requirement}`)
        lines.push(`User story: ${r.userstory}`)
        lines.push('')
      })
    }

    const blob = new Blob([lines.join('\n')], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = activeTool === 'extract' ? 'requirements.txt' : 'userstories.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app-container" onDrop={onDrop} onDragOver={onDragOver}>
      <header>
        <h1>RECOVER</h1>
      </header>

      <NavBar active={activeTool} onChange={handleTabChange} />

      {/* PROVIDER SWITCH */}
      <div className="provider-switch">
        <button
          className={provider === 'llama' ? 'active' : ''}
          onClick={() => setProvider('llama')}
        >LLaMA</button>
        <button
          className={provider === 'genai' ? 'active' : ''}
          onClick={() => setProvider('genai')}
        >Gemini</button>
        <button
          className={provider === 'chatgpt' ? 'active' : ''}
          onClick={() => setProvider('chatgpt')}
        >ChatGPT</button>
      </div>

      <main>
        <div className="card">
          <FileDropZone
            file={file}
            onFileUpload={handleFileUpload}
          />

          {rawText && (
            <div className="file-preview">
              <h4>📄 Preview del file</h4>
              <div className="preview-box">{rawText}</div>
            </div>
          )}

          <button
            className="action-btn"
            onClick={handleAction}
            disabled={!file || loading}
          >
            {loading ? <><Loader2 className="animate-spin" /> Elaborazione…</>
                     : <><Upload /> {activeTool === 'extract' ? 'Estrai requisiti' : 'Crea userstory'}</>}
          </button>

          {results && (
            <button className="action-btn secondary" onClick={downloadResults}>
              📄 Scarica risultati
            </button>
          )}

          {/* RESULTS */}
          <div className="results">

            {activeTool === 'extract' && results && (
              <div className="columns">

                <div className="column func">
                  <h3>🧩 Functional</h3>
                  {results.functional?.length ? results.functional.map((r,i) => (
                    <div key={i} className="result-item">
                      <p className="sentence">{r.sentence}</p>
                      <ul>{r.requirements.map((req,j) => <li key={j}>{req}</li>)}</ul>
                    </div>
                  )) : <p className="none">Nessun requisito</p>}
                </div>

                <div className="column nonfunc">
                  <h3>⚙️ Non Functional</h3>
                  {results.non_functional?.length ? results.non_functional.map((r,i) => (
                    <div key={i} className="result-item">
                      <p className="sentence">{r.sentence}</p>
                      <ul>{r.requirements.map((req,j) => <li key={j}>{req}</li>)}</ul>
                    </div>
                  )) : <p className="none">Nessun requisito</p>}
                </div>

              </div>
            )}

            {activeTool === 'userstory' && results?.length && results.map((r,i) => (
              <div key={i} className="result-item">
                <p className="sentence">{r.requirement}</p>
                <p className="userstory">📝 {r.userstory}</p>
              </div>
            ))}

          </div>
        </div>
      </main>
    </div>
  )
}

export default App
