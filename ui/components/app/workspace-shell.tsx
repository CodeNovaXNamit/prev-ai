"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { ThemeToggle } from "@/components/theme/theme-toggle";

const navItems = [
  { href: "/chat", label: "Chat" },
  { href: "/tasks", label: "Tasks" },
  { href: "/notes", label: "Notes" },
  { href: "/events", label: "Events" },
  { href: "/dashboard", label: "Dashboard" },
];

export function WorkspaceShell({
  title,
  description,
  actions,
  children,
}: {
  title: string;
  description: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <main className="workspace-shell">
      <div className="workspace-frame">
        <header className="workspace-topbar">
          <div className="workspace-brand">
            <Link href="/" className="workspace-logo" aria-label="PrivAI home">
              <span className="brand-mark workspace-brand-mark" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
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
              <div>
                <strong>PrivAI</strong>
                <span>Private local assistant</span>
              </div>
            </Link>
          </div>

          <div className="workspace-nav-wrap">
            <nav className="workspace-nav" aria-label="Assistant routes">
              {navItems.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`workspace-nav-link ${active ? "workspace-nav-link-active" : ""}`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            <ThemeToggle compact />
          </div>
        </header>

        <section className="workspace-hero-card reveal">
          <div>
            <span className="eyebrow">Workspace</span>
            <h1>{title}</h1>
            <p>{description}</p>
          </div>
          {actions ? <div className="button-row">{actions}</div> : null}
        </section>

        {children}
      </div>
    </main>
  );
}
