import { useState, useCallback } from 'react';
import './App.css';
import NavBar from './components/NavBar.jsx';
import FileDropZone from './components/FileDropZone.jsx';
import { Loader2, Upload } from 'lucide-react';

function App() {
  const [activeTool, setActiveTool] = useState('extract'); // or 'userstory'
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  // Handle drop anywhere
  const onDrop = useCallback(e => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files[0]) setFile(files[0]);
  }, [setFile]);

  const onDragOver = e => e.preventDefault();

  const handleAction = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    const endpoint = activeTool === 'extract'
      ? '/extract'
      : '/userstory'; // cambia path per userstory

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResults(data[ activeTool === 'extract' ? 'requirements' : 'userstories' ] || []);
    } catch {
      setResults([ 'Errore nella richiesta.' ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="app-container"
      onDrop={onDrop}
      onDragOver={onDragOver}
    >
      <header>
        <h1>RECOVER</h1>
      </header>

      <NavBar active={activeTool} onChange={setActiveTool} />

      <main>
        <div className="card">
          <FileDropZone file={file} onFileUpload={setFile} />
          <button
            onClick={handleAction}
            disabled={!file || loading}
            className="action-btn"
          >
            {loading
              ? <><Loader2 className="animate-spin"/> Elaborazione…</>
              : <><Upload/> { activeTool === 'extract' ? 'Estrai requisiti' : 'Crea userstory' }</>
            }
          </button>

          <div className="results">
            {results.map((r,i) => (
              <div key={i} className="result-item">
                { activeTool === 'extract'
                  ? <>
                      <p className="label">📌 Frase origine:</p>
                      <p className="sentence">{r.sentence}</p>
                      {r.requirements?.length
                        ? <ul>{r.requirements.map((x,j)=><li key={j}>{x}</li>)}</ul>
                        : <p className="none">Nessun requisito</p>
                      }
                    </>
                  : <>
                      <p className="label">📌 Requisito:</p>
                      <p className="sentence">{r.requirement}</p>
                      <p className="userstory">📝 {r.userstory}</p>
                    </>
                }
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
