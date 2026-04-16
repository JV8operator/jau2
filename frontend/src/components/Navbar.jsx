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
  }, [pathname]); // Re-check on route change

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    router.push('/');
  };

  return (
    <nav style={{ padding: '14px 0', borderBottom: '1px solid var(--panel-border)', background: 'var(--panel-bg)' }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link href="/" style={{ fontSize: '1.25rem', fontWeight: '700', fontFamily: 'Outfit', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          JAU
        </Link>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          {isClient && token ? (
            <>
              <Link href="/analyze" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500 }}>
                Analyze
              </Link>
              <button 
                onClick={handleLogout} 
                style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 500 }}
              >
                Logout
              </button>
            </>
          ) : (
            isClient && (
              <Link href="/auth" className="btn btn-primary" style={{ padding: '7px 18px', fontSize: '0.85rem' }}>
                Sign In
              </Link>
            )
          )}
        </div>
      </div>
    </nav>
  );
}
