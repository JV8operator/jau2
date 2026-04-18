'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ResultsPage() {
  const [data, setData] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const rawData = localStorage.getItem('analysisResults');
    if (!rawData) {
      router.push('/analyze');
      return;
    }
    setData(JSON.parse(rawData));
  }, [router]);

  if (!data) return <div style={{ color: 'var(--ink)', textAlign:'center', marginTop: '100px' }}>Loading...</div>;

  const scoreColor = data.category === 'High' ? 'var(--success)' : data.category === 'Moderate' ? 'var(--warning)' : 'var(--danger)';

  const panelStyle = {
    background: 'var(--white)',
    borderRadius: 'var(--radius)',
    border: '1px solid #ddd8ce',
    padding: '24px',
  };

  return (
    <div className="container" style={{ padding: '48px 24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '4px', letterSpacing: '-0.02em' }}>Analysis Results</h1>
          <p style={{ color: 'var(--ink-muted)', fontSize: '0.9rem' }}>Your placement readiness report and action plan.</p>
        </div>
        <Link href="/analyze" className="btn btn-secondary">
          Edit Profile
        </Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 280px', gap: '24px', alignItems: 'start' }}>
        
        {/* Main Content Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Insights Panel */}
          <div style={{ ...panelStyle, borderLeft: '3px solid var(--accent)' }}>
            <h3 style={{ marginBottom: '14px', fontSize: '1rem', fontWeight: 700 }}>Key Insights</h3>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {data.insights.map((insight, idx) => (
                <li key={idx} style={{ color: 'var(--ink-muted)', lineHeight: 1.55, display: 'flex', gap: '10px', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--accent)', fontWeight: 700, flexShrink: 0 }}>—</span>
                  {insight}
                </li>
              ))}
            </ul>
          </div>

          {/* Project Quality Panel */}
          {data.project_quality && (
            <div style={{ ...panelStyle, borderLeft: '3px solid #7c3aed' }}>
              <h3 style={{ marginBottom: '4px', fontSize: '1rem', fontWeight: 700 }}>Project Quality</h3>
              <p style={{ color: 'var(--ink-muted)', fontSize: '0.82rem', marginBottom: '16px' }}>
                Scored on description depth, tech stack, and real-world impact.
              </p>
              {/* Per-project scores */}
              {data.project_quality.project_scores && data.project_quality.project_scores.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '14px' }}>
                  {data.project_quality.project_scores.map((score, idx) => {
                    const col = score >= 7 ? 'var(--success)' : score >= 4 ? 'var(--warning)' : 'var(--danger)';
                    return (
                      <div key={idx} style={{ background: 'var(--surface)', padding: '10px 16px', borderRadius: 'var(--radius-sm)', border: `1px solid ${col}`, textAlign: 'center', minWidth: '70px' }}>
                        <div style={{ fontSize: '1.2rem', fontWeight: 700, color: col }}>{score}/10</div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--ink-muted)', marginTop: '2px' }}>Project {idx + 1}</div>
                      </div>
                    );
                  })}
                </div>
              )}
              {/* Feedback */}
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {data.project_quality.feedback.map((fb, idx) => (
                  <li key={idx} style={{ color: 'var(--ink-muted)', fontSize: '0.85rem', display: 'flex', gap: '8px' }}>
                    <span style={{ color: '#7c3aed', flexShrink: 0 }}>→</span>{fb}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Certificate Quality Panel */}
          {data.cert_quality && (
            <div style={{ ...panelStyle, borderLeft: '3px solid var(--warning)' }}>
              <h3 style={{ marginBottom: '4px', fontSize: '1rem', fontWeight: 700 }}>Certificate Evaluation</h3>
              <p style={{ color: 'var(--ink-muted)', fontSize: '0.82rem', marginBottom: '16px' }}>
                Only professional/technical certificates from recognised issuers are counted.
              </p>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '14px' }}>
                <div style={{ background: 'var(--surface)', padding: '10px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--success)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--success)' }}>{data.cert_quality.valid_count}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ink-muted)' }}>Recognised</div>
                </div>
                <div style={{ background: 'var(--surface)', padding: '10px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--warning)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--warning)' }}>{data.cert_quality.partial_count}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ink-muted)' }}>Partial</div>
                </div>
                <div style={{ background: 'var(--surface)', padding: '10px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--danger)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--danger)' }}>{data.cert_quality.ignored_count}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--ink-muted)' }}>Not Counted</div>
                </div>
              </div>
              {data.cert_quality.feedback.length > 0 && (
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {data.cert_quality.feedback.map((fb, idx) => (
                    <li key={idx} style={{ color: 'var(--ink-muted)', fontSize: '0.85rem', display: 'flex', gap: '8px' }}>
                      <span style={{ color: 'var(--warning)', flexShrink: 0 }}>→</span>{fb}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Roadmap */}
          <div style={panelStyle}>
            <h3 style={{ marginBottom: '20px', fontSize: '1.15rem', fontWeight: 700 }}>Action Roadmap</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative' }}>
              {/* Timeline line */}
              <div style={{ position: 'absolute', left: '13px', top: '16px', bottom: '16px', width: '1.5px', background: '#ddd8ce', zIndex: 0 }}></div>
              
              {data.roadmap.map((step, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '18px', zIndex: 1, position: 'relative' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--white)', border: '2px solid var(--accent)', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.72rem', fontWeight: '700', color: 'var(--accent)' }}>
                    {idx + 1}
                  </div>
                  <div style={{ background: 'var(--surface)', padding: '16px', borderRadius: 'var(--radius-sm)', flexGrow: 1, border: '1px solid #ddd8ce' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
                      <h4 style={{ color: 'var(--ink)', fontSize: '0.95rem', fontWeight: 600 }}>{step.skill}</h4>
                      <span style={{ color: 'var(--accent)', fontSize: '0.75rem', fontWeight: 600, background: 'rgba(26, 86, 219, 0.06)', padding: '3px 8px', borderRadius: 'var(--radius-sm)' }}>{step.week}</span>
                    </div>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                      {step.tasks.map((task, tidx) => (
                        <li key={tidx} style={{ color: 'var(--ink-muted)', fontSize: '0.85rem', marginBottom: '4px', display: 'flex', gap: '8px' }}>
                          <span style={{ opacity: 0.4, flexShrink: 0 }}>→</span> {task}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Benchmarks */}
          <div style={panelStyle}>
            <h3 style={{ marginBottom: '20px', fontSize: '1.15rem', fontWeight: 700 }}>Benchmarking vs Placed Students</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px' }}>
              {Object.keys(data.benchmarks.placed_averages).map((metric) => {
                const isAhead = data.benchmarks.indicators[metric] === "ahead";
                const gapColor = isAhead ? 'var(--success)' : 'var(--danger)';
                const gapText = isAhead ? '+' : '';
                return (
                  <div key={metric} style={{ background: 'var(--surface)', padding: '16px', borderRadius: 'var(--radius-sm)', border: '1px solid #ddd8ce' }}>
                    <div style={{ textTransform: 'capitalize', color: 'var(--ink-muted)', fontSize: '0.8rem', marginBottom: '6px' }}>{metric}</div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                      <div style={{ fontSize: '1.5rem', fontWeight: '700', fontFamily: 'Outfit' }}>{data.benchmarks.placed_averages[metric]}</div>
                      <div style={{ color: gapColor, fontSize: '0.82rem', fontWeight: 600 }}>
                        {gapText}{data.benchmarks.gaps[metric]} vs avg
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Sidebar Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Main Score Card */}
          <div style={{ ...panelStyle, textAlign: 'center' }}>
            <div style={{ marginBottom: '6px', color: 'var(--ink-muted)', fontSize: '0.82rem', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.04em' }}>Readiness Score</div>
            
            <div style={{ position: 'relative', width: '140px', height: '140px', margin: '0 auto 16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="140" height="140" viewBox="0 0 140 140" style={{ transform: 'rotate(-90deg)' }}>
                <circle cx="70" cy="70" r="60" fill="none" stroke="#ddd8ce" strokeWidth="8" />
                <circle cx="70" cy="70" r="60" fill="none" stroke={scoreColor} strokeWidth="8" 
                  strokeDasharray={`${2 * Math.PI * 60}`} 
                  strokeDashoffset={`${2 * Math.PI * 60 * (1 - (data.readiness_score/100))}`}
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
                />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: '2.2rem', fontWeight: 700, fontFamily: 'Outfit', letterSpacing: '-0.02em' }}>{data.readiness_score}</span>
              </div>
            </div>
            
            <div style={{ color: scoreColor, fontWeight: 600, fontSize: '1rem', marginBottom: '16px' }}>{data.category} Readiness</div>
            
            <div style={{ background: 'var(--surface)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--ink-muted)', marginBottom: '2px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>Placement Likelihood</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--ink)' }}>{data.placement_probability}%</div>
            </div>
          </div>

          {/* Skill Gaps Card */}
          <div style={panelStyle}>
            <h3 style={{ marginBottom: '4px', fontSize: '0.95rem', fontWeight: 700 }}>Skill Analysis</h3>
            <p style={{ color: 'var(--ink-muted)', fontSize: '0.78rem', marginBottom: '14px' }}>{data.skill_match_percentage}% match</p>
            {data.tier_breakdown && (
              <p style={{ color: 'var(--ink-muted)', fontSize: '0.75rem', marginBottom: '14px', lineHeight: 1.5 }}>
                Core: {data.tier_breakdown.tier1_matched}/{data.tier_breakdown.tier1_total} &nbsp;·&nbsp;
                Strong: {data.tier_breakdown.tier2_matched}/{data.tier_breakdown.tier2_total} &nbsp;·&nbsp;
                Bonus: {data.tier_breakdown.tier3_matched}/{data.tier_breakdown.tier3_total}
              </p>
            )}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--ink-muted)', marginBottom: '6px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.03em' }}>Matched</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {data.matched_skills.map(s => (
                  <span key={s} style={{ background: 'rgba(5, 150, 105, 0.08)', color: 'var(--success)', padding: '3px 8px', borderRadius: 'var(--radius-sm)', fontSize: '0.78rem', fontWeight: 500 }}>{s}</span>
                ))}
                {data.matched_skills.length === 0 && <span style={{color:'var(--ink-muted)', fontSize:'0.8rem'}}>None</span>}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--ink-muted)', marginBottom: '6px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.03em' }}>Missing</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {data.missing_skills.map(s => (
                  <span key={s} style={{ background: 'rgba(220, 38, 38, 0.08)', color: 'var(--danger)', padding: '3px 8px', borderRadius: 'var(--radius-sm)', fontSize: '0.78rem', fontWeight: 500 }}>{s}</span>
                ))}
                {data.missing_skills.length === 0 && <span style={{color:'var(--ink-muted)', fontSize:'0.8rem'}}>None</span>}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
