import { useState } from 'react'
import FileDropZone from "./components/FileDropZone.jsx";

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])



  const handleExtract = async () => {
    if (!file) return

    setLoading(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/extract', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      setResults(data.requirements || [])
    } catch (err) {
      console.error('Errore durante la chiamata:', err)
      setResults(['Errore nella richiesta.'])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-2xl shadow">
        <h1 className="text-2xl font-bold mb-4">Estrai requisiti da file .txt</h1>

        <FileDropZone
          onFileUpload={(file) => {
            setFile(file)
            setResults([])
          }}
          file={file}
        />




        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={handleExtract}
          disabled={loading || !file}
        >
          {loading ? 'Estrazione in corso...' : 'Estrai requisiti'}
        </button>

        <div className="mt-6">
          <ul className="space-y-4">
            {results.map((r, idx) => (
                <li key={idx}>
                  <p className="font-semibold text-gray-700">📌 Frase origine:</p>
                  <p className="mb-2 italic text-gray-600">{r.sentence}</p>

                  {r.requirements.length > 0 ? (
                      <ul className="list-disc list-inside ml-4 text-black">
                        {r.requirements.map((req, ridx) => (
                            <li key={ridx}>{req}</li>
                        ))}
                      </ul>
                  ) : (
                      <p className="text-gray-400 ml-4">Nessun requisito identificato</p>
                  )}
                </li>
            ))}
          </ul>

        </div>
      </div>
    </div>
  )
}

export default App
