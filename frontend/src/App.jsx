import { useState, useCallback } from 'react'
import './App.css'
import NavBar from './components/NavBar.jsx';
import FileDropZone from './components/FileDropZone.jsx';
import { Loader2, Upload } from 'lucide-react';

function App() {
  const [activeTool, setActiveTool] = useState('extract'); // 'extract' | 'userstory'
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  /*
   * Cambio tab
   * ------------------------------------------------------------------
   * Ogni volta che l'utente cambia sezione, azzeriamo i risultati così
   * da non mostrare le vecchie card e prevenire confusione.
   */
  const handleTabChange = (tool) => {
    setActiveTool(tool);
    setResults([]); // pulisci le card
  };

  // Drag‑n‑drop sull'intero schermo
  const onDrop = useCallback(
    (e) => {
      e.preventDefault();
      const files = e.dataTransfer.files;
      if (files[0]) setFile(files[0]);
    },
    [setFile]
  );

  const onDragOver = (e) => e.preventDefault();

  /*
   * Chiamata al backend per estrarre requisiti o user story
   */
  const handleAction = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    const endpoint = activeTool === 'extract' ? '/extract' : '/userstory';

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResults(
        data[
          activeTool === 'extract' ? 'requirements' : 'userstories'
        ] || []
      );
    } catch (err) {
      console.error(err);
      setResults(['Errore durante la richiesta.']);
    } finally {
      setLoading(false);
    }
  };

  /*
   * Download .txt dei risultati
   */
  const downloadResults = () => {
    const extracted = activeTool === 'extract'
      ? results.flatMap(r => r.requirements || [])
      : results.map(r => r.userstory);

    if (!extracted.length) return;

    const blob = new Blob([extracted.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeTool === 'extract' ? 'requisiti.txt' : 'userstories.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="app-container"
      onDrop={onDrop}
      onDragOver={onDragOver}
    >
      <header>
        <h1>🔍 RECOVER</h1>
      </header>

      <NavBar active={activeTool} onChange={handleTabChange} />

      <main>
        <div className="card">
          <FileDropZone
            file={file}
            onFileUpload={f => {
              setFile(f);
              setResults([]);
            }}
          />

          <button
            onClick={handleAction}
            disabled={!file || loading}
            className="action-btn"
          >
            {loading ? (
              <><Loader2 className="animate-spin" /> Elaborazione…</>
            ) : (
              <><Upload /> {activeTool === 'extract' ? 'Estrai requisiti' : 'Crea userstory'}</>
            )}
          </button>

          {results.length > 0 && (
            <button
              onClick={downloadResults}
              className="action-btn secondary"
            >
              📄 Scarica {activeTool === 'extract' ? 'requisiti' : 'userstory'}
            </button>
          )}

          {/* Render risultati */}
          <div className="results">
            {activeTool === 'extract' &&
              results.map((r, i) => (
                <div key={i} className="result-item">
                  <p className="label">📌 Frase origine:</p>
                  <p className="sentence">{r.sentence}</p>
                  {r.requirements?.length ? (
                    <ul>
                      {r.requirements.map((req, j) => <li key={j}>{req}</li>)}
                    </ul>
                  ) : <p className="none">Nessun requisito</p>}
                </div>
              ))}

            {activeTool === 'userstory' &&
              results.map((r, i) => (
                <div key={i} className="result-item">
                  <p className="label">📌 Requisito:</p>
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
