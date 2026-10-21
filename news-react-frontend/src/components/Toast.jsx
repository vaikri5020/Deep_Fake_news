import React from 'react';

const ICONS = { success: '✅', error: '❌', info: '📰' };

function Toast({ toast, onDismiss }) {
  return (
    <div className={`toast toast--${toast.type}`} role="status">
      <span className="toast__icon" aria-hidden="true">{ICONS[toast.type] ?? '💬'}</span>
      <span className="toast__msg">{toast.message}</span>
      <button className="toast__close" aria-label="Dismiss" onClick={() => onDismiss(toast.id)}>×</button>
    </div>
  );
}

export default function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="toast-container" aria-live="polite" aria-atomic="true">
      {toasts.map(t => (
        <Toast key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  );
}
