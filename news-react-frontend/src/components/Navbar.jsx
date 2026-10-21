import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Auth } from '../utils/auth';

export default function Navbar({ user, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    Auth.clear();
    onLogout();
    navigate('/');
  };

  return (
    <nav className="navbar" role="navigation" aria-label="Primary">
      <Link to="/" className="nav-brand" aria-label="NewsVerify home">
        <span className="brand-icon">📰</span>
        <span className="brand-text">NewsVerify</span>
      </Link>

      <div className="nav-actions">
        {user ? (
          <>
            <span className="nav-user" aria-label={`Signed in as ${user.name}`}>
              <span className="nav-avatar">
                {user.name.charAt(0).toUpperCase()}
              </span>
              {user.name.split(' ')[0]}
            </span>
            <button className="btn btn--ghost btn--sm" onClick={handleLogout}>
              Sign Out
            </button>
          </>
        ) : (
          <>
            <Link to="/login"  className="btn btn--ghost btn--sm">Sign In</Link>
            <Link to="/signup" className="btn btn--primary btn--sm">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}
