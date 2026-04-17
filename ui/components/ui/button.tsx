import { AnchorHTMLAttributes, ButtonHTMLAttributes } from "react";

type SharedProps = {
  variant?: "primary" | "secondary";
  children: React.ReactNode;
};

const classes = {
  primary:
    "bg-gradient-to-r from-[var(--accent)] to-[var(--info)] text-white shadow-glow",
  secondary:
    "glass-panel text-text hover:bg-white/5",
};

export function Button({
  variant = "primary",
  children,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & SharedProps) {
  return (
    <button
      {...props}
      className={`inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition hover:-translate-y-0.5 ${classes[variant]} ${className}`}
    >
      {children}
    </button>
  );
}

export function LinkButton({
  variant = "primary",
  children,
  className = "",
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & SharedProps) {
  return (
    <a
      {...props}
      className={`inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition hover:-translate-y-0.5 ${classes[variant]} ${className}`}
    >
      {children}
    </a>
  );
}
