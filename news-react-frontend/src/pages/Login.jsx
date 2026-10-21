import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PasswordInput from '../components/PasswordInput';
import { Auth, findUser } from '../utils/auth';

export default function Login({ onLogin, showToast }) {
  const navigate = useNavigate();
  const [error,   setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const form     = e.currentTarget;
    const email    = form.email.value.trim();
    const password = form.password.value;

    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    try {
      // Simulate network delay; replace with real API call
      await new Promise(r => setTimeout(r, 900));

      const user = findUser(email, password);
      if (!user) throw new Error('Invalid email or password.');

      Auth.set({ name: user.name, email: user.email });
      onLogin({ name: user.name, email: user.email });
      showToast(`Welcome back, ${user.name.split(' ')[0]}! 👋`, 'success');
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page page--auth">
      <div className="auth-container">
        <div className="auth-card glass-card">
          {/* Brand */}
          <div className="auth-card__brand">
            <span className="brand-icon brand-icon--lg">📰</span>
            <span className="brand-text">NewsVerify</span>
          </div>

          <div className="auth-card__header">
            <h1 className="auth-title">Welcome back</h1>
            <p className="auth-subtitle">Sign in to continue verifying news</p>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {/* Email */}
            <div className="field-group">
              <label htmlFor="loginEmail" className="field-label">Email address</label>
              <input
                type="email"
                id="loginEmail"
                name="email"
                className="field-input"
                autoComplete="username"
                placeholder="you@example.com"
                spellCheck="false"
                autoCorrect="off"
                autoCapitalize="off"
                required
                enterKeyHint="next"
              />
            </div>

            {/* Password */}
            <div className="field-group">
              <label htmlFor="loginPassword" className="field-label">
                Password
                <a href="#" className="field-label-link" tabIndex={0}>Forgot password?</a>
              </label>
              <PasswordInput
                id="loginPassword"
                name="password"
                autoComplete="current-password"
                placeholder="Your password"
                required
                enterKeyHint="done"
              />
            </div>

            {error && (
              <div className="form-error" role="alert">{error}</div>
            )}

            <button
              type="submit"
              className="btn btn--primary btn--full btn--lg"
              disabled={loading}
            >
              {loading ? (
                <><span className="btn-spinner" aria-hidden="true" /> Signing in…</>
              ) : 'Sign In'}
            </button>
          </form>

          <div className="auth-divider"><span>or</span></div>

          <div className="auth-footer">
            Don't have an account?{' '}
            <Link to="/signup" className="link-btn">Create account →</Link>
          </div>
        </div>

        <figure className="auth-quote" aria-hidden="true">
          <blockquote>
            "The press is the best instrument for enlightening the mind of man."
          </blockquote>
          <figcaption>— Thomas Jefferson</figcaption>
        </figure>
      </div>
    </main>
  );
}
