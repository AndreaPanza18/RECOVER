import { useState, useCallback } from 'react'
import './App.css'
import NavBar from './components/NavBar.jsx';
import FileDropZone from './components/FileDropZone.jsx';
import { Loader2, Upload } from 'lucide-react';

function App() {
  const [activeTool, setActiveTool] = useState('extract');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [provider, setProvider] = useState('llama')


  // ──────────────────────────────────────────────────────────────
  // TAB SWITCH
  // ──────────────────────────────────────────────────────────────
  const handleTabChange = (tool) => {
    setActiveTool(tool);
    setResults([]); // clear previous results when switching tab
  };

  // ──────────────────────────────────────────────────────────────
  // GLOBAL DRAG & DROP
  // ──────────────────────────────────────────────────────────────
  const onDrop = useCallback((e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files[0]) setFile(files[0]);
  }, []);
  const onDragOver = (e) => e.preventDefault();

  // ──────────────────────────────────────────────────────────────
  // BACKEND CALL
  // ──────────────────────────────────────────────────────────────
  const handleAction = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider', provider)
    const endpoint = activeTool === 'extract' ? '/extract' : '/userstory';

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });
      // 👇 AGGIUNGI QUESTO
      console.log("📦 Risposta grezza:", res);

      const data = await res.json();
      console.log("✅ Dati JSON:", data);
      setResults(
        data[activeTool === 'extract' ? 'requirements' : 'userstories'] || []
      );
    } catch (err) {
      console.error(err);
      setResults(['Errore durante la richiesta.']);
    } finally {
      setLoading(false);
    }
  };

  // ──────────────────────────────────────────────────────────────
  // DOWNLOAD TXT
  // ──────────────────────────────────────────────────────────────
  const downloadResults = () => {
    if (!results.length) return;

    let lines = [];

    if (activeTool === 'extract') {
      // Prendiamo solo le frasi che hanno almeno un requisito
      const relevant = results.filter(
        (r) => r.requirements && r.requirements.length
      );
      if (!relevant.length) return; // niente da scaricare

      relevant.forEach((r) => {
        lines.push(`Original statement: ${r.sentence}`);
        r.requirements.forEach((req) => lines.push(`  - ${req}`));
        lines.push('');
      });
    } else {
      // userstory – manteniamo tutti
      results.forEach((r) => {
        lines.push(`Requirement: ${r.requirement}`);
        lines.push(`User story: ${r.userstory}`);
        lines.push('');
      });
    }

    if (!lines.length) return;

    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeTool === 'extract' ? 'requisiti.txt' : 'userstories.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  // ──────────────────────────────────────────────────────────────
  // RENDER
  // ──────────────────────────────────────────────────────────────
  return (
      <div className="app-container" onDrop={onDrop} onDragOver={onDragOver}>
        <header>
          <h1>RECOVER</h1>
        </header>

        <NavBar active={activeTool} onChange={handleTabChange}/>
        <div className="provider-switch">
          <button
              className={provider === 'llama' ? 'active' : ''}
              onClick={() => setProvider('llama')}
          >
            LLaMA
          </button>
          <button
              className={provider === 'genai' ? 'active' : ''}
              onClick={() => setProvider('genai')}
          >
            Gemini
          </button>
        </div>


        <main>
          <div className="card">
            <FileDropZone
                file={file}
                onFileUpload={(f) => {
                  setFile(f);
                  setResults([]);
                }}
            />

            <button
                className="action-btn"
                onClick={handleAction}
                disabled={!file || loading}
            >
              {loading ? (
                  <>
                    <Loader2 className="animate-spin"/> Elaborazione…
                  </>
              ) : (
                  <>
                    <Upload/> {activeTool === 'extract' ? 'Estrai requisiti' : 'Crea userstory'}
                  </>
              )}
            </button>

            {results.length > 0 && (
                <button className="action-btn secondary" onClick={downloadResults}>
                  📄 Scarica {activeTool === 'extract' ? 'requisiti' : 'userstory'}
                </button>
            )}

            {/* RISULTATI VISIVI */}
            <div className="results">
              {activeTool === 'extract' &&
                  results.map((r, i) => (
                      <div key={i} className="result-item">
                        <p className="label">📌 Original sentence:</p>
                        <p className="sentence">{r.sentence}</p>
                        {r.requirements?.length ? (
                            <ul>
                              {r.requirements.map((req, j) => (
                                  <li key={j}>{req}</li>
                              ))}
                            </ul>
                        ) : (
                            <p className="none">Nessun requisito</p>
                        )}
                      </div>
                  ))}

              {activeTool === 'userstory' &&
                  results.map((r, i) => (
                      <div key={i} className="result-item">
                        <p className="label">📌 Requirement:</p>
                        <p className="sentence">{r.requirement}</p>
                        <p className="userstory">📝 {r.userstory}</p>
                      </div>
                  ))}
            </div>
          </div>
        </main>
      </div>
  );
}

export default App;
