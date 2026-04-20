import Link from "next/link";

import { ParallaxStage } from "@/components/app/parallax-stage";
import { ThemeToggle } from "@/components/theme/theme-toggle";

const featureCards = [
  {
    title: "Offline chat",
    copy:
      "Conversational AI powered by Phi-3 through Ollama, with responses generated locally and context preserved inside your own stack.",
    bullets: [
      "No cloud dependency once configured",
      "No remote memory layer or hidden sync",
      "Live conversation wired to the FastAPI backend",
    ],
  },
  {
    title: "Task + event capture",
    copy:
      "Natural language can become real tasks and schedule entries through the backend workflows already running in your project.",
    bullets: [
      "Task extraction from chat",
      "Event creation and local schedule storage",
      "Encrypted persistence before disk writes",
    ],
  },
  {
    title: "Notes and summaries",
    copy:
      "Long notes stay readable. PrivAI can summarize local text through the Ollama model and keep the result saved in your backend database.",
    bullets: [
      "Upload files from chat or summarize manually",
      "Saved summaries remain local",
      "Live dashboard reflects current stored counts",
    ],
  },
];

const compareCells = [
  {
    title: "Runs offline",
    text: "No network dependency after setup. The backend, model, database, and UI continue to function locally.",
    strong: "Always local",
  },
  {
    title: "Data on your device",
    text: "Structured records stay inside your own database and application stack instead of a hosted SaaS backend.",
    strong: "No remote copy",
  },
  {
    title: "Encrypted storage",
    text: "Sensitive content is protected before persistence and exposed back to the UI only through the backend contract.",
    strong: "Fernet-backed",
  },
  {
    title: "Full product flow",
    text: "Landing, chat, tasks, notes, events, analytics, and health checks now share one visual system.",
    strong: "End-to-end wired",
  },
];

