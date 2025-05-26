import React from 'react';
import './NavBar.css';

export default function NavBar({ active, onChange }) {
  return (
    <nav className="nav-bar">
      <button
        className={`nav-item ${active === 'extract' ? 'active' : ''}`}
        onClick={() => onChange('extract')}
      >
        Estrai requisiti
      </button>
      <button
        className={`nav-item ${active === 'userstory' ? 'active' : ''}`}
        onClick={() => onChange('userstory')}
      >
        Crea userstory
      </button>
    </nav>
  );
}
