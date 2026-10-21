import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PasswordInput from '../components/PasswordInput';
import { Auth, getStoredUsers, saveUser } from '../utils/auth';
import { StrengthMeter } from './Home';

export default function Signup({ onLogin, showToast }) {
  const navigate = useNavigate();
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const form    = e.currentTarget;
    const name    = form.querySelector('#signupName').value.trim();
    const email   = form.querySelector('#signupEmail').value.trim();
    const pw      = form.querySelector('#signupPassword').value;
    const confirm = form.querySelector('#signupConfirm').value;
    const terms   = form.querySelector('#signupTerms').checked;

    if (!name || !email || !pw || !confirm) {
      setError('Please fill in all fields.'); return;
    }
    if (pw.length < 8) {
      setError('Password must be at least 8 characters.'); return;
    }
    if (pw !== confirm) {
      setError('Passwords do not match.'); return;
    }
    if (!terms) {
      setError('You must accept the Terms of Service.'); return;
    }

    setLoading(true);
    try {
      await new Promise(r => setTimeout(r, 1000));

      const users = getStoredUsers();
      if (users.find(u => u.email === email)) {
        throw new Error('An account with this email already exists.');
      }

      saveUser({ name, email, password: pw });
      Auth.set({ name, email });
      onLogin({ name, email });
      showToast(`Account created! Welcome, ${name.split(' ')[0]}! 🎉`, 'success');
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
            <h1 className="auth-title">Create account</h1>
            <p className="auth-subtitle">Join thousands fighting misinformation</p>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {/* Name */}
            <div className="field-group">
              <label htmlFor="signupName" className="field-label">Full name</label>
              <input
                type="text"
                id="signupName"
                name="name"
                className="field-input"
                autoComplete="name"
                placeholder="Alex Johnson"
                required
                enterKeyHint="next"
              />
            </div>

            {/* Email */}
            <div className="field-group">
              <label htmlFor="signupEmail" className="field-label">Email address</label>
              <input
                type="email"
                id="signupEmail"
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
              <label htmlFor="signupPassword" className="field-label">
                Password
                <span className="field-hint">(min 8 characters)</span>
              </label>
              <PasswordInput
                id="signupPassword"
                name="new-password"
                autoComplete="new-password"
                placeholder="Create a strong password"
                minLength={8}
                required
                enterKeyHint="next"
                onChange={e => setPassword(e.target.value)}
              />
              <StrengthMeter password={password} />
            </div>

            {/* Confirm */}
            <div className="field-group">
              <label htmlFor="signupConfirm" className="field-label">Confirm password</label>
              <PasswordInput
                id="signupConfirm"
                name="confirm-password"
                autoComplete="new-password"
                placeholder="Repeat your password"
                required
                enterKeyHint="done"
              />
            </div>

            {/* Terms */}
            <div className="field-group field-group--checkbox">
              <label className="checkbox-label">
                <input type="checkbox" id="signupTerms" name="terms" required />
                <span className="checkbox-custom" />
                <span>
                  I agree to the{' '}
                  <a href="#" className="link">Terms of Service</a> and{' '}
                  <a href="#" className="link">Privacy Policy</a>
                </span>
              </label>
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
                <><span className="btn-spinner" aria-hidden="true" /> Creating account…</>
              ) : 'Create Account'}
            </button>
          </form>

          <div className="auth-divider"><span>or</span></div>

          <div className="auth-footer">
            Already have an account?{' '}
            <Link to="/login" className="link-btn">Sign in →</Link>
          </div>
        </div>

        <figure className="auth-quote" aria-hidden="true">
          <blockquote>
            "A free press can be good or bad, but without freedom, the press will be bad."
          </blockquote>
          <figcaption>— Albert Camus</figcaption>
        </figure>
      </div>
    </main>
  );
}
