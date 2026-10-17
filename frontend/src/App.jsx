
import { useState } from 'react'
import './App.css'

const features = [
  {
    number: '01',
    icon: 'âŒ˜',
    title: 'Understand your profile',
    description:
      'Extract skills from your CV and see what your current profile tells you about your next career move.',
    tag: 'CV & PROFILE',
  },
  {
    number: '02',
    icon: 'â—ˆ',
    title: 'Find your skill gaps',
    description:
      'Compare your profile with role-specific skills and understand where to focus your effort.',
    tag: 'SKILL DEVELOPMENT',
  },
  {
    number: '03',
    icon: 'â†—',
    title: 'Build a learning roadmap',
    description:
      'Turn skill gaps into practical learning actions instead of guessing what to learn next.',
    tag: 'LEARNING ROADMAP',
  },
  {
    number: '04',
    icon: 'â–¦',
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
          <span className="preview-menu-item active">â–¦ &nbsp; Overview</span>
          <span className="preview-menu-item">â—Ž &nbsp; My career</span>
          <span className="preview-menu-item">â—‡ &nbsp; Learning</span>
          <span className="preview-menu-item">â†— &nbsp; Projects</span>
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
            <span className="role-chip">Data Analyst â†—</span>
          </div>

          <div className="preview-metrics">
            <div className="metric-card readiness-card">
              <span className="metric-label">VERIFIED SKILL COVERAGE</span>
              <div className="metric-number">â€”<span> / 100%</span></div>
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
              <span className="next-step-icon">âœ³</span>
              <span className="eyebrow">YOUR NEXT STEP</span>
              <strong>Build with purpose.</strong>
              <p>Discover projects aligned with the skills you want to develop.</p>
              <span className="next-step-link">Explore project ideas <span>â†’</span></span>
            </div>
          </div>
          <div className="preview-disclaimer">
            Illustrative preview Â· No real candidate data or scores shown
          </div>
        </div>
      </div>
      <div className="floating-note note-top">
        <span className="note-icon violet-icon">âœ³</span>
        <span><strong>Evidence first</strong><small>Progress with purpose</small></span>
      </div>
      <div className="floating-note note-bottom">
        <span className="note-icon teal-icon">â†—</span>
        <span><strong>One step at a time</strong><small>Your journey, your pace</small></span>
      </div>
    </div>
  )
}


function AuthScreen({ mode, onNavigate, onContinue }) {
  const isLogin = mode === 'login'

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
          â† Back to home
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

        <div className="auth-prototype-notice">
          Prototype preview Â· Authentication is not connected yet.
        </div>

        <form
          onSubmit={(event) => {
            event.preventDefault()
            onContinue?.()
          }}
        >
          {!isLogin && (
            <label className="auth-field">
              Full name
              <input
                type="text"
                name="name"
                placeholder="Your full name"
                autoComplete="name"
                required
              />
            </label>
          )}

          <label className="auth-field">
            Email address
            <input
              type="email"
              name="email"
              placeholder="you@example.com"
              autoComplete="email"
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
              minLength={8}
              required
            />
          </label>

          <button className="button button-dark auth-submit" type="submit">
            {isLogin ? 'Continue to GradPath' : 'Create your account'} <span>â†’</span>
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
          Demo only. Form submissions do not create accounts or save credentials.
        </p>
      </section>

      <footer className="auth-footer">
        GradPath Â· Built for thoughtful progress.
      </footer>
    </main>
  )
}


