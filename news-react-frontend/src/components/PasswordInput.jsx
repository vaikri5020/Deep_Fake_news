import React, { useState, useRef } from 'react';

export default function PasswordInput({ id, name, placeholder, autoComplete, required, minLength, enterKeyHint, onChange }) {
  const [visible, setVisible] = useState(false);
  const inputRef = useRef(null);

  const toggle = () => {
    setVisible(v => !v);
    // Keep focus on input after toggle
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  return (
    <div className="password-wrap">
      <input
        ref={inputRef}
        type={visible ? 'text' : 'password'}
        id={id}
        name={name}
        className="field-input"
        autoComplete={autoComplete}
        placeholder={placeholder}
        required={required}
        minLength={minLength}
        enterKeyHint={enterKeyHint}
        onChange={onChange}
        spellCheck="false"
      />
      <button
        type="button"
        className="password-toggle"
        aria-label={visible ? 'Hide password' : 'Show password'}
        onClick={toggle}
      >
        <svg className="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          {visible ? (
            <>
              <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94" />
              <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </>
          ) : (
            <>
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </>
          )}
        </svg>
      </button>
    </div>
  );
}