export default function LandingPage() {
  const year = new Date().getFullYear();

  return (
    <main className="page-shell">
      <section className="panel hero" id="top">
        <header className="topbar">
          <a className="brand" href="#top" aria-label="PrivAI home">
            <span className="brand-mark" aria-hidden="true">
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none">
                <path
                  d="M7 11V8.8C7 5.6 9.6 3 12.8 3C16 3 18.6 5.6 18.6 8.8V11"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
                <rect x="5" y="10" width="15" height="11" rx="3" stroke="currentColor" strokeWidth="1.8" />
                <path d="M12.5 14.2V17.1" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </span>
            <span>PrivAI</span>
          </a>
          <nav className="nav" aria-label="Primary">
            <a href="#features">Features</a>
            <a href="#architecture">Architecture</a>
            <a href="#dashboard">Dashboard</a>
            <a href="#compare">Why it works</a>
          </nav>
          <div className="button-row">
            <ThemeToggle compact />
            <Link className="button button-secondary" href="/dashboard">
              Open Dashboard
            </Link>
            <Link className="button button-primary" href="/chat">
              Launch PrivAI
            </Link>
          </div>
        </header>

        <div className="hero-grid">
          <div className="reveal">
            <span className="eyebrow">Private AI Assistant</span>
            <h1>Local intelligence with zero cloud exposure.</h1>
            <p>
              PrivAI now uses your new interface system across the whole product. The polished landing
              experience is connected to the live backend stack for chat, tasks, notes, events,
              analytics, and model health.
            </p>
            <div className="button-row">
              <Link className="button button-primary" href="/chat">
                Open Chat Workspace
              </Link>
              <a className="button button-secondary" href="#architecture">
                How it works
              </a>
            </div>
            <div className="hero-meta">
              <span className="hero-chip">
                <strong>100% local</strong> runtime
              </span>
              <span className="hero-chip">
                <strong>Phi-3</strong> via Ollama
              </span>
              <span className="hero-chip">
                <strong>MySQL</strong> persistence
              </span>
              <span className="hero-chip">
                <strong>FastAPI</strong> orchestrated features
              </span>
            </div>
          </div>

          <ParallaxStage>
            <div className="orbital-lines" aria-hidden="true" data-depth="0.55">
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="line-axis" aria-hidden="true" data-depth="0.45" />
            <div className="lock-node" aria-hidden="true" data-depth="0.2">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
                <path
                  d="M7 11V8.8C7 5.6 9.6 3 12.8 3C16 3 18.6 5.6 18.6 8.8V11"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
                <rect x="5" y="10" width="15" height="11" rx="3" stroke="currentColor" strokeWidth="1.8" />
                <path d="M12.5 14.2V17.1" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </div>

            <article className="floating-card top-left float" data-depth="0.95">
              <h3>Chat locally</h3>
              <p>Talk to the model through the live FastAPI backend with zero external API dependence.</p>
              <div className="visual-stat">
                <span className="dot" />
                <strong>Session + memory</strong> stay private
              </div>
            </article>

            <article className="floating-card top-right float-delayed" data-depth="1.1">
              <h3>Task + event capture</h3>
              <p>Natural language flows can create tasks and schedule records directly in the database.</p>
              <div className="visual-stat">
                <span className="dot" />
                <strong>Structured actions</strong> from plain text
              </div>
            </article>

            <article className="floating-card bottom-left float-slow" data-depth="1">
              <h3>Notes workflow</h3>
              <p>Upload or paste source text and keep generated summaries available inside the new workspace.</p>
              <div className="visual-stat">
                <span className="dot" />
                <strong>Original + summary</strong> saved locally
              </div>
            </article>

            <article className="floating-card bottom-right float" data-depth="0.9">
              <h3>Live dashboard</h3>
              <p>Inspect model health, counts, analytics, and protected-storage previews from one surface.</p>
              <div className="visual-stat">
                <span className="dot" />
                <strong>Runtime visibility</strong> across the stack
              </div>
            </article>
          </ParallaxStage>
        </div>
      </section>

      <section id="features" className="panel section reveal">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Core Features</span>
            <h2>The new interface, wired to real workflows.</h2>
          </div>
          <p>
            The new UI is not just a landing page anymore. It now fronts the existing backend
            contract end to end, so the visuals and the product behavior finally match.
          </p>
        </div>

        <div className="grid-3">
          {featureCards.map((card, index) => (
            <article key={card.title} className={`feature-card reveal stagger-${index + 1}`}>
              <div className="icon-wrap" aria-hidden="true">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M6 12L10 16L18 8"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <h3>{card.title}</h3>
              <p>{card.copy}</p>
              <ul>
                {card.bullets.map((bullet) => (
                  <li key={bullet}>{bullet}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="panel section reveal">
        <div className="metrics">
          <div className="metrics-board reveal stagger-1">
            <div className="section-heading">
              <div>
                <span className="eyebrow">What changed</span>
                <h2>Motion and depth without losing reliability.</h2>
              </div>
              <p>
                The original animations are preserved and smoothed out with stronger easing, layered
                aurora lighting, and subtle 3D parallax so the interface feels more premium without
                making the app harder to maintain.
              </p>
            </div>
            <div className="metrics-grid">
              <article className="metric">
                <div className="value">Live</div>
                <div className="label">chat, tasks, notes, and events connected to the backend</div>
              </article>
              <article className="metric">
                <div className="value">Smooth</div>
                <div className="label">parallax, floating cards, and reveal transitions</div>
              </article>
              <article className="metric">
                <div className="value">1</div>
                <div className="label">shared visual system across landing and workspace pages</div>
              </article>
              <article className="metric">
                <div className="value">0</div>
                <div className="label">extra backend contract changes required for the UI swap</div>
              </article>
            </div>
          </div>

          <aside className="terminal-panel reveal stagger-2">
            <div className="terminal-header">
              <div>
                <span className="eyebrow">Local Run</span>
                <h3>Connected app stack</h3>
              </div>
            </div>
            <div className="terminal-body">
              <div className="terminal-line">
                <span className="terminal-prompt">$</span>
                <span>docker compose up -d mysql backend frontend</span>
              </div>
              <div className="terminal-line">
                <span className="terminal-prompt">&gt;</span>
                <span>MySQL healthy on <strong>localhost:3307</strong></span>
              </div>
              <div className="terminal-line">
                <span className="terminal-prompt">&gt;</span>
                <span>FastAPI live on <strong>localhost:8000</strong></span>
              </div>
              <div className="terminal-line">
                <span className="terminal-prompt">&gt;</span>
                <span>Next.js workspace live on <strong>localhost:3000</strong></span>
              </div>
              <div className="terminal-line">
                <span className="terminal-prompt">&gt;</span>
                <span>Ollama model reachable through the backend status checks</span>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section id="architecture" className="panel section reveal">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Architecture</span>
            <h2>UI to API to storage to model.</h2>
          </div>
          <p>
            The landing page now reflects the real stack already running in this repo: Next.js on the
            frontend, FastAPI on the backend, MySQL for persisted records, and Ollama for local inference.
          </p>
        </div>

        <div className="story-layout">
          <article className="story-card reveal stagger-1">
            <span className="eyebrow">Core stack</span>
            <h3>Built for local execution, not hosted dependency.</h3>
            <ul className="story-list">
              <li>The frontend calls FastAPI only, never the database directly.</li>
              <li>Backend routes still own validation, orchestration, and encryption boundaries.</li>
              <li>MySQL persists tasks, notes, events, and behavior analytics.</li>
              <li>Ollama serves the local Phi-3 model for chat and summaries.</li>
              <li>Docker still starts the whole stack with aligned ports and environment values.</li>
            </ul>
          </article>

          <article className="story-card reveal stagger-2">
            <span className="eyebrow">Request flow</span>
            <h3>Simple enough to trust at a glance.</h3>
            <div className="flow-lanes">
              <div className="flow-lane">
                <div className="flow-box">
                  <strong>User prompt</strong>
                  <span>Chat, summarize, or save an event.</span>
                </div>
                <div className="flow-arrow" aria-hidden="true" />
                <div className="flow-box">
                  <strong>FastAPI</strong>
                  <span>Routes requests through local services.</span>
                </div>
                <div className="flow-arrow" aria-hidden="true" />
                <div className="flow-box">
                  <strong>Ollama / MySQL</strong>
                  <span>Generate locally or persist locally.</span>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section id="dashboard" className="panel section reveal">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Dashboard</span>
            <h2>Health and privacy made visible.</h2>
          </div>
          <p>
            The new dashboard route now surfaces system checks, analytics, counts, and protected
            payload previews using the live backend endpoints already present in the project.
          </p>
        </div>

        <div className="privacy-layout">
          <article className="dashboard-card reveal stagger-1">
            <div className="dashboard-header">
              <div>
                <span className="eyebrow">Runtime checks</span>
                <h3>Model, database, and storage state</h3>
              </div>
              <span className="mini-chip">
                <strong>Live</strong> connected routes
              </span>
            </div>
            <div className="dashboard-columns">
              <section className="data-column">
                <h4>Chat</h4>
                <div className="data-pill">
                  Wired to the `/chat` endpoint
                  <code>Local assistant messages and action extraction</code>
                </div>
              </section>
              <section className="data-column">
                <h4>Notes</h4>
                <div className="data-pill">
                  Wired to `/summarize` and `/summaries`
                  <code>Stored summaries and original note text</code>
                </div>
              </section>
              <section className="data-column">
                <h4>System</h4>
                <div className="data-pill">
                  Wired to `/system/status` and `/analytics`
                  <code>Health checks, counts, and analytics timeline</code>
                </div>
              </section>
            </div>
          </article>

          <article className="delete-card reveal stagger-2">
            <div>
              <span className="eyebrow">Workspace routes</span>
              <h3>Every feature now lives inside the new visual system.</h3>
              <ul className="privacy-list">
                <li>Landing page uses the new UI direction.</li>
                <li>Chat, tasks, notes, events, and dashboard use the same shell.</li>
                <li>Motion is smoother and layered with subtle 3D depth.</li>
              </ul>
            </div>
            <Link className="delete-cta" href="/dashboard">
              Open live dashboard
            </Link>
          </article>
        </div>
      </section>

      <section id="compare" className="panel section reveal">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Outcome</span>
            <h2>Why this replacement is better than a skin-only swap.</h2>
          </div>
          <p>
            The frontend is no longer split between a polished concept and a basic working app. The
            concept now is the app, and it is wired to the real backend features.
          </p>
        </div>

        <div className="compare-strip">
          {compareCells.map((cell, index) => (
            <article key={cell.title} className={`compare-cell reveal stagger-${index + 1}`}>
              <h4>{cell.title}</h4>
              <p>{cell.text}</p>
              <strong>{cell.strong}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="panel cta-panel reveal">
        <div className="cta-inner">
          <div className="cta-copy reveal stagger-1">
            <span className="eyebrow">PrivAI</span>
            <h2>Your assistant. Your laptop. Your stack.</h2>
            <p>
              The new UI has replaced the old frontend while keeping the existing backend contract,
              Docker setup, database workflow, and local Ollama integration intact.
            </p>
            <div className="button-row">
              <Link className="button button-primary" href="/chat">
                Launch workspace
              </Link>
              <Link className="button button-secondary" href="/notes">
                Open notes
              </Link>
            </div>
          </div>

          <div className="notes-stack">
            <article className="cta-card reveal stagger-2">
              <span className="eyebrow">Visual direction</span>
              <h3>Polished motion, restrained depth.</h3>
              <p>
                Smooth parallax, better easing, layered glow fields, and glass surfaces add depth
                without turning the interface into gimmick-heavy motion design.
              </p>
            </article>
            <article className="cta-card reveal stagger-3">
              <span className="eyebrow">Feature coverage</span>
              <h3>Nothing was left as a static mockup.</h3>
              <p>
                Chat sends requests, tasks update, notes summarize, events save, and the dashboard
                reflects system state from the backend.
              </p>
            </article>
          </div>
        </div>

        <footer className="footer">
          <span>PrivAI local-first workspace</span>
          <span>Copyright {year} PrivAI</span>
        </footer>
      </section>
    </main>
  );
}