function MyCareer() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleUpload(event) {
    event.preventDefault()

    if (!selectedFile) {
      setError('Please select a PDF or DOCX file first.')
      return
    }

    setLoading(true)
    setError('')
    setProfile(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(
        'http://127.0.0.1:8000/api/cv/analyze',
        {
          method: 'POST',
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
    } catch (err) {
      setError(
        err.message ||
          'Could not connect to GradPath. Check that the API is running.',
      )
    } finally {
      setLoading(false)
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
            <p>PDF or DOCX Â· Maximum size 5 MB</p>
          </div>
        </div>

        <form onSubmit={handleUpload}>
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
              <span>Education</span>
              <strong>{(profile.education || []).length}</strong>
              <small>Entries extracted</small>
            </article>
            <article className="career-summary-card">
              <span>Experience</span>
              <strong>{(profile.experience || []).length}</strong>
              <small>Entries extracted</small>
            </article>
            <article className="career-summary-card">
              <span>Projects</span>
              <strong>{(profile.projects || []).length}</strong>
              <small>Entries extracted</small>
            </article>
            <article className="career-summary-card">
              <span>Skills</span>
              <strong>{skills.length}</strong>
              <small>Mentions identified</small>
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

                        const displayValue =
                          typeof value === 'object'
                            ? JSON.stringify(value)
                            : String(value)

                        return (
                          <p key={key}>
                            <strong>
                              {key
                                .replace(/_/g, ' ')
                                .replace(/\b\w/g, (char) =>
                                  char.toUpperCase(),
                                )}
                              :
                            </strong>{' '}
                            {displayValue}
                          </p>
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


function Workspace({ onNavigate, onLogout }) {
  const [activePage, setActivePage] = useState('Overview')
  const [targetRole, setTargetRole] = useState('Data Analyst')

  const navigation = [
    { group: 'WORKSPACE', items: [
      { name: 'Overview', icon: 'â—«' },
      { name: 'My Career', icon: 'â—Ž' },
      { name: 'Learning Roadmap', icon: 'â†—' },
      { name: 'Project Workspace', icon: 'â—‡' },
    ] },
    { group: 'YOUR PROGRESS', items: [
      { name: 'Readiness Report', icon: 'â–¤' },
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
            <strong>Guest workspace</strong>
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
            <span className="workspace-help-icon">âœ³</span>
            <strong>Small steps count.</strong>
            <p>Build your career plan one meaningful action at a time.</p>
          </div>
          <button className="workspace-logout" type="button" onClick={onLogout}>
            <span aria-hidden="true">â†©</span> Return to landing page
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
              <section className="workspace-welcome">
                <div>
                  <span className="eyebrow">YOUR CAREER, WITH MORE CLARITY</span>
                  <h1>Your next chapter starts here.</h1>
                  <p>A little progress today can give you a clearer direction tomorrow.</p>
                </div>
                <div className="welcome-decoration" aria-hidden="true">
                  <span className="welcome-orbit orbit-a" />
                  <span className="welcome-orbit orbit-b" />
                  <span className="welcome-star">âœ³</span>
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
                  <select value={targetRole} onChange={(event) => setTargetRole(event.target.value)}>
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
                <span className="workspace-status-label">No profile data connected</span>
              </div>

              <section className="workspace-stat-grid">
                <article className="workspace-stat-card">
                  <span className="workspace-stat-icon lavender">â—Ž</span>
                  <span className="workspace-stat-label">CV PROFILE</span>
                  <strong>Not started</strong>
                  <p>Review your experience and extracted skills.</p>
                  <button type="button" onClick={() => navigateTo('My Career')}>Set up profile <span>â†’</span></button>
                </article>
                <article className="workspace-stat-card">
                  <span className="workspace-stat-icon teal">â†—</span>
                  <span className="workspace-stat-label">LEARNING ROADMAP</span>
                  <strong>Ready to explore</strong>
                  <p>Discover learning actions for your target role.</p>
                  <button type="button" onClick={() => navigateTo('Learning Roadmap')}>View roadmap <span>â†’</span></button>
                </article>
                <article className="workspace-stat-card">
                  <span className="workspace-stat-icon violet">â—‡</span>
                  <span className="workspace-stat-label">PROJECT WORKSPACE</span>
                  <strong>Start building</strong>
                  <p>Find projects that help you practise your skills.</p>
                  <button type="button" onClick={() => navigateTo('Project Workspace')}>Explore projects <span>â†’</span></button>
                </article>
              </section>

              <section className="workspace-bottom-grid">
                <article className="workspace-panel workspace-readiness-panel">
                  <div className="workspace-panel-heading">
                    <div>
                      <span className="eyebrow">READINESS OVERVIEW</span>
                      <h2>Evidence before scores.</h2>
                    </div>
                    <span className="workspace-panel-symbol">â—Œ</span>
                  </div>
                  <div className="workspace-empty-state">
                    <div className="workspace-empty-icon">â–¤</div>
                    <strong>Your report will grow with you.</strong>
                    <p>Connect a profile and build evidence before reviewing your readiness results.</p>
                    <button type="button" onClick={() => navigateTo('Readiness Report')}>About readiness reports <span>â†’</span></button>
                  </div>
                </article>

                <article className="workspace-panel workspace-next-panel">
                  <span className="eyebrow">A GOOD FIRST STEP</span>
                  <div className="workspace-next-icon">âœ³</div>
                  <h2>Begin with your CV.</h2>
                  <p>Your CV helps establish a starting profile. Extracted skill mentions remain unverified until supported by appropriate evidence.</p>
                  <button type="button" className="workspace-primary-button" onClick={() => navigateTo('My Career')}>
                    Explore my career <span>â†’</span>
                  </button>
                </article>
              </section>

              <p className="workspace-footnote">
                GradPath prototype Â· No candidate records, scores or learning progress are loaded in this screen yet.
              </p>
            </>
          ) : activePage === 'My Career' ? (
            <MyCareer />
          ) : (
            <section className="workspace-placeholder">
              <button type="button" className="workspace-back-link" onClick={() => navigateTo('Overview')}>
                â† Back to overview
              </button>
              <div className="workspace-placeholder-icon">
                {activePage === 'My Career' ? 'â—Ž' : activePage === 'Learning Roadmap' ? 'â†—' : activePage === 'Project Workspace' ? 'â—‡' : 'â–¤'}
              </div>
              <span className="eyebrow">{pageInfo.eyebrow}</span>
              <h1>{pageInfo.title}</h1>
              <p>{pageInfo.description}</p>
              <div className="workspace-coming-soon">
                <span>âœ³</span>
                <div>
                  <strong>This section is the next part of GradPath.</strong>
                  <p>The navigation is ready. We'll connect this screen to the existing Python engine in a later integration phase.</p>
                </div>
              </div>
              <button
                type="button"
                className="workspace-primary-button"
                onClick={() => navigateTo(activePage === 'Readiness Report' ? 'My Career' : 'Overview')}
              >
                {pageInfo.action} <span>â†’</span>
              </button>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}


function App() {
  const [screen, setScreen] = useState('landing')

  if (screen === 'workspace') {
    return (
      <Workspace
        onNavigate={setScreen}
        onLogout={() => setScreen('landing')}
      />
    )
  }

  if (screen !== 'landing') {
    return (
      <AuthScreen
        mode={screen}
        onNavigate={setScreen}
        onContinue={() => setScreen('workspace')}
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
                Get started <span>â†’</span>
              </a>
          </div>
        </div>
      </header>

      <main>
        <section className="hero-section">
          <div className="hero-grid">
            <div className="hero-copy">
              <div className="hero-badge">
                <span className="badge-spark">âœ³</span>
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
                  Explore your possibilities <span>â†—</span>
                </a>
                <a className="text-link" href="#how-it-works">
                  See how it works <span>â†’</span>
                </a>
              </div>
              <div className="hero-trust">
                <div className="trust-avatars" aria-hidden="true">
                  <span>M</span><span>âœ³</span><span>â†—</span>
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
            <span>CLARITY <b>Â·</b> PROGRESS <b>Â·</b> EVIDENCE</span>
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
                  Learn more <span>â†—</span>
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
              Start with your goals <span>â†—</span>
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
          <span className="closing-spark">âœ³</span>
          <span className="eyebrow">YOUR NEXT CHAPTER STARTS HERE</span>
          <h2>You don't need every answer.<br /><em>Just a clearer next step.</em></h2>
          <a className="button button-dark" href="#features">
            Find your starting point <span>â†—</span>
          </a>
        </section>
      </main>

      <footer className="site-footer">
        <Brand />
        <p>Built for thoughtful progress. Powered by evidence.</p>
        <span>GradPath Â· Career readiness prototype</span>
      </footer>
    </div>
  )
}

export default App
