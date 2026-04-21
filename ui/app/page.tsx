import Link from "next/link";

import { ParallaxStage } from "@/components/app/parallax-stage";
import {
  LiveArchitectureSection,
  LiveFeatureGrid,
  LiveMetricsSection,
  LiveOutcomeSection,
} from "@/components/landing/live-sections";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { BrandLogo } from "@/components/ui/brand-logo";

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
              <BrandLogo className="brand-logo-svg" />
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
            <div className="orbital-lines parallax-item" aria-hidden="true" data-depth="0.55">
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="line-axis parallax-item" aria-hidden="true" data-depth="0.45" />
            <div className="lock-node parallax-item" aria-hidden="true" data-depth="0.2">
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

            <div className="floating-card-shell top-left parallax-item" data-depth="0.95">
              <article className="floating-card float">
                <h3>Chat locally</h3>
                <p>Talk to the model through the live FastAPI backend with zero external API dependence.</p>
                <div className="visual-stat">
                  <span className="dot" />
                  <strong>Session + memory</strong> stay private
                </div>
              </article>
            </div>

            <div className="floating-card-shell top-right parallax-item" data-depth="1.1">
              <article className="floating-card float-delayed">
                <h3>Task + event capture</h3>
                <p>Natural language flows can create tasks and schedule records directly in the database.</p>
                <div className="visual-stat">
                  <span className="dot" />
                  <strong>Structured actions</strong> from plain text
                </div>
              </article>
            </div>

            <div className="floating-card-shell bottom-left parallax-item" data-depth="1">
              <article className="floating-card float-slow">
                <h3>Notes workflow</h3>
                <p>Upload or paste source text and keep generated summaries available inside the new workspace.</p>
                <div className="visual-stat">
                  <span className="dot" />
                  <strong>Original + summary</strong> saved locally
                </div>
              </article>
            </div>

            <div className="floating-card-shell bottom-right parallax-item" data-depth="0.9">
              <article className="floating-card float">
                <h3>Live dashboard</h3>
                <p>Inspect model health, counts, analytics, and protected-storage previews from one surface.</p>
                <div className="visual-stat">
                  <span className="dot" />
                  <strong>Runtime visibility</strong> across the stack
                </div>
              </article>
            </div>
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

        <LiveFeatureGrid cards={featureCards} />
      </section>

      <section className="panel section reveal">
        <LiveMetricsSection />
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

        <LiveArchitectureSection />
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

      <section id="compare" className="panel section reveal compare-section">
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

        <LiveOutcomeSection cells={compareCells} />
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
