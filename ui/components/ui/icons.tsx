import { PropsWithChildren, SVGProps } from "react";

function IconBase({
  children,
  ...props
}: PropsWithChildren<SVGProps<SVGSVGElement>>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      {children}
    </svg>
  );
}

export const ShieldIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M12 3l7 3.8v5.7c0 4.2-2.8 8-7 9.5-4.2-1.5-7-5.3-7-9.5V6.8L12 3z" />
    <path d="M9.5 12l1.7 1.7 3.6-3.9" />
  </IconBase>
);

export const SparkIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M12 2l1.8 4.8L18.5 8l-4.7 1.2L12 14l-1.8-4.8L5.5 8l4.7-1.2L12 2z" />
    <path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15z" />
    <path d="M5 15l.6 1.6L7.2 17l-1.6.6L5 19.2l-.6-1.6L2.8 17l1.6-.4L5 15z" />
  </IconBase>
);

export const NotesIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <rect x="5" y="3" width="14" height="18" rx="2" />
    <path d="M9 8h6M9 12h6M9 16h4" />
  </IconBase>
);

export const TaskIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M9 11l2 2 4-5" />
    <circle cx="12" cy="12" r="9" />
  </IconBase>
);

export const ChatIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M7 18l-4 3V6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H7z" />
    <path d="M8 9h8M8 13h6" />
  </IconBase>
);

export const SummaryIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M6 5h12M6 10h12M6 15h8M18 20l3-3-3-3" />
  </IconBase>
);

export const MenuIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M4 7h16" />
    <path d="M4 12h16" />
    <path d="M4 17h16" />
  </IconBase>
);

export const UploadIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M12 16V5" />
    <path d="M8 9l4-4 4 4" />
    <path d="M5 19h14" />
  </IconBase>
);

export const FolderIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M3 7.5A2.5 2.5 0 0 1 5.5 5H9l2 2h7.5A2.5 2.5 0 0 1 21 9.5v7A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5z" />
  </IconBase>
);

export const WaveIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M3 14c2.2 0 2.8-4 5-4s2.8 4 5 4 2.8-4 5-4 2.8 4 3 4" />
  </IconBase>
);

export const SettingsIcon = (props: SVGProps<SVGSVGElement>) => (
  <IconBase {...props}>
    <path d="M12 8.5A3.5 3.5 0 1 0 12 15.5A3.5 3.5 0 1 0 12 8.5z" />
    <path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.2a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.2a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.2a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9c0 .7.4 1.3 1 1.5h.2a2 2 0 1 1 0 4h-.2a1.6 1.6 0 0 0-1.5 1z" />
  </IconBase>
);
