"use client";

import { useTheme } from "@/components/theme/theme-provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="glass-panel inline-flex items-center gap-3 rounded-full px-3 py-2 text-sm text-text transition hover:scale-[1.02]"
      aria-label="Toggle theme"
    >
      <span
        className={`inline-flex h-7 w-12 items-center rounded-full border border-white/10 p-1 transition ${
          theme === "light" ? "bg-[var(--accent-soft)]" : "bg-white/5"
        }`}
      >
        <span
          className={`h-5 w-5 rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--info)] transition ${
            theme === "light" ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </span>
      <span>{theme === "dark" ? "Dark Mode" : "Light Mode"}</span>
    </button>
  );
}
