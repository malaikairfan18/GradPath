
import { useEffect, useState } from 'react'
import './App.css'
const API_BASE_URL = 'http://127.0.0.1:8000'

async function authRequest(path, payload) {
  const csrfResponse = await fetch(API_BASE_URL + '/api/auth/csrf', {
    credentials: 'include',
  })

  if (!csrfResponse.ok) {
    throw new Error('Unable to prepare a secure request. Please check that the GradPath API is running.')
  }

  const csrfData = await csrfResponse.json()

  const response = await fetch(API_BASE_URL + path, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfData.csrf_token,
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const message = typeof data.detail === 'string'
      ? data.detail
      : 'Authentication failed. Please try again.'

    throw new Error(message)
  }

  return data
}

const features = [
  {
    number: '01',
    icon: '⌘',
    title: 'Understand your profile',
    description:
      'Extract skills from your CV and see what your current profile tells you about your next career move.',
    tag: 'CV & PROFILE',
  },
  {
    number: '02',
    icon: '◈',
    title: 'Find your skill gaps',
    description:
      'Compare your profile with role-specific skills and understand where to focus your effort.',
    tag: 'SKILL DEVELOPMENT',
  },
  {
    number: '03',
    icon: '↗',
    title: 'Build a learning roadmap',
    description:
      'Turn skill gaps into practical learning actions instead of guessing what to learn next.',
    tag: 'LEARNING ROADMAP',
  },
  {
    number: '04',
    icon: '▦',
    title: 'Create proof of your skills',
    description:
      'Explore relevant projects, track your progress and submit evidence of what you have built.',
    tag: 'PROJECT WORKSPACE',
  },
]

const skills = [
  { name: 'Python', width: '88%', tone: 'violet' },
  { name: 'SQL', width: '72%', tone: 'teal' },
  { name: 'Data visualization', width: '54%', tone: 'lavender' },
]

function Brand({ light = false }) {
  return (
    <a className={`brand ${light ? 'brand-light' : ''}`} href="#home">
      <span className="brand-mark" aria-hidden="true">
        g<span>.</span>
      </span>
      <span>gradpath</span>
    </a>
  )
}

