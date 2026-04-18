'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isLogin ? '/auth/login' : '/auth/signup';

    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || 'Authentication failed');
      }

      localStorage.setItem('token', data.token);
      router.push('/analyze');

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{
      minHeight: 'calc(100vh - 52px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 16px',
    }}>
      <div className="auth-form-container" style={{ width: '100%' }}>
        <h2 style={{
          textAlign: 'center',
          marginBottom: '6px',
          fontSize: '1.6rem',
        }}>
          {isLogin ? 'Sign in' : 'Create account'}
        </h2>
        <p style={{ textAlign: 'center', color: 'var(--ink-muted)', marginBottom: '24px', fontSize: '0.88rem', fontWeight: 300 }}>
          {isLogin ? 'Enter your credentials to continue.' : 'Set up your account to get started.'}
        </p>

        {error && (
          <div style={{
            background: 'rgba(192, 57, 43, 0.06)',
            border: '1px solid var(--danger)',
            color: 'var(--danger)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '18px',
            fontSize: '0.85rem',
            textAlign: 'center',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              className="input-control"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              className="input-control"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px', padding: '12px', fontSize: '0.88rem' }}
            disabled={loading}
          >
            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.85rem', color: 'var(--ink-muted)' }}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            style={{
              background: 'none', border: 'none',
              color: 'var(--accent)', fontWeight: 500,
              cursor: 'pointer', fontSize: '0.85rem',
              fontFamily: 'var(--font-body)',
            }}
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  );
}
