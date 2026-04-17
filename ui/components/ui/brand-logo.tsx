export function BrandLogo({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 96 96"
      aria-hidden="true"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="privaiCore" x1="20" y1="12" x2="74" y2="86" gradientUnits="userSpaceOnUse">
          <stop stopColor="#18F0FF" />
          <stop offset="1" stopColor="#274EAF" />
        </linearGradient>
        <linearGradient id="privaiFace" x1="18" y1="14" x2="48" y2="58" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFFFFF" />
          <stop offset="1" stopColor="#BFD3DE" />
        </linearGradient>
      </defs>

      <path
        d="M25 16c8.8-5.5 19.9-5.2 28 0l-6 18-10 9-8 20-13-4V33c0-7.2 3.5-13.4 9-17z"
        fill="url(#privaiFace)"
      />
      <path
        d="M50 17c12.5 0 24 8.1 28.6 20.4 2 5.2 2.5 11 1.6 17.4L72 84l-10-8-7 6-3-9-7 2 2-10-8-4 3-13-5-6 8-8 5-17z"
        fill="url(#privaiCore)"
      />
      <path d="M18 60l14 4 9-20 11-10 4-13" stroke="#111827" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M16 33v26" stroke="#111827" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M28 47l13 2" stroke="#111827" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M42 48l4 13" stroke="#111827" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M56 33l17 13" stroke="#7EE7FF" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M58 44l18 1" stroke="#7EE7FF" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M57 54l15-11" stroke="#7EE7FF" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M55 61l10-16" stroke="#7EE7FF" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M60 68l14-9" stroke="#5AAEFF" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M61 77l10-17" stroke="#4979E4" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M51 79l13-11" stroke="#355FC7" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M65 75l13 9" stroke="#274EAF" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M59 76l2 13" stroke="#274EAF" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M68 76l-7 13" stroke="#274EAF" strokeWidth="2.6" strokeLinecap="round" />
      <circle cx="56" cy="60" r="8.5" stroke="#0F172A" strokeWidth="3.2" />
      <circle cx="56" cy="60" r="2.8" fill="#0F172A" />
      <circle cx="69" cy="44" r="2.7" fill="#7EE7FF" />
      <circle cx="76" cy="59" r="2.5" fill="#59B6FF" />
      <circle cx="82" cy="34" r="4.1" fill="#18F0FF" />
      <circle cx="88" cy="47" r="2.3" fill="#18F0FF" />
      <circle cx="86" cy="60" r="3" fill="#355FC7" />
      <circle cx="40" cy="30" r="1.9" fill="#0F172A" />
      <circle cx="31" cy="49" r="1.8" fill="#0F172A" />
      <path d="M20 60l12 4-9 9H13z" fill="#0F172A" />
      <path d="M32 33l-8-14c5.8-4 13.7-5.1 21.3-2.8z" fill="#FFFFFF" />
    </svg>
  );
}
