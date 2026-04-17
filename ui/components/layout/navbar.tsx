"use client";

import { useState } from "react";

import { ThemeToggle } from "@/components/theme/theme-toggle";
import { LinkButton } from "@/components/ui/button";
import { MenuIcon } from "@/components/ui/icons";

export function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="section-shell sticky top-0 z-40 pt-5">
      <div className="glass-panel rounded-[30px] px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div
              className="font-semibold uppercase tracking-[0.3em] text-[var(--info)]"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              PrivAI
            </div>
            <div className="text-xs muted">Privacy-preserving AI assistant</div>
          </div>

          <nav className="hidden items-center gap-6 text-sm text-text/80 md:flex">
            <a href="#features">Features</a>
            <a href="#privacy">Privacy</a>
            <a href="#dashboard">Dashboard</a>
          </nav>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <LinkButton href="#dashboard" className="hidden sm:inline-flex">
              Launch Preview
            </LinkButton>
            <button
              type="button"
              aria-label="Toggle menu"
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((current) => !current)}
              className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/5 text-text transition hover:bg-white/10"
            >
              <MenuIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="mt-4 grid gap-2 rounded-[24px] border border-white/10 bg-black/10 p-3 md:hidden">
            <a
              href="#features"
              onClick={() => setMenuOpen(false)}
              className="rounded-2xl px-4 py-3 transition hover:bg-white/5"
            >
              Features
            </a>
            <a
              href="#privacy"
              onClick={() => setMenuOpen(false)}
              className="rounded-2xl px-4 py-3 transition hover:bg-white/5"
            >
              Privacy
            </a>
            <a
              href="#dashboard"
              onClick={() => setMenuOpen(false)}
              className="rounded-2xl px-4 py-3 transition hover:bg-white/5"
            >
              Dashboard
            </a>
          </div>
        )}
      </div>
    </header>
  );
}
