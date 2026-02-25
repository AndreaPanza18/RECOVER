import { useState } from 'react'
import './App.css'
import FileDropZone from './components/FileDropZone.jsx'
import Terminal from './components/Terminal.jsx'
import { Loader2, Upload } from 'lucide-react'

function App() {
  // ================= STEP 1 – EXTRACT =================
  const [provider1, setProvider1] = useState(null)
  const [file1, setFile1] = useState(null)
  const [rawText1, setRawText1] = useState('')
  const [results1, setResults1] = useState(null)
  const [currentStep1, setCurrentStep1] = useState(1)
  const [completedStep1, setCompletedStep1] = useState(0)
  const [logs1, setLogs1] = useState([])
  const [running1, setRunning1] = useState(false)
  const [loading1, setLoading1] = useState(false)

  // ================= STEP 2 – USER STORY =================
  const [provider2, setProvider2] = useState(null)
  const [file2, setFile2] = useState(null)
  const [rawText2, setRawText2] = useState('')
  const [results2, setResults2] = useState(null)
  const [currentStep2, setCurrentStep2] = useState(1)
  const [completedStep2, setCompletedStep2] = useState(0)
  const [logs2, setLogs2] = useState([])
  const [running2, setRunning2] = useState(false)
  const [loading2, setLoading2] = useState(false)

  // ================= FILE UPLOAD =================
  const handleFileUpload = (file, setFile, setRawText) => {
    setFile(file)
    const reader = new FileReader()
    reader.onload = (e) => setRawText(e.target.result)
    reader.readAsText(file)
  }

  // ================= BACKEND CALLS =================
  const handleExtract = async () => {
    if (!file1 || !provider1) return
    setLoading1(true)
    setRunning1(true)
    setLogs1([])
    const formData = new FormData()
    formData.append('file', file1)
    formData.append('provider', provider1)
    try {
      const res = await fetch('http://localhost:8000/extract', { method: 'POST', body: formData })
      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      let done = false
      let finalJson = ''

      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        const chunk = decoder.decode(value || new Uint8Array(), { stream: !done })
        if (chunk.startsWith('LOG:')) {
          setLogs1(prev => [...prev, chunk.replace('LOG:','').trim()])
        } else {
          finalJson += chunk
        }
      }

      const data = JSON.parse(finalJson)

      setResults1({
        functional: data.functional || [],
        non_functional: data.non_functional || []
      })
      setCompletedStep1(4)
      setCurrentStep1(4)
    } catch (err) {
      console.error(err)
      alert('Errore backend')
    } finally {
      setRunning1(false)
      setLoading1(false)
    }
  }

  const handleUserStory = async () => {
    if (!file2 || !provider2) return
    setLoading2(true)
    setRunning2(true)
    setLogs2([])
    const formData = new FormData()
    formData.append('file', file2)
    formData.append('provider', provider2)
    try {
      const res = await fetch('http://localhost:8000/userstory', { method: 'POST', body: formData })
      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      let done = false
      let finalJson = ''

      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        const chunk = decoder.decode(value || new Uint8Array(), { stream: !done })
        if (chunk.startsWith('LOG:')) {
          setLogs2(prev => [...prev, chunk.replace('LOG:','').trim()])
        } else {
          finalJson += chunk
        }
      }

      const data = JSON.parse(finalJson)

      setResults2(data.userstories || [])
      setCompletedStep2(4)
      setCurrentStep2(4)
    } catch (err) {
      console.error(err)
      alert('Errore backend')
    } finally {
      setRunning2(false)
      setLoading2(false)
    }
  }

  // ================= DOWNLOAD =================
  const downloadResults = (results, type) => {
    let lines = []
    if (type === 'extract') {
      lines.push('=== FUNCTIONAL REQUIREMENTS ===\n')
      results.functional.forEach(r => {
        lines.push(`Sentence: ${r.sentence}`)
        r.requirements.forEach(req => lines.push(` - ${req}`))
        lines.push('')
      })
      lines.push('\n=== NON FUNCTIONAL REQUIREMENTS ===\n')
      results.non_functional.forEach(r => {
        lines.push(`Sentence: ${r.sentence}`)
        r.requirements.forEach(req => lines.push(` - ${req}`))
        lines.push('')
      })
    } else {
      results.forEach(r => {
        lines.push(`Requirement: ${r.requirement}`)
        lines.push(`User story: ${r.userstory}`)
        lines.push('')
      })
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = type === 'extract' ? 'requirements.txt' : 'userstories.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  // ================= RESET =================
  const resetWizard1 = () => {
    setProvider1(null)
    setFile1(null)
    setRawText1('')
    setResults1(null)
    setLoading1(false)
    setLogs1([])
    setRunning1(false)
    setCurrentStep1(1)
    setCompletedStep1(0)
  }

  const resetWizard2 = () => {
    setProvider2(null)
    setFile2(null)
    setRawText2('')
    setResults2(null)
    setLoading2(false)
    setLogs2([])
    setRunning2(false)
    setCurrentStep2(1)
    setCompletedStep2(0)
  }

  // ================= WIZARD BUTTON =================
  const StepButton = ({ step, completed, currentStep, setStep, children }) => {

  const clickable = completed || step <= currentStep

  return (
    <button
      className={`wizard-step ${completed ? 'filled' : 'empty'}`}
      disabled={!clickable}
      onClick={() => clickable && setStep(step)}
    >
      {children}
    </button>
  )
}

  // ================= RENDER =================
  return (
    <div className="app-container">
      <header><h1>RECOVER</h1></header>
      <main>

        {/* ================= STEP 1 ================= */}
        <div className="step-header">STEP 1 – Estrazione dei Requisiti</div>
        <div className="wizard-breadcrumb">
          <StepButton step={1} completed={completedStep1>=1} currentStep={currentStep1} setStep={setCurrentStep1}>Scelta Modello</StepButton>
          <StepButton step={2} completed={completedStep1>=2} currentStep={currentStep1} setStep={setCurrentStep1}>Carica file</StepButton>
          <StepButton step={3} completed={completedStep1>=3} currentStep={currentStep1} setStep={setCurrentStep1}>Avvia Estrazione</StepButton>
          <StepButton step={4} completed={completedStep1>=4} currentStep={currentStep1} setStep={setCurrentStep1}>Requisiti Ottenuti</StepButton>
        </div>

        {completedStep1<4 && (
          <div className="step-section">
            {currentStep1===1 && (
              <div className="card-block">
                <h3 className="step-title">Scegli il modello</h3>
                <div className="provider-switch">
                  {['llama','genai','chatgpt'].map(p => (
                    <button key={p} className={provider1===p?'active':''} onClick={()=>{setProvider1(p); setCompletedStep1(1); setCurrentStep1(2)}}>
                      {p==='llama'?'LLaMA':p==='genai'?'Gemini':'ChatGPT'}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {currentStep1===2 && (
              <div className="card-block">
                <h3 className="step-title">Carica il file dei requisiti</h3>

                {!file1 && (
                  <FileDropZone
                    file={file1}
                    onFileUpload={(f)=>{
                      handleFileUpload(f,setFile1,setRawText1)
                      setCompletedStep1(2)
                    }}
                  />
                )}

                {file1 && (
                  <>
                    <button
                      className="action-btn secondary"
                      onClick={()=>{
                        setFile1(null)
                        setRawText1('')
                        setCompletedStep1(1)
                      }}
                    >
                      🔄 Sostituisci file
                    </button>

                    <div className="file-preview big-preview">
                      <pre>{rawText1}</pre>
                    </div>

                    <button
                      className="action-btn"
                      onClick={()=>{
                        setCompletedStep1(3)
                        setCurrentStep1(3)
                        handleExtract()
                      }}
                    >
                      ▶ Avvia Estrazione
                    </button>
                  </>
                )}
              </div>
            )}

            {currentStep1===3 && (
              <div className="card-block">
                <h3 className="step-title">Estrazione in corso...</h3>
                  {/*<Terminal logs={logs1} running={running1}>*/}
                <button className="action-btn">
                    {loading1 ? <><Loader2 className="animate-spin"/> Elaborazione...</> : <><Upload/> Estrai requisiti</>}
                </button>
              </div>
            )}
          </div>
        )}

        {completedStep1===4 && results1 && (
          <div className="card-block results">
            <h3 className="step-title">Risultati dell'estrazione</h3>
            <div className="columns">
              <div className="column">
                <h3>Functional Requirements</h3>
                {results1.functional.map((r,i)=>(
                  <div key={i} className="result-item">
                    <p className="sentence">{r.sentence}</p>
                    <ul>{r.requirements.map((req,j)=><li key={j}>{req}</li>)}</ul>
                  </div>
                ))}
              </div>
              <div className="column">
                <h3>Non Functional Requirements</h3>
                {results1.non_functional.map((r,i)=>(
                  <div key={i} className="result-item">
                    <p className="sentence">{r.sentence}</p>
                    <ul>{r.requirements.map((req,j)=><li key={j}>{req}</li>)}</ul>
                  </div>
                ))}
              </div>
            </div>
            <button className="action-btn secondary" onClick={()=>downloadResults(results1,'extract')}>📄 Scarica file TXT</button>
            <button className="action-btn" onClick={resetWizard1}>🔄 Nuova estrazione</button>
          </div>
        )}

        {/* ================= STEP 2 ================= */}
        <div className="step-header">STEP 2 – Creazione User Story</div>
        <div className="wizard-breadcrumb">
          <StepButton step={1} completed={completedStep2>=1} currentStep={currentStep2} setStep={setCurrentStep2}>Scelta Modello</StepButton>
          <StepButton step={2} completed={completedStep2>=2} currentStep={currentStep2} setStep={setCurrentStep2}>Carica file</StepButton>
          <StepButton step={3} completed={completedStep2>=3} currentStep={currentStep2} setStep={setCurrentStep2}>Avvia Creazione</StepButton>
          <StepButton step={4} completed={completedStep2>=4} currentStep={currentStep2} setStep={setCurrentStep2}>Userstory Ottenuta</StepButton>
        </div>

        {completedStep2<4 && (
          <div className="step-section">
            {currentStep2===1 && (
              <div className="card-block">
                <h3 className="step-title">Scegli il modello</h3>
                <div className="provider-switch">
                  {['llama','genai','chatgpt'].map(p => (
                    <button key={p} className={provider2===p?'active':''} onClick={()=>{setProvider2(p); setCompletedStep2(1); setCurrentStep2(2)}}>
                      {p==='llama'?'LLaMA':p==='genai'?'Gemini':'ChatGPT'}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {currentStep2===2 && (
              <div className="card-block">
                <h3 className="step-title">Carica il file dei requisiti</h3>

                {!file2 && (
                  <FileDropZone
                    file={file2}
                    onFileUpload={(f)=>{
                      handleFileUpload(f,setFile2,setRawText2)
                      setCompletedStep2(2)
                    }}
                  />
                )}

                {file2 && (
                  <>
                    <button
                      className="action-btn secondary"
                      onClick={()=>{
                        setFile2(null)
                        setRawText2('')
                        setCompletedStep2(1)
                      }}
                    >
                      🔄 Sostituisci file
                    </button>

                    <div className="file-preview big-preview">
                      <pre>{rawText2}</pre>
                    </div>

                    <button
                      className="action-btn"
                      onClick={()=>{
                        setCompletedStep2(3)
                        setCurrentStep2(3)
                        handleUserStory()
                      }}
                    >
                      ▶ Avvia Creazione
                    </button>
                  </>
                )}
              </div>
            )}

            {currentStep2===3 && (
              <div className="card-block">
                <h3 className="step-title">Generazione User Story in corso...</h3>
                  {/*<Terminal logs={logs2} running={running2}/> */}
                <button className="action-btn">
                  {loading2 ? <><Loader2 className="animate-spin"/> Elaborazione...</> : <><Upload/> Genera User Story</>}
                </button>
              </div>
            )}
          </div>
        )}

        {completedStep2===4 && results2 && (
          <div className="card-block results">
            <h3 className="step-title">User Story generate</h3>
            {results2.map((r,i)=>(
              <div key={i} className="result-item">
                <p className="sentence">{r.requirement}</p>
                <p className="userstory">📝 {r.userstory}</p>
              </div>
            ))}
            <button className="action-btn secondary" onClick={()=>downloadResults(results2,'userstory')}>📄 Scarica file TXT</button>
            <button className="action-btn" onClick={resetWizard2}>🔄 Nuova generazione</button>
          </div>
        )}

      </main>
    </div>
  )
}

export default App