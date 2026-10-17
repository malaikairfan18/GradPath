
import './App.css'

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

function App() {
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
            <a className="login-link" href="#get-started">Log in</a>
            <a className="button button-dark button-small" href="#get-started">
              Get started <span>↗</span>
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
