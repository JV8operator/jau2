'use client';
import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function InputPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [error, setError] = useState('');
  const [cgpaScale, setCgpaScale] = useState(10);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadConfirmation, setUploadConfirmation] = useState(null); // { filename, skillsCount, cgpa }
  const fileInputRef = useRef(null);

  // "I have none" toggles
  const [noInternships, setNoInternships] = useState(false);
  const [noProjects, setNoProjects] = useState(false);
  const [noCertificates, setNoCertificates] = useState(false);

  const [formData, setFormData] = useState({
    branch: 'CSE',
    cgpa: '',
    internships: [],
    projects: [],
    certificates: [],
    // 3 separate skill category fields
    skillsLanguages: '',
    skillsFrameworks: '',
    skillsTools: '',
  });

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      router.push('/auth');
    }
  }, [router]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // ----- Dynamic Internship Handlers -----
  const addInternship = () =>
    setFormData({ ...formData, internships: [...formData.internships, { company: '', role: '', duration: '' }] });
  const updateInternship = (index, field, value) => {
    const arr = [...formData.internships];
    arr[index][field] = value;
    setFormData({ ...formData, internships: arr });
  };
  const removeInternship = (index) =>
    setFormData({ ...formData, internships: formData.internships.filter((_, i) => i !== index) });

  // ----- Dynamic Project Handlers -----
  const addProject = () =>
    setFormData({ ...formData, projects: [...formData.projects, { title: '', description: '' }] });
  const updateProject = (index, field, value) => {
    const arr = [...formData.projects];
    arr[index][field] = value;
    setFormData({ ...formData, projects: arr });
  };
  const removeProject = (index) =>
    setFormData({ ...formData, projects: formData.projects.filter((_, i) => i !== index) });

  // ----- Dynamic Certificate Handlers -----
  const addCertificate = () =>
    setFormData({ ...formData, certificates: [...formData.certificates, { title: '', mode: 'type', uploading: false, issuer: '', uploaded: false, filename: '' }] });
  const updateCertificate = (index, field, value) => {
    const arr = [...formData.certificates];
    arr[index][field] = value;
    setFormData({ ...formData, certificates: arr });
  };
  const removeCertificate = (index) =>
    setFormData({ ...formData, certificates: formData.certificates.filter((_, i) => i !== index) });

  // ----- Certificate PDF Upload -----
  const uploadCertificate = async (index, file) => {
    const arr = [...formData.certificates];
    arr[index].uploading = true;
    setFormData(prev => ({ ...prev, certificates: arr }));
    try {
      const data = new FormData();
      data.append('document', file);
      data.append('type', 'certificate');
      data.append('branch', formData.branch);
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/upload-document`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: data
      });
      if (!res.ok) throw new Error('Upload failed');
      const result = await res.json();
      const updated = [...formData.certificates];
      updated[index].title = result.cert_title || '';
      updated[index].issuer = result.cert_issuer || '';
      updated[index].uploading = false;
      updated[index].uploaded = true;
      updated[index].filename = file.name;
      setFormData(prev => ({ ...prev, certificates: updated }));
    } catch (err) {
      setError(err.message);
      const updated = [...formData.certificates];
      updated[index].uploading = false;
      setFormData(prev => ({ ...prev, certificates: updated }));
    }
  };

  // ----- Resume Drag & Drop -----
  const handleDragOver = (e) => { e.preventDefault(); setIsDragOver(true); };
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragOver(false); };
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) uploadResume(e.dataTransfer.files[0]);
  };
  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) uploadResume(e.target.files[0]);
  };

  const uploadResume = async (file) => {
    setUploadLoading(true);
    setError('');
    setUploadConfirmation(null);
    try {
      const data = new FormData();
      data.append('document', file);
      data.append('type', 'resume');
      data.append('branch', formData.branch);
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_URL}/upload-document`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: data
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Upload failed');
      }
      const result = await res.json();
      const updates = {};

      // Auto-fill CGPA
      if (result.cgpa) {
        updates.cgpa = result.cgpa;
        setCgpaScale(result.cgpa_scale || 10);
      }

      // Auto-fill skills into 3 categorized boxes (merge with existing)
      if (result.skills_categorized) {
        const { languages = [], frameworks = [], tools = [] } = result.skills_categorized;

        const mergeSkills = (existing, incoming) => {
          const current = existing.split(',').map(s => s.trim()).filter(s => s);
          const merged = [...new Set([...current, ...incoming])];
          return merged.join(', ');
        };

        if (languages.length > 0)
          updates.skillsLanguages = mergeSkills(formData.skillsLanguages, languages);
        if (frameworks.length > 0)
          updates.skillsFrameworks = mergeSkills(formData.skillsFrameworks, frameworks);
        if (tools.length > 0)
          updates.skillsTools = mergeSkills(formData.skillsTools, tools);
      }

      setFormData(prev => ({ ...prev, ...updates }));

      // Set a quiet text confirmation — no popup
      setUploadConfirmation({
        filename: file.name,
        skillsCount: result.skills_count || 0,
        cgpa: result.cgpa || null,
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      const cgpaOn10 = cgpaScale === 4
        ? Math.round((parseFloat(formData.cgpa) / 4.0) * 10 * 100) / 100
        : parseFloat(formData.cgpa);

      // Combine the 3 skill fields into one comma-separated string for the backend
      const combinedSkills = [
        formData.skillsLanguages,
        formData.skillsFrameworks,
        formData.skillsTools
      ].filter(s => s.trim()).join(', ');

      const payload = {
        branch: formData.branch,
        cgpa: cgpaOn10,
        skills: combinedSkills,
        internships: noInternships ? [] : formData.internships,
        projects: noProjects ? [] : formData.projects,
        certificates: noCertificates ? [] : formData.certificates,
      };

      const res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (res.status === 401) {
        localStorage.removeItem('token');
        router.push('/auth');
        return;
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to analyze data');

      localStorage.setItem('analysisResults', JSON.stringify(data));
      router.push('/results');
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  // ---- Shared Styles ----
  const noneToggleStyle = {
    display: 'flex', alignItems: 'center', gap: '10px',
    padding: '10px 14px', borderRadius: 'var(--radius-sm)',
    border: '1px solid #ddd8ce', background: 'var(--surface)',
    cursor: 'pointer', transition: 'all 0.15s ease',
    fontSize: '0.85rem', color: 'var(--ink-muted)', userSelect: 'none'
  };
  const noneToggleActiveStyle = {
    ...noneToggleStyle, background: 'rgba(192, 57, 43, 0.04)',
    borderColor: 'var(--danger)', color: 'var(--danger)'
  };
  const sectionLabelStyle = {
    fontFamily: "'Times New Roman', Times, serif",
    fontSize: '0.72rem', fontWeight: 600, color: 'var(--ink-subtle)',
    textTransform: 'uppercase', letterSpacing: '0.08em'
  };
  const cardStyle = {
    background: 'var(--surface)', padding: '14px',
    borderRadius: 'var(--radius)', border: '1px solid #ddd8ce'
  };
  const sectionHeaderStyle = {
    display: 'flex', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: '10px'
  };

  const Checkbox = ({ checked }) => (
    <span style={{
      width: '18px', height: '18px', borderRadius: '4px',
      border: checked ? 'none' : '1.5px solid #c8cdd4',
      background: checked ? 'var(--danger)' : '#fff',
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      flexShrink: 0, transition: 'all 0.15s ease'
    }}>
      {checked && <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>}
    </span>
  );

  return (
    <div className="container" style={{ padding: '48px 24px' }}>
      <div style={{ maxWidth: '760px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '8px' }}>Analyze Profile</h1>
        <p style={{ color: 'var(--ink-muted)', marginBottom: '32px', fontSize: '0.95rem' }}>
          Enter your academic and skill details to generate a placement readiness report.
        </p>

        {error && (
          <div style={{ background: 'rgba(220, 38, 38, 0.06)', border: '1px solid var(--danger)', color: 'var(--danger)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', marginBottom: '20px', fontSize: '0.85rem' }}>
            {error}
          </div>
        )}

        {/* ── Resume Upload Zone ── */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
          style={{
            background: isDragOver ? 'rgba(46, 91, 255, 0.03)' : 'var(--white)',
            border: `1.5px dashed ${isDragOver ? 'var(--accent)' : '#ddd8ce'}`,
            borderRadius: 'var(--radius)',
            padding: '28px 20px',
            textAlign: 'center',
            marginBottom: uploadConfirmation ? '12px' : '24px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <div style={{ marginBottom: '8px' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          {uploadLoading ? (
            <div style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.9rem' }}>Reading document...</div>
          ) : (
            <>
              <div style={{ marginBottom: '4px', fontSize: '0.95rem', fontWeight: 600, color: 'var(--ink)' }}>
                Drop your resume here, or click to browse
              </div>
              <div style={{ color: 'var(--ink-subtle)', fontSize: '0.82rem' }}>
                PDF only — CGPA and skills will be auto-extracted
              </div>
            </>
          )}
          <input type="file" ref={fileInputRef} onChange={handleFileSelect} accept=".pdf" style={{ display: 'none' }} />
        </div>

        {/* ── Upload Confirmation (quiet, inline, no popup) ── */}
        {uploadConfirmation && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            background: 'rgba(5, 150, 105, 0.05)',
            border: '1px solid var(--success)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 14px',
            marginBottom: '24px',
            fontSize: '0.85rem',
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span style={{ color: 'var(--success)', fontWeight: 600 }}>
              {uploadConfirmation.filename} uploaded.
            </span>
            <span style={{ color: 'var(--ink-muted)' }}>
              {[
                uploadConfirmation.skillsCount ? `${uploadConfirmation.skillsCount} skills detected` : null,
                uploadConfirmation.cgpa ? `CGPA set to ${uploadConfirmation.cgpa}` : null,
              ].filter(Boolean).join(' · ')}
              {' — please review and edit below.'}
            </span>
          </div>
        )}

        {/* ── Main Form ── */}
        <div style={{ background: 'var(--white)', padding: '28px', borderRadius: 'var(--radius)', border: '1px solid #ddd8ce' }}>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '20px' }}>

            {/* Branch + CGPA */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="input-group" style={{ marginBottom: 0 }}>
                <label>Branch</label>
                <select className="input-control" name="branch" value={formData.branch} onChange={handleChange}>
                  <option value="CSE">Computer Science (CSE)</option>
                  <option value="IT">Information Tech (IT)</option>
                  <option value="ECE">Electronics (ECE)</option>
                </select>
              </div>
              <div className="input-group" style={{ marginBottom: 0 }}>
                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span>CGPA</span>
                  <span style={{ display: 'flex', gap: '2px', background: 'var(--surface)', borderRadius: 'var(--radius-sm)', padding: '2px', border: '1px solid #ddd8ce' }}>
                    {[10, 4].map(s => (
                      <button key={s} type="button" onClick={() => setCgpaScale(s)} style={{
                        padding: '2px 8px', borderRadius: '4px', border: 'none', cursor: 'pointer',
                        fontSize: '0.72rem', fontWeight: 600,
                        background: cgpaScale === s ? 'var(--accent)' : 'transparent',
                        color: cgpaScale === s ? '#fff' : 'var(--ink-muted)',
                        transition: 'all 0.15s ease'
                      }}>/{s}</button>
                    ))}
                  </span>
                </label>
                <input
                  type="number" step="0.01" min="0" max={cgpaScale}
                  className="input-control" name="cgpa"
                  placeholder={cgpaScale === 4 ? 'e.g. 3.64' : 'e.g. 8.25'}
                  value={formData.cgpa} onChange={handleChange} required
                />
                {cgpaScale === 4 && formData.cgpa && (
                  <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: 'var(--ink-muted)' }}>
                    ≈ {Math.round((parseFloat(formData.cgpa) / 4.0) * 10 * 100) / 100} on 10-point scale
                  </p>
                )}
              </div>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid #ddd8ce', margin: '4px 0' }} />

            {/* ── SKILLS — 3 Categorized Boxes ── */}
            <div>
              <div style={{ marginBottom: '10px' }}>
                <label style={sectionLabelStyle}>Skills</label>
                <p style={{ color: 'var(--ink-muted)', fontSize: '0.78rem', margin: '2px 0 0' }}>
                  Auto-filled from your resume. Add or edit as needed — use comma separated values.
                </p>
              </div>
              <div style={{ display: 'grid', gap: '12px' }}>
                <div className="input-group" style={{ marginBottom: 0 }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--ink-muted)', fontWeight: 600 }}>Languages</label>
                  <input
                    type="text" className="input-control"
                    name="skillsLanguages"
                    placeholder="Python, Java, C++, SQL..."
                    value={formData.skillsLanguages}
                    onChange={handleChange}
                  />
                </div>
                <div className="input-group" style={{ marginBottom: 0 }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--ink-muted)', fontWeight: 600 }}>Frameworks & Libraries</label>
                  <input
                    type="text" className="input-control"
                    name="skillsFrameworks"
                    placeholder="React, Django, TensorFlow, Pandas..."
                    value={formData.skillsFrameworks}
                    onChange={handleChange}
                  />
                </div>
                <div className="input-group" style={{ marginBottom: 0 }}>
                  <label style={{ fontSize: '0.8rem', color: 'var(--ink-muted)', fontWeight: 600 }}>Tools & Databases</label>
                  <input
                    type="text" className="input-control"
                    name="skillsTools"
                    placeholder="Git, Docker, PostgreSQL, AWS..."
                    value={formData.skillsTools}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid #ddd8ce', margin: '4px 0' }} />

            {/* ── INTERNSHIPS ── */}
            <div>
              <div style={sectionHeaderStyle}>
                <div>
                  <label style={sectionLabelStyle}>Internships</label>
                  <p style={{ color: 'var(--ink-muted)', fontSize: '0.78rem', margin: '2px 0 0' }}>
                    Companies are verified against a database of 100+ institutions.
                  </p>
                </div>
                {!noInternships && (
                  <button type="button" onClick={addInternship} className="btn btn-secondary" style={{ padding: '5px 10px', fontSize: '0.8rem', flexShrink: 0 }}>+ Add</button>
                )}
              </div>
              <div onClick={() => { setNoInternships(!noInternships); if (!noInternships) setFormData(prev => ({ ...prev, internships: [] })); }} style={noInternships ? noneToggleActiveStyle : noneToggleStyle}>
                <Checkbox checked={noInternships} />
                <span>I don't have any internships yet</span>
              </div>
              {!noInternships && (
                <div style={{ display: 'grid', gap: '12px', marginTop: '10px' }}>
                  {formData.internships.map((intern, idx) => (
                    <div key={idx} style={cardStyle}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--ink-muted)' }}>Internship {idx + 1}</span>
                        <button type="button" onClick={() => removeInternship(idx)} style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '0.82rem' }}>Remove</button>
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '10px' }}>
                        <div className="input-group" style={{ marginBottom: 0 }}>
                          <input type="text" className="input-control" placeholder="Company (e.g. Google, TCS)" value={intern.company} onChange={(e) => updateInternship(idx, 'company', e.target.value)} required />
                        </div>
                        <div className="input-group" style={{ marginBottom: 0 }}>
                          <input type="text" className="input-control" placeholder="Role (e.g. SDE Intern)" value={intern.role} onChange={(e) => updateInternship(idx, 'role', e.target.value)} required />
                        </div>
                      </div>
                      <div className="input-group" style={{ marginBottom: 0 }}>
                        <select className="input-control" value={intern.duration} onChange={(e) => updateInternship(idx, 'duration', e.target.value)} required>
                          <option value="">Duration</option>
                          <option value="1 month">1 Month</option>
                          <option value="2 months">2 Months</option>
                          <option value="3 months">3 Months</option>
                          <option value="4 months">4 Months</option>
                          <option value="6 months">6 Months</option>
                          <option value="1 year">1 Year</option>
                          <option value="2 years">2+ Years</option>
                        </select>
                      </div>
                    </div>
                  ))}
                  {formData.internships.length === 0 && (
                    <div style={{ color: 'var(--ink-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '6px 0' }}>No internships added. Click "+ Add" above.</div>
                  )}
                </div>
              )}
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid #ddd8ce', margin: '4px 0' }} />

            {/* ── PROJECTS ── */}
            <div>
              <div style={sectionHeaderStyle}>
                <label style={sectionLabelStyle}>Projects</label>
                {!noProjects && (
                  <button type="button" onClick={addProject} className="btn btn-secondary" style={{ padding: '5px 10px', fontSize: '0.8rem' }}>+ Add</button>
                )}
              </div>
              <div onClick={() => { setNoProjects(!noProjects); if (!noProjects) setFormData(prev => ({ ...prev, projects: [] })); }} style={noProjects ? noneToggleActiveStyle : noneToggleStyle}>
                <Checkbox checked={noProjects} />
                <span>I don't have any projects yet</span>
              </div>
              {!noProjects && (
                <div style={{ display: 'grid', gap: '12px', marginTop: '10px' }}>
                  {formData.projects.map((proj, idx) => (
                    <div key={idx} style={cardStyle}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--ink-muted)' }}>Project {idx + 1}</span>
                        <button type="button" onClick={() => removeProject(idx)} style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '0.82rem' }}>Remove</button>
                      </div>
                      <div className="input-group" style={{ marginBottom: '10px' }}>
                        <input type="text" className="input-control" placeholder="Project name" value={proj.title} onChange={(e) => updateProject(idx, 'title', e.target.value)} required />
                      </div>
                      <div className="input-group" style={{ marginBottom: 0 }}>
                        <textarea className="input-control" placeholder="Brief description — mention technologies used, what it does, and if deployed" rows="3" value={proj.description} onChange={(e) => updateProject(idx, 'description', e.target.value)} style={{ resize: 'vertical' }} required />
                      </div>
                    </div>
                  ))}
                  {formData.projects.length === 0 && (
                    <div style={{ color: 'var(--ink-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '6px 0' }}>No projects added. Click "+ Add" above.</div>
                  )}
                </div>
              )}
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid #ddd8ce', margin: '4px 0' }} />

            {/* ── CERTIFICATES ── */}
            <div>
              <div style={sectionHeaderStyle}>
                <div>
                  <label style={sectionLabelStyle}>Certificates</label>
                  <p style={{ color: 'var(--ink-muted)', fontSize: '0.78rem', margin: '2px 0 0' }}>Type the name or upload a PDF — both supported per entry.</p>
                </div>
                {!noCertificates && (
                  <button type="button" onClick={addCertificate} className="btn btn-secondary" style={{ padding: '5px 10px', fontSize: '0.8rem', flexShrink: 0 }}>+ Add</button>
                )}
              </div>
              <div onClick={() => { setNoCertificates(!noCertificates); if (!noCertificates) setFormData(prev => ({ ...prev, certificates: [] })); }} style={noCertificates ? noneToggleActiveStyle : noneToggleStyle}>
                <Checkbox checked={noCertificates} />
                <span>I don't have any certificates yet</span>
              </div>
              {!noCertificates && (
                <div style={{ display: 'grid', gap: '12px', marginTop: '10px' }}>
                  {formData.certificates.map((cert, idx) => (
                    <div key={idx} style={cardStyle}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--ink-muted)' }}>Certificate {idx + 1}</span>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          <span style={{ display: 'flex', gap: '2px', background: 'var(--white)', borderRadius: 'var(--radius-sm)', padding: '2px', border: '1px solid #ddd8ce' }}>
                            {['type', 'upload'].map(m => (
                              <button key={m} type="button" onClick={() => updateCertificate(idx, 'mode', m)} style={{
                                padding: '2px 8px', borderRadius: '4px', border: 'none', cursor: 'pointer',
                                fontSize: '0.72rem', fontWeight: 600,
                                background: cert.mode === m ? 'var(--accent)' : 'transparent',
                                color: cert.mode === m ? '#fff' : 'var(--ink-muted)',
                                transition: 'all 0.15s ease'
                              }}>{m === 'type' ? 'Type' : 'Upload'}</button>
                            ))}
                          </span>
                          <button type="button" onClick={() => removeCertificate(idx)} style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '0.82rem' }}>Remove</button>
                        </div>
                      </div>

                      {/* Type Mode */}
                      {cert.mode === 'type' && (
                        <input type="text" className="input-control"
                          placeholder="e.g. AWS Cloud Practitioner — Coursera"
                          value={cert.title}
                          onChange={(e) => updateCertificate(idx, 'title', e.target.value)}
                          required
                        />
                      )}

                      {/* Upload Mode */}
                      {cert.mode === 'upload' && (
                        <div>
                          {cert.uploading ? (
                            <div style={{ padding: '16px', textAlign: 'center', color: 'var(--accent)', fontWeight: 600, fontSize: '0.85rem', border: '1.5px dashed var(--accent)', borderRadius: 'var(--radius-sm)' }}>
                              Reading certificate...
                            </div>
                          ) : cert.uploaded ? (
                            /* ── Quiet confirmation (no popup) ── */
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', background: 'rgba(5, 150, 105, 0.05)', border: '1px solid var(--success)', borderRadius: 'var(--radius-sm)' }}>
                              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                              <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, color: 'var(--ink)', fontSize: '0.88rem' }}>{cert.title}</div>
                                {cert.issuer && <div style={{ fontSize: '0.75rem', color: 'var(--success)' }}>Issuer: {cert.issuer}</div>}
                                {!cert.issuer && <div style={{ fontSize: '0.75rem', color: 'var(--warning)' }}>Issuer not recognised — may count as partial credit.</div>}
                                <div style={{ fontSize: '0.72rem', color: 'var(--ink-muted)', marginTop: '2px' }}>{cert.filename} uploaded.</div>
                              </div>
                              <button type="button" onClick={() => { updateCertificate(idx, 'title', ''); updateCertificate(idx, 'issuer', ''); updateCertificate(idx, 'uploaded', false); updateCertificate(idx, 'filename', ''); }}
                                style={{ color: 'var(--ink-muted)', background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.78rem', flexShrink: 0 }}>Clear</button>
                            </div>
                          ) : (
                            <label htmlFor={`cert-upload-${idx}`} style={{
                              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px',
                              padding: '20px 14px', border: '1.5px dashed #c8cdd4',
                              borderRadius: 'var(--radius-sm)', cursor: 'pointer', textAlign: 'center',
                              transition: 'border-color 0.15s ease'
                            }}
                              onDragOver={(e) => { e.preventDefault(); e.currentTarget.style.borderColor = 'var(--accent)'; }}
                              onDragLeave={(e) => { e.currentTarget.style.borderColor = '#c8cdd4'; }}
                              onDrop={(e) => {
                                e.preventDefault(); e.currentTarget.style.borderColor = '#c8cdd4';
                                if (e.dataTransfer.files && e.dataTransfer.files[0]) uploadCertificate(idx, e.dataTransfer.files[0]);
                              }}
                            >
                              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--ink)' }}>Drop certificate PDF here</span>
                              <span style={{ fontSize: '0.75rem', color: 'var(--ink-muted)' }}>or click to browse</span>
                              <input id={`cert-upload-${idx}`} type="file" accept=".pdf" style={{ display: 'none' }}
                                onChange={(e) => { if (e.target.files && e.target.files[0]) uploadCertificate(idx, e.target.files[0]); }}
                              />
                            </label>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                  {formData.certificates.length === 0 && (
                    <div style={{ color: 'var(--ink-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '6px 0' }}>No certificates added. Click "+ Add" above.</div>
                  )}
                </div>
              )}
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '12px', padding: '12px', width: '100%' }} disabled={loading}>
              {loading ? 'Analyzing...' : 'Generate Analysis'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

