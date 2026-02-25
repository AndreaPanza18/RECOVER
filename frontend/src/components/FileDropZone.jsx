import React, { useRef } from 'react';
import './FileDropZone.css';

export default function FileDropZone({ file, onFileUpload }) {
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files[0]) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const triggerFileSelect = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  return (
    <div
      className="file-input-zone drop-active"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <p>Trascina un file qui oppure usa il pulsante</p>

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
