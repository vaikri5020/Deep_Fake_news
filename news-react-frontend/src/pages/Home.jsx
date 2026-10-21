import React, { useState, useRef } from 'react';

const API_BASE = 'http://localhost:8000';

function StrengthMeter({ password }) {
  const score = scorePassword(password);
  const labels = ['—', 'Weak', 'Fair', 'Good', 'Strong'];
  const cls    = ['', 'weak', 'fair', 'good', 'strong'];
  const colors = ['rgba(232,228,216,.45)', '#c0392b', '#d4a017', '#27ae60', '#1a6b3c'];

  return (
    <div className="strength-meter" aria-label="Password strength">
      <div className="strength-bar">
        {[0,1,2,3].map(i => (
          <div
            key={i}
            className={`strength-bar__seg${i < score ? ` ${cls[score]}` : ''}`}
          />
        ))}
      </div>
      <span className="strength-label" style={{ color: colors[score] }}>
        {labels[score]}
      </span>
    </div>
  );
}

function scorePassword(pw) {
  if (!pw) return 0;
  let s = 0;
  if (pw.length >= 8)          s++;
  if (/[A-Z]/.test(pw))        s++;
  if (/[0-9]/.test(pw))        s++;
  if (/[^A-Za-z0-9]/.test(pw)) s++;
  return s;
}

// ── RESULT PANEL ──────────────────────────────────────────────
function ResultPanel({ data, onReset }) {
  const isFake = data.label.toLowerCase().includes('fake') ||
                 data.label.toLowerCase().includes('false');
  const pct = Math.round(data.confidence * 100);

  return (
    <div className="result-panel">
      <div className="result-verdict">
        <div className={`verdict-badge verdict-badge--${isFake ? 'fake' : 'real'}`}>
          {isFake ? '🚨' : '✅'}
        </div>
        <div className="verdict-meta">
          <span className="verdict-label" style={{ color: isFake ? '#ff8090' : '#2ecc71' }}>
            {data.label}
          </span>
          <div className="confidence-bar-wrap">
            <div className="confidence-bar">
              <div
                className={`confidence-bar__fill confidence-bar__fill--${isFake ? 'fake' : 'real'}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="confidence-value">{pct}% confidence</span>
          </div>
        </div>
      </div>

      <div className="result-summary">
        <h3 className="result-summary__title">Summary</h3>
        <p className="result-summary__text">{data.summary}</p>
      </div>

      <button className="btn btn--ghost btn--sm reset-btn" onClick={onReset}>
        ← Analyze Another Article
      </button>
    </div>
  );
}

// ── HOME PAGE ──────────────────────────────────────────────────
export default function Home({ showToast }) {
  const [text, setText]       = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);
  const [status, setStatus]   = useState('');

  const charOk = text.length >= 50;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!charOk) { showToast('Please enter at least 50 characters.', 'error'); return; }

    setLoading(true);
    setStatus('Analyzing…');

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
      setStatus('Analysis complete');
    } catch (err) {
      const msg = err.message.includes('Failed to fetch')
        ? 'Cannot reach the API. Is it running on localhost:8000?'
        : err.message;
      showToast(msg, 'error', 6000);
      setStatus('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setText('');
    setStatus('');
  };

  return (
    <main className="page page--active">
      <section className="hero">
        {/* Badge */}
        <div className="hero-badge">
          <span className="badge-dot" />
          AI-Powered Journalism Tool
        </div>

        {/* Title */}
        <h1 className="hero-title">
          Detect Fake News.<br />
          <em>Instantly.</em>
        </h1>
        <p className="hero-subtitle">
          Paste any news article below. Our deep-learning model analyzes credibility,
          detects misinformation, and generates a concise summary — in seconds.
        </p>

        {/* Analyzer Card */}
        <div className="analyzer-card glass-card">
          <div className="analyzer-card__header">
            <h2 className="analyzer-card__title">Analyze Article</h2>
            <div className="analyzer-status" aria-live="polite">{status}</div>
          </div>

          {!result ? (
            <form onSubmit={handleSubmit} noValidate>
              <div className="field-group">
                <label htmlFor="articleText" className="field-label">
                  Article Text
                  <span className="field-hint">(minimum 50 characters)</span>
                </label>
                <textarea
                  id="articleText"
                  className="field-input field-textarea"
                  rows={7}
                  placeholder="Paste the full news article text here…"
                  value={text}
                  onChange={e => setText(e.target.value)}
                  minLength={50}
                  required
                  enterKeyHint="done"
                  spellCheck="true"
                />
                <div className="field-counter">
                  <span style={{ color: charOk ? '#2ecc71' : 'rgba(232,228,216,.35)' }}>
                    {text.length}
                  </span>
                  {' / 50 min'}
                </div>
              </div>

              <button
                type="submit"
                className="btn btn--primary btn--full btn--lg"
                disabled={loading}
              >
                {loading ? (
                  <><span className="btn-spinner" aria-hidden="true" /> Analyzing…</>
                ) : (
                  'Analyze Article'
                )}
              </button>
            </form>
          ) : (
            <ResultPanel data={result} onReset={handleReset} />
          )}
        </div>

        {/* Feature pills */}
        <div className="feature-pills" aria-label="Key features">
          {[
            ['🤖', 'LSTM-powered detection'],
            ['⚡', 'Real-time analysis'],
            ['📋', 'Smart summarization'],
            ['🔒', 'Privacy first'],
          ].map(([icon, label]) => (
            <div className="pill" key={label}>
              <span className="pill-icon">{icon}</span> {label}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export { StrengthMeter };
