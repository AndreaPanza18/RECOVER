import React, { useRef } from 'react';
import './FileDropZone.css';

export default function FileDropZone({ file, onFileUpload }) {
  const fileInputRef = useRef(null);

  const triggerFileSelect = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  return (
    <div className="file-input-zone">
      <p>Trascina un file o usa il pulsante qui sotto</p>

      <button className="fake-upload-btn" onClick={triggerFileSelect}>
        📁 Seleziona file
      </button>

      <input
        type="file"
        accept=".txt"
        ref={fileInputRef}
        onChange={(e) => {
          if (e.target.files[0]) onFileUpload(e.target.files[0]);
          e.target.value = null;
        }}
        className="hidden-file-input"
      />

      {file && (
        <p className="selected">
          Hai selezionato: <strong>{file.name}</strong>
        </p>
      )}
    </div>
  );
}
