'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

export default function Navbar() {
  const [isClient, setIsClient] = useState(false);
  const [token, setToken] = useState(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setIsClient(true);
    setToken(localStorage.getItem('token'));
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    router.push('/');
  };

  return (
    <nav style={{
      padding: '12px 0',
      background: 'var(--ink)',
      borderBottom: 'none',
    }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link href="/" style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.3rem',
          color: 'var(--white)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <span style={{
            width: '8px', height: '8px',
            borderRadius: '50%',
            background: 'var(--accent)',
            display: 'inline-block',
          }}></span>
          Career Path Analyzer
        </Link>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          {isClient && token ? (
            <>
              <Link href="/analyze" style={{
                fontFamily: 'var(--font-ui)',
                color: 'var(--ink-subtle)',
                fontSize: '0.8rem',
                fontWeight: 600,
                letterSpacing: '0.02em',
              }}>
                Analyze
              </Link>
              <button
                onClick={handleLogout}
                style={{
                  background: 'none', border: 'none',
                  fontFamily: 'var(--font-ui)',
                  color: 'var(--ink-subtle)',
                  cursor: 'pointer',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                }}
              >
                Logout
              </button>
            </>
          ) : (
            isClient && (
              <Link href="/auth" className="btn btn-primary" style={{ padding: '8px 20px' }}>
                Sign In
              </Link>
            )
          )}
        </div>
      </div>
    </nav>
  );
}
