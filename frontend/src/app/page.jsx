import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="container" style={{ paddingTop: '100px', paddingBottom: '80px', minHeight: 'calc(100vh - 85px)', display: 'flex', alignItems: 'center' }}>
      <div style={{ maxWidth: '720px', margin: '0 auto', textAlign: 'center' }}>
        
        <p style={{ fontSize: '0.8rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--accent-primary)', marginBottom: '20px' }}>
          Placement Readiness Platform
        </p>

        <h1 style={{ fontSize: 'clamp(2.2rem, 5vw, 3.5rem)', lineHeight: 1.15, marginBottom: '20px', fontWeight: '800', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          Know where you stand.<br />
          Know what to do next.
        </h1>
        
        <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '40px', maxWidth: '560px', margin: '0 auto 40px' }}>
          Get a realistic placement probability, identify exact skill gaps, and follow a structured weekly roadmap — built for tier 2/3 engineering students.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <Link href="/auth" className="btn btn-primary" style={{ padding: '12px 28px' }}>
            Get Started
          </Link>
          <a href="#features" className="btn btn-secondary" style={{ padding: '12px 28px' }}>
            How it works
          </a>
        </div>

        <div id="features" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginTop: '80px', textAlign: 'left' }}>
          
          <div style={{ background: 'var(--panel-bg)', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--panel-border)' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-sm)', background: 'rgba(26, 86, 219, 0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <h3 style={{ marginBottom: '8px', fontSize: '1.05rem', fontWeight: 700 }}>Placement Prediction</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>ML-backed likelihood scores trained on 5,000+ historical student profiles.</p>
          </div>
          
          <div style={{ background: 'var(--panel-bg)', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--panel-border)' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-sm)', background: 'rgba(5, 150, 105, 0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            </div>
            <h3 style={{ marginBottom: '8px', fontSize: '1.05rem', fontWeight: 700 }}>Weekly Roadmaps</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>Task-based weekly plans built around your specific missing skills.</p>
          </div>

          <div style={{ background: 'var(--panel-bg)', padding: '24px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--panel-border)' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: 'var(--radius-sm)', background: 'rgba(217, 119, 6, 0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--warning)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            </div>
            <h3 style={{ marginBottom: '8px', fontSize: '1.05rem', fontWeight: 700 }}>Benchmarking</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>Compare your profile against averages of successfully placed students.</p>
          </div>
        </div>
      </div>
    </main>
  );
}
