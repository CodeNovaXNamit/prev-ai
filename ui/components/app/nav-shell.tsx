"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/tasks", label: "Tasks" },
  { href: "/events", label: "Events" },
  { href: "/summaries", label: "Summaries" },
  { href: "/dashboard", label: "Dashboard" },
];

export function NavShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <div className="app-title">PrivAI</div>
          <div className="app-subtitle">Private local assistant</div>
        </div>
        <nav className="app-nav">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={pathname === link.href ? "nav-link nav-link-active" : "nav-link"}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </header>
      <main className="page-wrap">{children}</main>
    </div>
  );
}
