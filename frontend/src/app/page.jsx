import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="container" style={{ paddingTop: '80px', paddingBottom: '80px', minHeight: 'calc(100vh - 52px)', display: 'flex', alignItems: 'center' }}>
      <div style={{ maxWidth: '680px', margin: '0 auto', textAlign: 'center' }}>

        <p className="section-label" style={{ marginBottom: '20px', color: 'var(--accent)' }}>
          Placement Readiness
        </p>

        <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)', marginBottom: '20px', lineHeight: 1.15 }}>
          You have a <em style={{ color: 'var(--accent)' }}>clear picture</em><br />
          of where you stand.
        </h1>

        <p style={{ fontSize: '1rem', color: 'var(--ink-muted)', lineHeight: 1.7, maxWidth: '520px', margin: '0 auto 36px', fontWeight: 300 }}>
          Get a realistic placement probability, identify exact skill gaps, and follow a structured weekly roadmap — built for tier 2/3 engineering students.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/auth" className="btn btn-primary" style={{ padding: '12px 28px' }}>
            Get Started
          </Link>
          <a href="#features" className="btn btn-secondary" style={{ padding: '12px 28px' }}>
            How it works
          </a>
        </div>

        <div id="features" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '72px', textAlign: 'left' }}>

          <div className="card">
            <p className="section-label" style={{ marginBottom: '12px', color: 'var(--accent)' }}>Prediction</p>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Placement Probability</h3>
            <p style={{ color: 'var(--ink-muted)', fontSize: '0.88rem', lineHeight: 1.55, fontWeight: 300 }}>
              ML-backed scores trained on 5,000+ historical student profiles.
            </p>
          </div>

          <div className="card">
            <p className="section-label" style={{ marginBottom: '12px', color: 'var(--success)' }}>Roadmaps</p>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Weekly Action Plans</h3>
            <p style={{ color: 'var(--ink-muted)', fontSize: '0.88rem', lineHeight: 1.55, fontWeight: 300 }}>
              Task-based weekly plans built specifically around your missing skills.
            </p>
          </div>

          <div className="card">
            <p className="section-label" style={{ marginBottom: '12px', color: 'var(--warning)' }}>Benchmarking</p>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '8px' }}>Peer Comparison</h3>
            <p style={{ color: 'var(--ink-muted)', fontSize: '0.88rem', lineHeight: 1.55, fontWeight: 300 }}>
              Compare your profile against averages of successfully placed students.
            </p>
          </div>

        </div>
      </div>
    </main>
  );
}