function DashboardPreview() {
  return (
    <div className="preview-shell" aria-label="Illustrative GradPath dashboard preview">
      <div className="preview-window">
        <aside className="preview-sidebar">
          <Brand />
          <span className="preview-menu-label">WORKSPACE</span>
          <span className="preview-menu-item active">▦ &nbsp; Overview</span>
          <span className="preview-menu-item">◎ &nbsp; My career</span>
          <span className="preview-menu-item">◇ &nbsp; Learning</span>
          <span className="preview-menu-item">↗ &nbsp; Projects</span>
          <div className="preview-sidebar-bottom">
            <span className="avatar">M</span>
            <span>
              <strong>Your workspace</strong>
              <small>Career development</small>
            </span>
          </div>
        </aside>

        <div className="preview-main">
          <div className="preview-topbar">
            <span>Monday, your next step starts here</span>
            <span className="preview-status"><i /> Prototype preview</span>
          </div>

          <div className="preview-heading">
            <div>
              <span className="eyebrow">YOUR CAREER OVERVIEW</span>
              <h3>A clearer path forward.</h3>
              <p>Understand where you are. Decide what comes next.</p>
            </div>
            <span className="role-chip">Data Analyst ↗</span>
          </div>

          <div className="preview-metrics">
            <div className="metric-card readiness-card">
              <span className="metric-label">VERIFIED SKILL COVERAGE</span>
              <div className="metric-number">—<span> / 100%</span></div>
              <div className="metric-footnote">
                <span className="metric-dot" /> Calculated from verified evidence
              </div>
              <div className="coverage-track"><span /></div>
              <small>Connect your profile to calculate coverage</small>
            </div>
            <div className="metric-card">
              <span className="metric-label">LEARNING PROGRESS</span>
              <div className="metric-number">Start <span>your journey</span></div>
              <div className="mini-bars" aria-hidden="true">
                <i /><i /><i /><i /><i /><i /><i /><i /><i /><i />
              </div>
              <small>Your activities will appear here</small>
            </div>
          </div>

          <div className="preview-lower">
            <div className="preview-panel">
              <div className="panel-title">
                <strong>Skill development</strong>
                <span>Illustrative only</span>
              </div>
              {skills.map((skill) => (
                <div className="skill-line" key={skill.name}>
                  <div className="skill-line-label">
                    <span>{skill.name}</span><span>Explore</span>
                  </div>
                  <div className={`skill-track ${skill.tone}`}>
                    <i style={{ width: skill.width }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="next-step-card">
              <span className="next-step-icon">✳</span>
              <span className="eyebrow">YOUR NEXT STEP</span>
              <strong>Build with purpose.</strong>
              <p>Discover projects aligned with the skills you want to develop.</p>
              <span className="next-step-link">Explore project ideas <span>→</span></span>
            </div>
          </div>
          <div className="preview-disclaimer">
            Illustrative preview · No real candidate data or scores shown
          </div>
        </div>
      </div>
      <div className="floating-note note-top">
        <span className="note-icon violet-icon">✳</span>
        <span><strong>Evidence first</strong><small>Progress with purpose</small></span>
      </div>
      <div className="floating-note note-bottom">
        <span className="note-icon teal-icon">↗</span>
        <span><strong>One step at a time</strong><small>Your journey, your pace</small></span>
      </div>
    </div>
  )
}

function AuthScreen({ mode, onNavigate, onContinue }) {
  const isLogin = mode === 'login'
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [authError, setAuthError] = useState('')

  async function handleAuthSubmit(event) {
    event.preventDefault()
    setIsSubmitting(true)
    setAuthError('')

    const formData = new FormData(event.currentTarget)
    const password = formData.get('password')

    const payload = isLogin
      ? {
          username_or_email: formData.get('username_or_email'),
          password,
        }
      : {
          username: formData.get('username'),
          email: formData.get('email'),
          password,
        }

    try {
      const result = await authRequest(
        isLogin ? '/api/auth/login' : '/api/auth/register',
        payload,
      )
      onContinue?.(result.user)
    } catch (error) {
      setAuthError(error.message || 'Something went wrong. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-topbar">
        <a
          className="brand"
          href="#home"
          onClick={(event) => {
            event.preventDefault()
            onNavigate('landing')
          }}
        >
          <span className="brand-mark" aria-hidden="true">
            g<span>.</span>
          </span>
          <span>gradpath</span>
        </a>
        <span className="auth-top-note">Your next step starts here.</span>
      </div>

      <section className="auth-card">
        <button
          className="auth-back"
          type="button"
          onClick={() => onNavigate('landing')}
        >
          ← Back to home
        </button>

        <div className="auth-symbol" aria-hidden="true">g.</div>
        <span className="eyebrow">
          {isLogin ? 'WELCOME BACK' : 'YOUR JOURNEY BEGINS'}
        </span>

        <h1>{isLogin ? 'Good to see you again.' : 'Make room for growth.'}</h1>
        <p className="auth-description">
          {isLogin
            ? 'Continue building a clearer path toward your career goals.'
            : 'Create your GradPath profile and start planning your next steps.'}
        </p>

        {authError && <div className="auth-prototype-notice" role="alert">{authError}</div>}

        <form onSubmit={handleAuthSubmit}>
          {!isLogin && (
            <label className="auth-field">
              Username
              <input
                type="text"
                name="username"
                placeholder="Choose a username"
                autoComplete="username"
                required
              />
            </label>
          )}

          <label className="auth-field">
            {isLogin ? 'Username or email' : 'Email address'}
            <input
              type={isLogin ? 'text' : 'email'}
              name={isLogin ? 'username_or_email' : 'email'}
              placeholder={isLogin ? 'Username or email' : 'you@example.com'}
              autoComplete={isLogin ? 'username' : 'email'}
              required
            />
          </label>

          <label className="auth-field">
            Password
            <input
              type="password"
              name="password"
              placeholder="Enter a password"
              autoComplete={isLogin ? 'current-password' : 'new-password'}
              minLength={isLogin ? undefined : 12}
              required
            />
          </label>

          <button className="button button-dark auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Please wait...' : isLogin ? 'Continue to GradPath' : 'Create your account'} <span>→</span>
          </button>
        </form>

        <p className="auth-switch">
          {isLogin ? "New to GradPath?" : 'Already have an account?'}{' '}
          <button
            type="button"
            onClick={() => onNavigate(isLogin ? 'register' : 'login')}
          >
            {isLogin ? 'Create an account' : 'Log in'}
          </button>
        </p>

        <p className="auth-privacy-note">
          Your account details are submitted securely to the GradPath API.
        </p>
      </section>

      <footer className="auth-footer">
        GradPath · Built for thoughtful progress.
      </footer>
    </main>
  )
}

function MyCareer({
  targetRole,
  onTargetRoleChange,
  onProfileChange,
  onCareerPlanChange,
}) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [careerPlan, setCareerPlan] = useState(null)
  const [planning, setPlanning] = useState(false)
  const [planError, setPlanError] = useState('')

  async function handleUpload(event) {
    event.preventDefault()

    if (!selectedFile) {
      setError('Please select a PDF or DOCX file first.')
      return
    }

    setLoading(true)
    setError('')
    setProfile(null)
    setCareerPlan(null)
    setPlanError('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(
        'http://127.0.0.1:8000/api/cv/analyze',
        {
          method: 'POST',
          credentials: 'include',
          body: formData,
        },
      )

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          result.detail || 'We could not analyze this CV.',
        )
      }

      if (!result.profile) {
        throw new Error('The API returned no candidate profile.')
      }

      setProfile(result.profile)
      onProfileChange(result.profile)
      onCareerPlanChange(null)
    } catch (err) {
      setError(
        err.message ||
          'Could not connect to GradPath. Check that the API is running.',
      )
    } finally {
      setLoading(false)
    }
  }

    async function handleGeneratePlan() {
    if (!profile) {
      setPlanError('Analyze your CV before generating a career plan.')
      return
    }

    setPlanning(true)
    setPlanError('')
    setCareerPlan(null)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/career/plan',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            candidate_profile: profile,
            target_role: targetRole,
          }),
        },
      )

      const result = await response.json()

      if (!response.ok) {
        throw new Error(
          result.detail || 'Could not generate your career plan.',
        )
      }

      setCareerPlan(result)
      onCareerPlanChange(result)
    } catch (err) {
      setPlanError(
        err.message ||
          'Could not connect to GradPath. Check that the API is running.',
      )
    } finally {
      setPlanning(false)
    }
  }

  const skills = profile?.skills || []

  const profileSections = [
    { title: 'Education', items: profile?.education || [] },
    { title: 'Experience', items: profile?.experience || [] },
    { title: 'Projects', items: profile?.projects || [] },
    {
      title: 'Certifications',
      items: profile?.certifications || [],
    },
  ]

  return (
    <section className="career-page">
      <div className="career-intro">
        <span className="eyebrow">YOUR PROFESSIONAL PROFILE</span>
        <h1>Start with your experience.</h1>
        <p>
          Upload your CV to build your starting profile.
          Review what GradPath extracts before deciding your next step.
        </p>
      </div>

      <section className="career-upload-card">
        <div className="career-card-heading">
          <span className="career-upload-icon" aria-hidden="true">
            CV
          </span>
          <div>
            <h2>Upload your CV</h2>
            <p>PDF or DOCX · Maximum size 5 MB</p>
          </div>
        </div>

                <label className="career-role-select">
          <span>Target career role</span>
          <select
            value={targetRole}
            onChange={(event) => {
            onTargetRoleChange(event.target.value)
            setCareerPlan(null)
            onCareerPlanChange(null)
            setPlanError('')
          }}
          >
            <option value="Data Analyst">Data Analyst</option>
            <option value="Data Scientist">Data Scientist</option>
          </select>
        </label>

        <form onSubmit={handleUpload}>
           <p className="career-upload-guidance">
            Upload your latest CV to build your career profile. GradPath will
            extract relevant information and identify skills mentioned in your CV.
            Detected skills are not automatically verified.
          </p>
          <label className="career-file-label">
            <span>Choose a CV file</span>
            <input
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(event) => {
                setSelectedFile(event.target.files?.[0] || null)
                setError('')
              }}
            />
          </label>

          {selectedFile && (
            <p className="career-selected-file">
              Selected: {selectedFile.name}
            </p>
          )}

          <button
            className="workspace-primary-button career-upload-button"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Analyzing your CV...' : 'Analyze my CV'}
          </button>
        </form>

        <p className="career-privacy-note">
          Your file is processed temporarily by the local API.
          This prototype does not save your CV as a candidate record.
        </p>

        {error && (
          <div className="career-message career-error" role="alert">
            {error}
          </div>
        )}
      </section>

      {loading && (
        <div className="career-message" role="status">
          Extracting your profile and identifying skill mentions...
        </div>
      )}

      {profile && (
        <div className="career-results">
          <section className="career-results-header">
            <div>
              <span className="eyebrow">CV ANALYSIS RESULTS</span>
              <h2>Your starting profile</h2>
              <p>
                Extraction status:{' '}
                <strong>
                  {profile.source_document?.extraction_status || 'Unknown'}
                </strong>
              </p>
            </div>
            <span className="career-status-badge">
              Profile extracted
            </span>
          </section>

          <div className="career-summary-grid">
            <article className="career-summary-card">
              <span>Skills Detected</span>
              <strong>{(profile.skills || []).length}</strong>
              <small>CV mentions · unverified by default</small>
            </article>

            <article className="career-summary-card">
              <span>Sections Populated</span>
              <strong>
                {profileSections.filter((section) => section.items.length > 0).length}
              </strong>
              <small>Of 4 profile sections</small>
            </article>

            <article className="career-summary-card">
              <span>Skills with Evidence</span>
              <strong>
                {(profile.skills || []).filter((skill) =>
                  (skill.evidence || []).some(
                    (evidence) => Boolean(evidence.text?.trim()),
                  ),
                ).length}
              </strong>
              <small>Supporting CV text available</small>
            </article>

            <article className="career-summary-card">
              <span>Review Status</span>
              <strong>Review</strong>
              <small>Check extracted details and skill evidence</small>
            </article>
          </div>

          <section className="career-results-card">
            <div className="career-section-heading">
              <div>
                <span className="eyebrow">SKILLS FOUND IN YOUR CV</span>
                <h2>Skills identified</h2>
              </div>
              <span className="career-unverified-badge">Unverified</span>
            </div>

            <p className="career-explanation">
              GradPath found these skills through text matching. A mention in
              your CV does not prove proficiency. Skills remain unverified until
              they meet GradPath's verification criteria using supported
              evidence, such as assessments or project evidence.
            </p>

            {skills.length > 0 ? (
              <div className="career-skills-list">
                {skills.map((skill, index) => (
                  <details
                    className="career-skill-item"
                    key={`${skill.skill_id || skill.skill_name || 'skill'}-${index}`}
                  >
                    <summary className="career-skill-summary">
                      <span className="career-skill-name">
                        {skill.skill_name || 'Unnamed skill'}
                        <small>{skill.skill_category || 'Category not specified'}</small>
                      </span>
                      <span className="career-skill-status">Unverified</span>
                    </summary>

                    <div className="career-skill-detail">
                      <p>
                        <strong>Why unverified?</strong> This skill was identified
                        in CV text, but GradPath has not confirmed your proficiency
                        against its verification criteria.
                      </p>

                      {Array.isArray(skill.evidence) && skill.evidence.length > 0 ? (
                        <div className="career-skill-evidence">
                          <strong>Evidence found in your CV</strong>
                          <ul className="career-evidence-list">
                            {skill.evidence.slice(0, 3).map((item, evidenceIndex) => (
                              <li key={evidenceIndex}>
                                <span className="career-evidence-section">
                                  {(item.section || 'CV').replace(/_/g, ' ')}
                                </span>
                                <p>{item.text || 'Evidence text unavailable.'}</p>
                              </li>
                            ))}
                          </ul>
                          {skill.evidence.length > 3 && (
                            <p className="career-evidence-more">
                              {skill.evidence.length - 3} additional evidence matches
                              are available.
                            </p>
                          )}
                        </div>
                      ) : (
                        <p>No supporting CV excerpt is available for this skill.</p>
                      )}
                    </div>
                  </details>
                ))}
              </div>
            ) : (
              <p>No skill mentions were extracted from this CV.</p>
            )}
          </section>

                    <section className="career-results-card career-plan-card">
            <div className="career-section-heading">
              <div>
                <span className="eyebrow">YOUR NEXT STEPS</span>
                <h2>Career plan</h2>
              </div>
              <span className="career-status-badge">{targetRole}</span>
            </div>

            <p className="career-explanation">
              Compare your CV evidence with role-specific skills and observed
              job-market data. Missing CV mentions are potential gaps, not
              proof that you lack a skill.
            </p>

            <button
              type="button"
              className="workspace-primary-button"
              onClick={handleGeneratePlan}
              disabled={planning}
            >
              {planning
                ? 'Generating your career plan...'
                : careerPlan
                  ? 'Refresh career plan'
                  : 'Analyze skill gaps and learning'}
            </button>

            {planError && (
              <div className="career-message career-error" role="alert">
                {planError}
              </div>
            )}

            {planning && (
              <div className="career-message" role="status">
                Analyzing skill evidence and matching learning resources...
              </div>
            )}

            {careerPlan && (
              <div className="career-plan-results">
                <div className="career-plan-counts">
                  <article className="career-summary-card">
                    <span>Skills assessed</span>
                    <strong>{careerPlan.skill_gaps.length}</strong>
                  </article>
                  <article className="career-summary-card">
                    <span>Learning actions</span>
                    <strong>{careerPlan.learning_actions.length}</strong>
                  </article>
                </div>

                <h3>Skill-gap analysis</h3>

                  {careerPlan.skill_gaps.length > 0 ? (
                    <>
                      <div className="career-plan-list">
                        {careerPlan.skill_gaps.slice(0, 6).map((gap) => (
                          <article
                            className="career-plan-item"
                            key={gap.skill_id}
                          >
                            <div className="career-plan-item-heading">
                              <strong>{gap.skill_name}</strong>
                              <span>
                                {(gap.candidate_status || '').replace(/_/g, ' ')}
                              </span>
                            </div>

                            <p>{gap.explanation}</p>

                            <small>
                              Market evidence: {gap.market_evidence_status || 'Not available'}
                              {' · '}
                              Priority score: {gap.priority_score ?? 'Not available'}
                            </small>
                          </article>
                        ))}
                      </div>

                      {careerPlan.skill_gaps.length > 6 && (
                        <details className="all-skill-gaps">
                          <summary>
                            View all {careerPlan.skill_gaps.length} skill-gap records
                          </summary>

                          <div className="career-plan-list">
                            {careerPlan.skill_gaps.slice(6).map((gap) => (
                              <article
                                className="career-plan-item"
                                key={gap.skill_id}
                              >
                                <div className="career-plan-item-heading">
                                  <strong>{gap.skill_name}</strong>
                                  <span>
                                    {(gap.candidate_status || '').replace(/_/g, ' ')}
                                  </span>
                                </div>

                                <p>{gap.explanation}</p>

                                <small>
                                  Market evidence: {gap.market_evidence_status || 'Not available'}
                                  {' · '}
                                  Priority score: {gap.priority_score ?? 'Not available'}
                                </small>
                              </article>
                            ))}
                          </div>
                        </details>
                      )}
                    </>
                  ) : (
                    <p>No skill-gap records were returned for this role.</p>
                  )}

                <h3>Recommended learning actions</h3>

                {careerPlan.learning_actions.length > 0 ? (

              <div className="career-plan-list">
                {careerPlan.learning_actions.map((action) => (
                  <article
                    className="career-plan-item learning-action-card"
                    key={`${action.skill_id}-${action.recommended_action}`}
                  >
                    <div className="career-plan-item-heading">
                      <strong>{action.skill_name}</strong>
                      <span>
                        {(action.recommended_action || 'review').replace(/_/g, ' ')}
                      </span>
                    </div>

                    {action.resource_title && (
                      <h4 className="learning-resource-title">
                        {action.resource_title}
                      </h4>
                    )}

                    {action.resource_description && (
                      <p className="learning-resource-description">
                        {action.resource_description}
                      </p>
                    )}

                    <div className="learning-resource-meta">
                      <span>{action.difficulty || 'Difficulty not specified'}</span>
                      <span>{action.access_type || 'Access details not specified'}</span>
                    </div>

                    {action.resource_url && (
                      <a
                        className="learning-resource-link"
                        href={action.resource_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Open learning resource
                        <span aria-hidden="true"> ↗</span>
                      </a>
                    )}

                    <details className="learning-evidence-details">
                      <summary>Why this recommendation?</summary>
                      <p>{action.explanation}</p>

                      <div className="learning-evidence-stats">
                        <span>
                          Market evidence: {action.market_evidence_status || 'Not available'}
                        </span>
                        <span>
                          Observed jobs: {action.market_jobs_with_skill ?? 'Not available'}
                          {' / '}
                          {action.market_relevant_jobs_total ?? 'Not available'}
                        </span>
                        <span>
                          Priority score: {action.priority_score ?? 'Not available'}
                        </span>
                      </div>

                      {action.esco_mapping_status && (
                        <p>
                          <strong>ESCO mapping:</strong> {action.esco_mapping_status}
                          {action.esco_relationship
                            ? ` · ${action.esco_relationship}`
                            : ''}
                          {action.esco_label ? ` · ${action.esco_label}` : ''}
                        </p>
                      )}
                    </details>
                  </article>
                ))}
              </div>

                ) : (
                  <p>
                    No learning actions were returned. This can happen when
                    suitable resources are unavailable for the current results.
                  </p>
                )}
              </div>
            )}
          </section>

          <section className="career-results-card career-skills-card">
            <div className="career-section-heading">
              <div>
                <h2>Detected Skills</h2>
                <p className="career-skills-intro">
                  Skills identified in your CV. These mentions are not proof of
                  proficiency.
                </p>
              </div>
              <span>{(profile?.skills || []).length} detected</span>
            </div>

            {(profile?.skills || []).length > 0 ? (
              <div className="career-skills-list">
                {(profile?.skills || []).map((skill, index) => (
                  <article
                    className="career-skill-item"
                    key={`${skill.skill_id || skill.skill_name}-${index}`}
                  >
                    <div className="career-skill-top">
                      <div>
                        <h3>{skill.skill_name || 'Unnamed skill'}</h3>
                        <span className="career-skill-category">
                          {skill.skill_category || 'Category unavailable'}
                        </span>
                      </div>
                      <span className="career-skill-status">
                        {skill.verification_status === 'verified'
                          ? 'Verified'
                          : 'Unverified'}
                      </span>
                    </div>

                    {skill.evidence?.length > 0 ? (
                      <div className="career-skill-evidence">
                        <strong>CV evidence</strong>
                        {skill.evidence.map((evidence, evidenceIndex) => (
                          <div
                            className="career-skill-evidence-item"
                            key={`${evidence.section || 'section'}-${evidenceIndex}`}
                          >
                            <span>
                              {evidence.section || 'CV section'}
                              {evidence.evidence_type
                                ? ` · ${evidence.evidence_type}`
                                : ''}
                            </span>
                            {evidence.text && <p>{evidence.text}</p>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="career-skill-no-evidence">
                        No supporting text is available for this skill.
                      </p>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="career-skills-empty">
                No skills have been detected yet. Upload your CV to view extracted
                skills and their available evidence.
              </p>
            )}
          </section>

          {profileSections.map((section) => (
            <section
              className="career-results-card"
              key={section.title}
            >
              <div className="career-section-heading">
                <h2>{section.title}</h2>
                <span>{section.items.length} entries</span>
              </div>

              {section.items.length > 0 ? (
                <div className="career-entry-list">
                  {section.items.map((item, index) => (
                    <article
                      className="career-entry"
                      key={`${section.title}-${index}`}
                    >

                      {Object.entries(item).map(([key, value]) => {
                        if (
                          value === null ||
                          value === undefined ||
                          value === ''
                        ) {
                          return null
                        }

                        const label = key
                          .replace(/_/g, ' ')
                          .replace(/\b\w/g, (letter) => letter.toUpperCase())

                        const displayValue = Array.isArray(value)
                          ? value
                              .map((entry) =>
                                typeof entry === 'object' && entry !== null
                                  ? Object.values(entry)
                                      .filter(
                                        (part) =>
                                          part !== null &&
                                          part !== undefined &&
                                          typeof part !== 'object',
                                      )
                                      .join(' — ')
                                  : String(entry),
                              )
                              .filter(Boolean)
                              .join(', ')
                          : typeof value === 'object'
                            ? Object.entries(value)
                                .filter(
                                  ([, part]) =>
                                    part !== null &&
                                    part !== undefined &&
                                    typeof part !== 'object',
                                )
                                .map(
                                  ([nestedKey, part]) =>
                                    `${nestedKey.replace(/_/g, ' ')}: ${part}`,
                                )
                                .join(' · ')
                            : String(value)

                        if (!displayValue.trim()) return null

                        return (
                          <div
                            className="career-entry-field"
                            key={key}
                          >
                            <span className="career-entry-label">
                              {label}
                            </span>
                            <span className="career-entry-value">
                              {displayValue}
                            </span>
                          </div>
                        )
                      })}

                    </article>
                  ))}
                </div>
              ) : (
                <p className="career-empty-note">
                  No entries extracted for this section.
                </p>
              )}
            </section>
          ))}

          {profile.extraction_warnings?.length > 0 && (
            <section className="career-message career-warning">
              <strong>Extraction notes</strong>
              <ul>
                {profile.extraction_warnings.map((warning, index) => (
                  <li key={index}>
                    {typeof warning === 'string'
                      ? warning
                      : JSON.stringify(warning)}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </section>
  )
}

function Workspace({ onNavigate, onLogout, currentUser }) {
  const [activePage, setActivePage] = useState('Overview')
  const [targetRole, setTargetRole] = useState('Data Analyst')
  const [candidateProfile, setCandidateProfile] = useState(null)
  const [sharedCareerPlan, setSharedCareerPlan] = useState(null)

  const projectIdeas =
  targetRole === 'Data Scientist'
    ? [
        {
          title: 'Customer Churn Prediction',
          description:
            'Build and evaluate a machine learning model to identify customers likely to leave.',
          skills: ['Python', 'Pandas', 'scikit-learn'],
        },
        {
          title: 'Exploratory Data Analysis',
          description:
            'Explore a real-world dataset, identify patterns, and communicate findings through visualizations.',
          skills: ['Python', 'Pandas', 'Matplotlib'],
        },
        {
          title: 'Model Evaluation Dashboard',
          description:
            'Compare model performance using evaluation metrics and present the results clearly.',
          skills: ['Python', 'scikit-learn', 'Power BI'],
        },
      ]
    : [
        {
          title: 'Sales Performance Dashboard',
          description:
            'Analyze sales trends and build an interactive dashboard to communicate business insights.',
          skills: ['SQL', 'Power BI', 'Data Analysis'],
        },
        {
          title: 'Customer Insights Analysis',
          description:
            'Explore customer behavior and summarize useful business insights from a dataset.',
          skills: ['Python', 'Pandas', 'SQL'],
        },
        {
          title: 'Business KPI Reporting',
          description:
            'Create a repeatable reporting workflow for tracking key performance indicators.',
          skills: ['SQL', 'Power BI', 'Excel'],
        },
      ]

  const navigation = [
    { group: 'WORKSPACE', items: [
      { name: 'Overview', icon: '←' },
      { name: 'My Career', icon: '◎' },
      { name: 'Learning Roadmap', icon: '↗' },
      { name: 'Project Workspace', icon: '◇' },
    ] },
    { group: 'YOUR PROGRESS', items: [
      { name: 'Readiness Report', icon: '◇' },
    ] },
  ]

  const pageDescriptions = {
    'My Career': {
      eyebrow: 'YOUR PROFESSIONAL PROFILE',
      title: 'Start with your experience.',
      description: 'Upload your CV to extract your profile and review the skills identified in it.',
      action: 'Continue to CV profile',
    },
    'Learning Roadmap': {
      eyebrow: 'YOUR LEARNING PLAN',
      title: 'Make learning intentional.',
      description: 'Explore role-specific skill gaps and learning recommendations based on your profile.',
      action: 'Explore learning',
    },
    'Project Workspace': {
      eyebrow: 'PRACTICE AND BUILD',
      title: 'Turn knowledge into evidence.',
      description: 'Discover relevant projects, track your progress and record the work you complete.',
      action: 'Explore projects',
    },
    'Readiness Report': {
      eyebrow: 'YOUR EVIDENCE-BASED PROGRESS',
      title: 'Understand what your progress means.',
      description: 'Readiness reporting will use available profile, assessment and project evidence. No score is available until your data is connected.',
      action: 'Review your profile',
    },
  }

  const isOverview = activePage === 'Overview'
  const pageInfo = pageDescriptions[activePage]

  function navigateTo(page) {
    setActivePage(page)
  }

  return (
    <div className="workspace-shell">
      <aside className="workspace-sidebar">
        <button
          type="button"
          className="workspace-brand"
          onClick={() => navigateTo('Overview')}
          aria-label="GradPath overview"
        >
          <span className="brand-mark">g<span>.</span></span>
          <span>gradpath</span>
        </button>

        <div className="workspace-profile">
          <span className="workspace-avatar">G</span>
          <div>
            <strong>{currentUser?.username || currentUser?.email || 'My workspace'}</strong>
            <small>Career development</small>
          </div>
        </div>

        <nav className="workspace-nav" aria-label="Workspace navigation">
          {navigation.map((section) => (
            <div className="workspace-nav-group" key={section.group}>
              <span className="workspace-nav-label">{section.group}</span>
              {section.items.map((item) => (
                <button
                  type="button"
                  key={item.name}
                  className={`workspace-nav-item ${activePage === item.name ? 'active' : ''}`}
                  onClick={() => navigateTo(item.name)}
                  aria-current={activePage === item.name ? 'page' : undefined}
                >
                  <span className="workspace-nav-icon" aria-hidden="true">{item.icon}</span>
                  <span>{item.name}</span>
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="workspace-sidebar-bottom">
          <div className="workspace-help">
            <span className="workspace-help-icon">✳</span>
            <strong>Small steps count.</strong>
            <p>Build your career plan one meaningful action at a time.</p>
          </div>
          <button className="workspace-logout" type="button" onClick={onLogout}>
            <span aria-hidden="true">↗</span> Return to landing page
          </button>
        </div>
      </aside>

      <main className="workspace-main">
        <header className="workspace-topbar">
          <div className="workspace-breadcrumb">
            <span>Workspace</span><span>/</span><strong>{activePage}</strong>
          </div>
          <div className="workspace-topbar-right">
            <span className="workspace-prototype-pill"><i /> Prototype mode</span>
            <span className="workspace-top-avatar">G</span>
          </div>
        </header>

        <div className="workspace-content">

          {isOverview ? (
            <>
              {(() => {
                const skills = candidateProfile?.skills ?? []
                const learningActions = sharedCareerPlan?.learning_actions ?? []
                const skillGaps = sharedCareerPlan?.skill_gaps ?? []
                const hasProfile = Boolean(candidateProfile)

                return (
                  <>
                    <section className="workspace-welcome">
                      <div>
                        <span className="eyebrow">YOUR CAREER, WITH MORE CLARITY</span>
                        <h1>Your next chapter starts here.</h1>
                        <p>
                          {hasProfile
                            ? 'Your profile is taking shape. Keep building evidence for your target role.'
                            : 'A little progress today can give you a clearer direction tomorrow.'}
                        </p>
                      </div>
                      <div className="welcome-decoration" aria-hidden="true">
                        <span className="welcome-orbit orbit-a" />
                        <span className="welcome-orbit orbit-b" />
                        <span className="welcome-star">✳</span>
                      </div>
                    </section>

                    <section className="workspace-role-card">
                      <div className="workspace-role-copy">
                        <span className="eyebrow">YOUR TARGET ROLE</span>
                        <h2>What are you working towards?</h2>
                        <p>Choose a role to shape your future profile and learning plan.</p>
                      </div>
                      <label className="workspace-role-select">
                        <span>Career goal</span>
                        <select
                          value={targetRole}
                          onChange={(event) => {
                          setTargetRole(event.target.value)
                          setSharedCareerPlan(null)
                        }}
                        >
                          <option>Data Analyst</option>
                          <option>Data Scientist</option>
                        </select>
                      </label>
                    </section>

                    <div className="workspace-section-heading">
                      <div>
                        <span className="eyebrow">YOUR STARTING POINT</span>
                        <h2>Build your foundation.</h2>
                      </div>
                      <span className="workspace-status-label">
                        {hasProfile ? 'Profile analyzed' : 'Profile not started'}
                      </span>
                    </div>

                    <section className="workspace-stat-grid">
                      <article className="workspace-stat-card">
                        <span className="workspace-stat-icon lavender">◎</span>
                        <span className="workspace-stat-label">CV PROFILE</span>
                        <strong>{hasProfile ? 'Analyzed' : 'Not started'}</strong>
                        <p>
                          {hasProfile
                            ? `${skills.length} skill${skills.length === 1 ? '' : 's'} detected in your profile.`
                            : 'Review your experience and extracted skills.'}
                        </p>
                        <button type="button" onClick={() => navigateTo('My Career')}>
                          {hasProfile ? 'Review profile' : 'Set up profile'} <span>→</span>
                        </button>
                      </article>

                      <article className="workspace-stat-card">
                        <span className="workspace-stat-icon teal">↗</span>
                        <span className="workspace-stat-label">LEARNING ROADMAP</span>
                        <strong>
                          {sharedCareerPlan
                            ? `${learningActions.length} learning actions`
                            : 'Not generated'}
                        </strong>
                        <p>
                          {sharedCareerPlan
                            ? `${skillGaps.length} skill-gap records in your current plan.`
                            : 'Generate a career plan to see learning recommendations.'}
                        </p>
                        <button type="button" onClick={() => navigateTo('Learning Roadmap')}>
                          View roadmap <span>→</span>
                        </button>
                      </article>

                      <article className="workspace-stat-card">
                        <span className="workspace-stat-icon violet">◇</span>
                        <span className="workspace-stat-label">PROJECT WORKSPACE</span>
                        <strong>Not started</strong>
                        <p>Explore projects to practise and demonstrate your skills.</p>
                        <button type="button" onClick={() => navigateTo('Project Workspace')}>
                          Explore projects <span>→</span>
                        </button>
                      </article>
                    </section>

                    <section className="workspace-panel workspace-journey-panel">
                      <div className="workspace-panel-heading">
                        <div>
                          <span className="eyebrow">YOUR CAREER JOURNEY</span>
                          <h2>Small steps, meaningful progress.</h2>
                        </div>
                      </div>

                      <p className="workspace-journey-description">
                        Follow your progress from your CV profile to practical
                        evidence of your skills.
                      </p>

                      <div className="workspace-journey-steps">
                        <article className={`workspace-journey-step ${hasProfile ? 'is-complete' : 'is-current'}`}>
                          <span className="workspace-journey-number">
                            {hasProfile ? '✓' : '01'}
                          </span>
                          <div>
                            <strong>Build your profile</strong>
                            <p>
                              {hasProfile
                                ? 'Your CV profile is available.'
                                : 'Start by analyzing your CV.'}
                            </p>
                            {!hasProfile && (
                              <button type="button" onClick={() => navigateTo('My Career')}>
                                Analyze CV →
                              </button>
                            )}
                          </div>
                        </article>

                        <article className={`workspace-journey-step ${sharedCareerPlan ? 'is-complete' : hasProfile ? 'is-current' : ''}`}>
                          <span className="workspace-journey-number">
                            {sharedCareerPlan ? '✓' : '02'}
                          </span>
                          <div>
                            <strong>Create your learning plan</strong>
                            <p>
                              {sharedCareerPlan
                                ? 'Your career plan is available.'
                                : hasProfile
                                  ? 'Generate recommendations for your target role.'
                                  : 'Your plan can follow your CV analysis.'}
                            </p>
                            {!sharedCareerPlan && (
                              <button type="button" onClick={() => navigateTo('My Career')}>
                                {hasProfile ? 'Continue' : 'Get started'} →
                              </button>
                            )}
                          </div>
                        </article>

                        <article className="workspace-journey-step">
                          <span className="workspace-journey-number">03</span>
                          <div>
                            <strong>Build project evidence</strong>
                            <p>
                              Explore projects that help demonstrate your skills.
                            </p>
                            <button type="button" onClick={() => navigateTo('Project Workspace')}>
                              Explore projects →
                            </button>
                          </div>
                        </article>

                        <article className="workspace-journey-step">
                          <span className="workspace-journey-number">04</span>
                          <div>
                            <strong>Review your readiness</strong>
                            <p>
                              Review available evidence and identify what still needs work.
                            </p>
                            <button type="button" onClick={() => navigateTo('Readiness Report')}>
                              View report →
                            </button>
                          </div>
                        </article>
                      </div>
                    </section>

                    <section className="workspace-bottom-grid">
                      <article className="workspace-panel workspace-readiness-panel">
                        <div className="workspace-panel-heading">
                          <div>
                            <span className="eyebrow">READINESS OVERVIEW</span>
                            <h2>Evidence before scores.</h2>
                          </div>
                          <span className="workspace-panel-symbol">○</span>
                        </div>

                        <div className="workspace-readiness-content">
                          <p className="workspace-readiness-intro">
                            Readiness should reflect evidence, not just the
                            skills mentioned in a CV.
                          </p>

                          <div className="workspace-evidence-list">
                            <div className="workspace-evidence-item">
                              <span className="workspace-evidence-icon">01</span>
                              <div>
                                <strong>CV skill mentions</strong>
                                <p>
                                  {hasProfile
                                    ? `${skills.length} skills detected; mentions remain unverified.`
                                    : 'Analyze your CV to identify relevant skills.'}
                                </p>
                              </div>
                              <span className="workspace-evidence-state">
                                {hasProfile ? 'Available' : 'Pending'}
                              </span>
                            </div>

                            <div className="workspace-evidence-item">
                              <span className="workspace-evidence-icon">02</span>
                              <div>
                                <strong>Learning progress</strong>
                                <p>
                                  {sharedCareerPlan
                                    ? `${learningActions.length} learning actions in your current plan.`
                                    : 'Generate a learning plan to identify next steps.'}
                                </p>
                              </div>
                              <span className="workspace-evidence-state">
                                {sharedCareerPlan ? 'Available' : 'Pending'}
                              </span>
                            </div>

                            <div className="workspace-evidence-item">
                              <span className="workspace-evidence-icon">03</span>
                              <div>
                                <strong>Practical project evidence</strong>
                                <p>
                                  Record completed projects and supporting evidence
                                  before treating skills as demonstrated.
                                </p>
                              </div>
                              <span className="workspace-evidence-state">
                                To build
                              </span>
                            </div>
                          </div>

                          <button
                            type="button"
                            onClick={() => navigateTo('Readiness Report')}
                          >
                            Review readiness <span>→</span>
                          </button>
                        </div>

                      </article>

                      <article className="workspace-panel workspace-next-panel">
                        <span className="eyebrow">YOUR NEXT STEP</span>
                        <div className="workspace-next-icon">✳</div>

                        <h2>
                          {!hasProfile
                            ? 'Start with your CV.'
                            : !sharedCareerPlan
                              ? 'Turn your profile into a plan.'
                              : learningActions.length > 0
                                ? 'Take your next learning step.'
                                : 'Explore practical projects.'}
                        </h2>
                        <p>
                          {!hasProfile
                            ? 'Upload your CV to build a starting profile and identify the skills mentioned in it.'
                            : !sharedCareerPlan
                              ? 'Generate a learning plan for your selected role to explore skill gaps and relevant learning resources.'
                              : learningActions.length > 0
                                ? `Your current plan includes ${learningActions.length} learning actions. Choose one to begin building your skills.`
                                : 'Explore role-relevant projects and start collecting evidence of what you can do.'}
                        </p>

                        <button
                          type="button"
                          className="workspace-primary-button"
                          onClick={() =>
                            navigateTo(
                              !hasProfile || !sharedCareerPlan
                                ? 'My Career'
                                : learningActions.length > 0
                                  ? 'Learning Roadmap'
                                  : 'Project Workspace',
                            )
                          }
                        >
                          {!hasProfile
                              ? 'Analyze my CV'
                              : !sharedCareerPlan
                                ? 'Create my plan'
                                : learningActions.length > 0
                                  ? 'View learning plan'
                                  : 'Explore projects'} <span>→</span>
                        </button>
                      </article>
                    </section>

                    <p className="workspace-footnote">
                      Dashboard metrics reflect data available in this session. Persistent
                      profile history and verified readiness results are not yet connected here.
                    </p>
                  </>
                )
              })()}
            </>
          ) : activePage === 'My Career' ? (

            <MyCareer
                targetRole={targetRole}
                onTargetRoleChange={setTargetRole}
                onProfileChange={setCandidateProfile}
                onCareerPlanChange={setSharedCareerPlan}
              />

          ) : activePage === 'Learning Roadmap' ? (
            <section className="workspace-placeholder">
              <button
                type="button"
                className="workspace-back-link"
                onClick={() => navigateTo('Overview')}
              >
                ← Back to overview
              </button>

              <span className="eyebrow">YOUR LEARNING PLAN</span>
              <h1>Your {targetRole} learning roadmap.</h1>
              <p>
                Use your identified skill gaps to guide your next learning steps.
                Recommendations depend on the career plan generated from your CV.
              </p>

              {!sharedCareerPlan ? (
                <div className="workspace-coming-soon">
                  <span>✳</span>
                  <div>
                    <strong>Your learning plan is waiting.</strong>
                    <p>
                      Visit My Career, analyze your CV, and generate a career plan
                      to see your personalized learning recommendations here.
                    </p>
                    <button
                      type="button"
                      className="workspace-primary-button"
                      onClick={() => navigateTo('My Career')}
                    >
                      Go to My Career <span>→</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="roadmap-content">
                  <div className="workspace-section-heading">
                    <div>
                      <span className="eyebrow">RECOMMENDED NEXT STEPS</span>
                      <h2>Your learning actions</h2>
                    </div>
                    <span className="workspace-status-label">
                      {sharedCareerPlan.learning_actions?.length ?? 0} actions
                    </span>
                  </div>

                  {(sharedCareerPlan.learning_actions ?? []).length === 0 ? (
                    <div className="workspace-coming-soon">
                      <span>◇</span>
                      <div>
                        <strong>No learning actions are available yet.</strong>
                        <p>
                          Review your profile and regenerate your career plan
                          to check for available recommendations.
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="workspace-stat-grid">

                    {(sharedCareerPlan.learning_actions ?? []).map((action, index) => {
                      const title =
                        action.resource_title ??
                        action.title ??
                        action.recommended_action ??
                        action.skill_name ??
                        `Learning action ${index + 1}`

                      const description =
                        action.resource_description ??
                        action.description ??
                        action.explanation ??
                        ''

                      return (
                        <article
                          className="workspace-stat-card learning-action-card"
                          key={`${action.skill_id ?? title}-${index}`}
                        >
                          <span className="workspace-stat-icon teal">↗</span>
                          <span className="workspace-stat-label">
                            LEARNING STEP {index + 1}
                          </span>

                          <strong>{title}</strong>

                          {action.skill_name && (
                            <p>Skill focus: {action.skill_name}</p>
                          )}

                          {description && <p>{description}</p>}

                          <div className="learning-resource-meta">
                            {action.difficulty && <span>{action.difficulty}</span>}
                            {action.access_type && <span>{action.access_type}</span>}
                          </div>

                          {action.resource_url && (
                            <a
                              className="learning-resource-link"
                              href={action.resource_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Open learning resource ↗
                            </a>
                          )}

                          {action.explanation && (
                            <details className="learning-evidence-details">
                              <summary>Why this recommendation?</summary>
                              <p>{action.explanation}</p>
                              {action.market_evidence_status && (
                                <p>
                                  Market evidence: {action.market_evidence_status}
                                </p>
                              )}
                            </details>
                          )}
                        </article>
                      )
                    })}

                    </div>
                  )}

                  <div className="workspace-coming-soon">
                    <span>◎</span>
                    <div>
                      <strong>Build evidence as you learn.</strong>
                      <p>
                        Recommendations are not proof of completed learning.
                        Track completion and demonstrate your skills as those
                        features become available.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </section>

          ) : activePage === 'Project Workspace' ? (
            <section className="workspace-placeholder">
              <button
                type="button"
                className="workspace-back-link"
                onClick={() => navigateTo('Overview')}
              >
                ← Back to overview
              </button>

              <span className="eyebrow">PRACTICE AND BUILD</span>
              <h1>Turn knowledge into evidence.</h1>
              <p>
                Use practical projects to practise your skills and build evidence
                of what you can do. Your CV is the starting point, not proof
                that a skill has been demonstrated.
              </p>

              <div className="workspace-section-heading">
                <div>
                  <span className="eyebrow">YOUR STARTING POINT</span>
                  <h2>Skills to build on</h2>
                </div>
                <span className="workspace-status-label">
                  {candidateProfile
                    ? `${candidateProfile.skills?.length ?? 0} detected`
                    : 'No profile yet'}
                </span>
              </div>

              {candidateProfile ? (
                <>
                  {(candidateProfile.skills ?? []).length > 0 ? (
                    <div className="workspace-stat-grid">
                      {candidateProfile.skills.map((skill, index) => {
                        const label =
                          typeof skill === 'string'
                            ? skill
                            : skill.name ?? skill.skill ?? `Skill ${index + 1}`

                        return (
                          <article
                            className="workspace-stat-card"
                            key={`${label}-${index}`}
                          >
                            <span className="workspace-stat-icon lavender">
                              ◇
                            </span>
                            <span className="workspace-stat-label">
                              DETECTED SKILL
                            </span>
                            <strong>{label}</strong>
                            <p>
                              Use this skill as a starting point when planning
                              a practical project.
                            </p>
                          </article>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="workspace-coming-soon">
                      <span>◇</span>
                      <div>
                        <strong>No skills are available to display.</strong>
                        <p>
                          Review your CV profile to understand what information
                          was extracted.
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="workspace-coming-soon">
                    <span>✳</span>
                    <div>
                      <strong>Project tracking is not connected yet.</strong>
                      <p>
                        This screen does not yet load project recommendations
                        or save project completion. No project is marked
                        complete until supporting functionality is integrated.
                      </p>
                      <button
                        type="button"
                        className="workspace-primary-button"
                        onClick={() => navigateTo('My Career')}
                      >
                        Review my profile <span>→</span>
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="workspace-coming-soon">
                  <span>✳</span>
                  <div>
                    <strong>Start with your CV profile.</strong>
                    <p>
                      Analyze your CV to identify skills that can help you
                      plan relevant practice projects.
                    </p>
                    <button
                      type="button"
                      className="workspace-primary-button"
                      onClick={() => navigateTo('My Career')}
                    >
                      Go to My Career <span>→</span>
                    </button>
                  </div>
                </div>
              )}
              <section className="project-ideas-section">
                <div className="workspace-section-heading">
                  <div>
                    <span className="workspace-stat-label">
                      RECOMMENDED PRACTICE
                    </span>
                    <h3>Projects to build next</h3>
                    <p>
                      Choose a project to practise your skills and build portfolio
                      evidence. These are starter suggestions, not saved projects.
                    </p>
                  </div>
                  <span className="workspace-status-label">
                    {targetRole}
                  </span>
                </div>

                <div className="workspace-stat-grid">
                  {projectIdeas.map((project, index) => (
                    <article
                      className="workspace-stat-card project-idea-card"
                      key={project.title}
                    >
                      <span className="workspace-stat-icon violet">
                        {['◈', '▦', '↗'][index]}
                      </span>

                      <span className="workspace-stat-label">
                        PROJECT IDEA {index + 1}
                      </span>

                      <h3>{project.title}</h3>
                      <p>{project.description}</p>

                      <div className="project-skill-list">
                        {project.skills.map((skill) => (
                          <span key={skill}>{skill}</span>
                        ))}
                      </div>

                      <span className="workspace-status-label">
                        Suggested · Not started
                      </span>
                    </article>
                  ))}
                </div>
              </section>

                    <section className="workspace-panel workspace-skills-panel">
                      <div className="workspace-panel-heading">
                        <div>
                          <span className="eyebrow">YOUR SKILL SNAPSHOT</span>
                          <h2>Skills detected in your CV</h2>
                        </div>
                        <span className="workspace-status-label">
                          {skills.length} detected
                        </span>
                      </div>

                      {skills.length > 0 ? (
                        <>
                          <p className="workspace-skills-description">
                            These skills were identified in your CV. Detection
                            does not mean a skill has been verified.
                          </p>

                          <div className="workspace-skill-list">
                            {skills.slice(0, 6).map((skill, index) => (
                              <div
                                className="workspace-skill-item"
                                key={skill.skill_id ?? `${skill.skill_name}-${index}`}
                              >
                                <div className="workspace-skill-info">
                                  <strong>{skill.skill_name}</strong>
                                  <span>
                                    {skill.skill_category || 'Detected skill'}
                                  </span>
                                </div>
                                <span className="workspace-skill-status">
                                  Unverified
                                </span>
                              </div>
                            ))}
                          </div>

                          {skills.length > 6 && (
                            <p className="workspace-skills-more">
                              +{skills.length - 6} more detected skills
                            </p>
                          )}
                        </>
                      ) : (
                        <div className="workspace-skills-empty">
                          <p>
                            {hasProfile
                              ? 'No matching skills were detected in this CV. Review your profile to check the extracted information.'
                              : 'Upload your CV to see the skills GradPath detects here.'}
                          </p>
                          <button
                            type="button"
                            onClick={() => navigateTo('My Career')}
                          >
                            {hasProfile ? 'Review profile' : 'Analyze my CV'} →
                          </button>
                        </div>
                      )}

                      {skills.length > 0 && (
                        <button
                          type="button"
                          className="workspace-skills-link"
                          onClick={() => navigateTo('My Career')}
                        >
                          Review full profile <span>→</span>
                        </button>
                      )}
                    </section>

            </section>
          ) : (
            <section className="workspace-placeholder">
              <button
                type="button"
                className="workspace-back-link"
                onClick={() => navigateTo('Overview')}
              >
                ← Back to overview
              </button>

              <span className="eyebrow">YOUR EVIDENCE-BASED PROGRESS</span>
              <h1>Your readiness report.</h1>
              <p>
                Understand the information currently available about your
                career profile. A meaningful readiness assessment requires
                supporting evidence, not just skills mentioned on a CV.
              </p>

              <div className="workspace-section-heading">
                <div>
                  <span className="eyebrow">CURRENT EVIDENCE</span>
                  <h2>What we know so far</h2>
                </div>
                <span className="workspace-status-label">
                  {candidateProfile ? 'Profile available' : 'Awaiting profile'}
                </span>
              </div>

              <section className="workspace-stat-grid">
                <article className="workspace-stat-card">
                  <span className="workspace-stat-icon lavender">◎</span>
                  <span className="workspace-stat-label">CV PROFILE</span>
                  <strong>
                    {candidateProfile ? 'Available' : 'Not analyzed'}
                  </strong>
                  <p>
                    {candidateProfile
                      ? 'A candidate profile is available for review.'
                      : 'Analyze your CV to establish your starting profile.'}
                  </p>
                  <button
                    type="button"
                    onClick={() => navigateTo('My Career')}
                  >
                    Review profile <span>→</span>
                  </button>
                </article>

                <article className="workspace-stat-card">
                  <span className="workspace-stat-icon teal">↗</span>
                  <span className="workspace-stat-label">SKILL EVIDENCE</span>
                  <strong>
                    {candidateProfile?.skills?.length ?? 0} detected
                  </strong>
                  <p>
                    Detected CV skills are not automatically verified skills.
                  </p>
                  <button
                    type="button"
                    onClick={() => navigateTo('My Career')}
                  >
                    Review skills <span>→</span>
                  </button>
                </article>

                <article className="workspace-stat-card">
                  <span className="workspace-stat-icon violet">◇</span>
                  <span className="workspace-stat-label">LEARNING PLAN</span>
                  <strong>
                    {sharedCareerPlan
                      ? `${sharedCareerPlan.learning_actions?.length ?? 0} actions`
                      : 'Not generated'}
                  </strong>
                  <p>
                    Review learning recommendations for your selected role.
                  </p>
                  <button
                    type="button"
                    onClick={() => navigateTo('Learning Roadmap')}
                  >
                    View roadmap <span>→</span>
                  </button>
                </article>
              </section>

              <div className="workspace-panel workspace-readiness-panel">
                <div className="workspace-panel-heading">
                  <div>
                    <span className="eyebrow">ASSESSMENT STATUS</span>
                    <h2>Evidence before scores.</h2>
                  </div>
                  <span className="workspace-panel-symbol">○</span>
                </div>

                <div className="workspace-empty-state">
                  <div className="workspace-empty-icon">◇</div>
                  <strong>
                    {candidateProfile
                      ? 'Your profile is a starting point.'
                      : 'Your report begins with your CV.'}
                  </strong>
                  <p>
                    {candidateProfile
                      ? 'This overview does not calculate a new readiness score. Skill verification, assessments, and project evidence must be considered by the readiness engine before reporting a score.'
                      : 'Analyze your CV to make your profile available. Readiness results require evidence and a connected assessment engine.'}
                  </p>
                  <button
                    type="button"
                    className="workspace-primary-button"
                    onClick={() => navigateTo('My Career')}
                  >
                    {candidateProfile ? 'Review my career' : 'Analyze my CV'}
                    {' '}<span>→</span>
                  </button>
                </div>
              </div>

              <p className="workspace-footnote">
                This report reflects data available in the current session.
                It does not represent a completed readiness assessment, and
                detected skills should not be interpreted as verified.
              </p>
            </section>
          )}

        </div>
      </main>
    </div>
  )
}

function App() {
  const [screen, setScreen] = useState('landing')
  const [currentUser, setCurrentUser] = useState(null)

  useEffect(() => {
    let isActive = true

    async function restoreSession() {
      try {
        const response = await fetch(API_BASE_URL + '/api/auth/me', {
          credentials: 'include',
        })

        if (!response.ok) return

        const data = await response.json()

        if (isActive && data.user) {
          setCurrentUser(data.user)
          setScreen('workspace')
        }
      } catch {
        // Keep the landing page available if the API is offline.
      }
    }

    restoreSession()

    return () => {
      isActive = false
    }
  }, [])

  async function handleLogout() {
    try {
      await authRequest('/api/auth/logout', {})
      setCurrentUser(null)
      setScreen('landing')
    } catch (error) {
      window.alert(error.message || 'Unable to log out. Please try again.')
    }
  }

  if (screen === 'workspace') {
    return (
      <Workspace
        onNavigate={setScreen}
        onLogout={handleLogout}
        currentUser={currentUser}
      />
    )
  }

  if (screen !== 'landing') {
    return (
      <AuthScreen
        mode={screen}
        onNavigate={setScreen}
        onContinue={(user) => { setCurrentUser(user); setScreen('workspace') }}
      />
    )
  }

  return (
    <div className="site-shell" id="home">
      <header className="site-header">
        <div className="header-inner">
          <Brand />
          <nav className="main-nav" aria-label="Main navigation">
            <a href="#how-it-works">How it works</a>
            <a href="#features">Features</a>
            <a href="#principles">Our approach</a>
          </nav>
          <div className="header-actions">

          <a
            className="login-link"
            href="#login"
            onClick={(event) => {
              event.preventDefault()
              setScreen('login')
            }}
          >
            Log in
          </a>

            <a
                className="button button-dark button-small"
                href="#register"
                onClick={(event) => {
                  event.preventDefault()
                  setScreen('register')
                }}
              >
                Get started <span>→</span>
              </a>
          </div>
        </div>
      </header>

      <main>
        <section className="hero-section">
          <div className="hero-grid">
            <div className="hero-copy">
              <div className="hero-badge">
                <span className="badge-spark">✳</span>
                A more thoughtful way to grow
              </div>
              <h1>
                Your career journey,
                <span> mapped to your </span>
                <em>potential.</em>
              </h1>
              <p className="hero-description">
                Turn what you know into what comes next. Understand your skills,
                find your gaps, and build a practical path toward your career goals.
              </p>
              <div className="hero-actions" id="get-started">
                <a className="button button-dark" href="#features">
                  Explore your possibilities <span>↗</span>
                </a>
                <a className="text-link" href="#how-it-works">
                  See how it works <span>→</span>
                </a>
              </div>
              <div className="hero-trust">
                <div className="trust-avatars" aria-hidden="true">
                  <span>M</span><span>✳</span><span>↗</span>
                </div>
                <p><strong>Built around your growth.</strong><br />Not just another list of skills.</p>
              </div>
            </div>
            <div className="hero-visual">
              <div className="visual-orbit orbit-one" />
              <div className="visual-orbit orbit-two" />
              <DashboardPreview />
            </div>
          </div>
          <div className="hero-bottom">
            <span>YOUR GOALS, MADE PRACTICAL</span>
            <span className="hero-bottom-line" />
            <span>CLARITY <b>·</b> PROGRESS <b>·</b> EVIDENCE</span>
          </div>
        </section>

        <section className="intro-strip" id="how-it-works">
          <div className="intro-label"><span /> A CAREER COMPANION, NOT A SHORTCUT</div>
          <p>
            Real growth happens one step at a time. GradPath helps you make each
            step <strong>clearer, more focused, and easier to act on.</strong>
          </p>
        </section>

        <section className="features-section" id="features">
          <div className="section-heading">
            <div>
              <span className="eyebrow">FROM UNCERTAINTY TO ACTION</span>
              <h2>A path you can actually follow.</h2>
            </div>
            <p>
              Four connected parts. One goal: helping you make informed decisions
              about your career development.
            </p>
          </div>
          <div className="feature-grid">
            {features.map((feature) => (
              <article className="feature-card" key={feature.number}>
                <div className="feature-card-top">
                  <span className="feature-number">{feature.number}</span>
                  <span className="feature-icon">{feature.icon}</span>
                </div>
                <span className="feature-tag">{feature.tag}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <a href="#principles" className="feature-link" aria-label={`Learn about ${feature.title}`}>
                  Learn more <span>↗</span>
                </a>
              </article>
            ))}
          </div>
        </section>

        <section className="principles-section" id="principles">
          <div className="principles-copy">
            <span className="eyebrow">DESIGNED WITH INTENTION</span>
            <h2>Your progress should mean something.</h2>
            <p>
              A skill mentioned on a CV is a starting point, not proof. GradPath
              is designed to distinguish what is mentioned, what is practised,
              and what has verified evidence behind it.
            </p>
            <a href="#get-started" className="button button-light">
              Start with your goals <span>↗</span>
            </a>
          </div>
          <div className="principles-list">
            <div className="principle-item">
              <span className="principle-symbol">01</span>
              <div><strong>Clarity over guesswork</strong><p>Recommendations should explain why they are relevant.</p></div>
            </div>
            <div className="principle-item">
              <span className="principle-symbol">02</span>
              <div><strong>Evidence over assumptions</strong><p>CV mentions and completed projects do not automatically verify skills.</p></div>
            </div>
            <div className="principle-item">
              <span className="principle-symbol">03</span>
              <div><strong>Progress over perfection</strong><p>Build momentum through realistic, actionable next steps.</p></div>
            </div>
          </div>
        </section>

        <section className="closing-section">
          <span className="closing-spark">✳</span>
          <span className="eyebrow">YOUR NEXT CHAPTER STARTS HERE</span>
          <h2>You don't need every answer.<br /><em>Just a clearer next step.</em></h2>
          <a className="button button-dark" href="#features">
            Find your starting point <span>↗</span>
          </a>
        </section>
      </main>

      <footer className="site-footer">
        <Brand />
        <p>Built for thoughtful progress. Powered by evidence.</p>
        <span>GradPath · Career readiness prototype</span>
      </footer>
    </div>
  )
}

export default App
