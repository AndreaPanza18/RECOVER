import React, { useState } from 'react';
import './FileDropZone.css';

const FileDropZone = ({ onFileUpload, file }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) onFileUpload(file)
  }

  const handleDragEnter = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    console.log("file in dropzone:", file)

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileUpload(files[0])
    }
  };

  return (
    <div
      className={`file-drop-zone ${isDragging ? 'dragging' : ''}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <p>Trascina un file qui oppure</p>

      <input
        type="file"
        accept=".txt"
        onChange={(e) => {
          handleFileChange(e)
          e.target.value = null
        }}
        className="mb-4"
      />

      {file && file.name && (
      <p className="text-sm text-green-400 mt-2">
        Hai selezionato: <strong>{file.name}</strong>
      </p>
      )}
    </div>
  );
};

export default FileDropZone;
