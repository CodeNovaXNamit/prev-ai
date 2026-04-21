"use client";

import { useEffect, useRef, useState } from "react";

type FeatureCard = {
  title: string;
  copy: string;
  bullets: string[];
};

type CompareCell = {
  title: string;
  text: string;
  strong: string;
};

type TiltPanelProps = {
  children: React.ReactNode;
  className: string;
};

function TiltPanel({ children, className }: TiltPanelProps) {
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    let frame = 0;
    let nextX = 0;
    let nextY = 0;

    const render = () => {
      node.style.setProperty("--tilt-x", `${nextX.toFixed(2)}deg`);
      node.style.setProperty("--tilt-y", `${nextY.toFixed(2)}deg`);
      node.style.setProperty("--glow-x", `${50 + nextY * 8}%`);
      node.style.setProperty("--glow-y", `${50 - nextX * 8}%`);
      frame = 0;
    };

    const queue = () => {
      if (!frame) {
        frame = window.requestAnimationFrame(render);
      }
    };

    const handleMove = (event: PointerEvent) => {
      const rect = node.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;
      nextX = y * -7;
      nextY = x * 9;
      queue();
    };

    const handleLeave = () => {
      nextX = 0;
      nextY = 0;
      queue();
    };

    node.addEventListener("pointermove", handleMove);
    node.addEventListener("pointerleave", handleLeave);

    return () => {
      node.removeEventListener("pointermove", handleMove);
      node.removeEventListener("pointerleave", handleLeave);
      if (frame) {
        window.cancelAnimationFrame(frame);
      }
    };
  }, []);

  return (
    <article ref={ref} className={`${className} live-tilt-panel`}>
      {children}
    </article>
  );
}

export function LiveFeatureGrid({ cards }: { cards: FeatureCard[] }) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActive((current) => (current + 1) % cards.length);
    }, 3000);

    return () => window.clearInterval(timer);
  }, [cards.length]);

  return (
    <div className="grid-3 live-grid">
      {cards.map((card, index) => (
        <TiltPanel
          key={card.title}
          className={`feature-card reveal stagger-${index + 1} ${active === index ? "is-live" : ""}`}
        >
          <div className="live-card-topline" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div className="live-card-meta">
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
            <span className="micro-status">
              <span className="micro-status-dot" />
              live workflow
            </span>
          </div>
          <h3>{card.title}</h3>
          <p>{card.copy}</p>
          <ul>
            {card.bullets.map((bullet) => (
              <li key={bullet}>{bullet}</li>
            ))}
          </ul>
        </TiltPanel>
      ))}
    </div>
  );
}

export function LiveMetricsSection() {
  const metrics = [
    {
      value: "Live",
      label: "chat, tasks, notes, and events connected to the backend",
      meter: "92%",
    },
    {
      value: "Smooth",
      label: "parallax, floating cards, and reveal transitions",
      meter: "88%",
    },
    {
      value: "1",
      label: "shared visual system across landing and workspace pages",
      meter: "100%",
    },
    {
      value: "0",
      label: "extra backend contract changes required for the UI swap",
      meter: "0%",
    },
  ];

  const terminalFrames = [
    "booting landing motion layer...",
    "binding section cards to hover + scroll depth...",
    "syncing flow state with live product narrative...",
    "hackathon mode: presentable and production-shaped",
  ];

  const [frame, setFrame] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setFrame((current) => (current + 1) % terminalFrames.length);
    }, 2600);

    return () => window.clearInterval(timer);
  }, [terminalFrames.length]);

  return (
    <div className="metrics">
      <div className="metrics-board reveal stagger-1 live-board">
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
          {metrics.map((metric, index) => (
            <TiltPanel
              key={metric.label}
              className={`metric ${frame === index ? "is-live" : ""}`}
            >
              <div className="value">{metric.value}</div>
              <div className="label">{metric.label}</div>
              <div className="metric-meter" aria-hidden="true">
                <div style={{ width: metric.meter }} />
              </div>
            </TiltPanel>
          ))}
        </div>
      </div>

      <aside className="terminal-panel reveal stagger-2 live-terminal-panel">
        <div className="terminal-header">
          <div>
            <span className="eyebrow">Local Run</span>
            <h3>Connected app stack</h3>
          </div>
          <span className="micro-status">
            <span className="micro-status-dot" />
            stable loop
          </span>
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
          <div className="terminal-line terminal-stream">
            <span className="terminal-prompt">*</span>
            <span key={frame} className="terminal-stream-copy">
              {terminalFrames[frame]}
            </span>
          </div>
          <div className="terminal-activity" aria-hidden="true">
            <span />
            <span />
            <span />
            <span />
          </div>
        </div>
      </aside>
    </div>
  );
}

export function LiveArchitectureSection() {
  const flowSteps = [
    {
      title: "User prompt",
      text: "Chat, summarize, or save an event.",
    },
    {
      title: "FastAPI",
      text: "Routes requests through local services.",
    },
    {
      title: "Ollama / MySQL",
      text: "Generate locally or persist locally.",
    },
  ];

  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActive((current) => (current + 1) % flowSteps.length);
    }, 2200);

    return () => window.clearInterval(timer);
  }, [flowSteps.length]);

  return (
    <div className="story-layout live-story-layout">
      <TiltPanel className="story-card reveal stagger-1 is-live">
        <span className="eyebrow">Core stack</span>
        <h3>Built for local execution, not hosted dependency.</h3>
        <ul className="story-list">
          <li>The frontend calls FastAPI only, never the database directly.</li>
          <li>Backend routes still own validation, orchestration, and encryption boundaries.</li>
          <li>MySQL persists tasks, notes, events, and behavior analytics.</li>
          <li>Ollama serves the local Phi-3 model for chat and summaries.</li>
          <li>Docker still starts the whole stack with aligned ports and environment values.</li>
        </ul>
        <div className="story-signal-strip" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
      </TiltPanel>

      <TiltPanel className="story-card reveal stagger-2 live-flow-card">
        <span className="eyebrow">Request flow</span>
        <h3>Simple enough to trust at a glance.</h3>
        <div className="flow-lanes">
          <div className="flow-lane live-flow-lane">
            {flowSteps.map((step, index) => (
              <div key={step.title} className="live-flow-step">
                <div className={`flow-box ${active === index ? "is-live" : ""}`}>
                  <strong>{step.title}</strong>
                  <span>{step.text}</span>
                </div>
                {index < flowSteps.length - 1 ? (
                  <div className={`flow-arrow ${active === index ? "is-live" : ""}`} aria-hidden="true" />
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </TiltPanel>
    </div>
  );
}

export function LiveOutcomeSection({ cells }: { cells: CompareCell[] }) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActive((current) => (current + 1) % cells.length);
    }, 2600);

    return () => window.clearInterval(timer);
  }, [cells.length]);

  return (
    <div className="compare-strip live-compare-strip compare-stage">
      {cells.map((cell, index) => (
        <TiltPanel
          key={cell.title}
          className={`compare-cell reveal stagger-${index + 1} ${active === index ? "is-live" : ""}`}
        >
          <span className="compare-shine" aria-hidden="true" />
          <h4>{cell.title}</h4>
          <p>{cell.text}</p>
          <strong>{cell.strong}</strong>
        </TiltPanel>
      ))}
    </div>
  );
}
