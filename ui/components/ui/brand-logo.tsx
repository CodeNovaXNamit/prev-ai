import { useId } from "react";

export function BrandLogo({ className = "" }: { className?: string }) {
  const id = useId().replace(/:/g, "");
  const shieldGradient = `privaiShield-${id}`;
  const shieldEdge = `privaiShieldEdge-${id}`;
  const coreGradient = `privaiCore-${id}`;
  const orbitGradient = `privaiOrbit-${id}`;
  const glowGradient = `privaiGlow-${id}`;

  return (
    <svg
      viewBox="0 0 96 96"
      aria-hidden="true"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id={shieldGradient} x1="18" y1="12" x2="72" y2="88" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFE3AE" />
          <stop offset="0.32" stopColor="#F4B45D" />
          <stop offset="0.7" stopColor="#B66824" />
          <stop offset="1" stopColor="#FFCF93" />
        </linearGradient>
        <linearGradient id={shieldEdge} x1="22" y1="18" x2="65" y2="82" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFF6E0" />
          <stop offset="0.45" stopColor="#E5A24A" />
          <stop offset="1" stopColor="#7E4016" />
        </linearGradient>
        <radialGradient id={coreGradient} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(49 42) rotate(90) scale(28)">
          <stop stopColor="#FFF4EC" />
          <stop offset="0.45" stopColor="#F7C5A3" />
          <stop offset="1" stopColor="#6E3314" />
        </radialGradient>
        <linearGradient id={orbitGradient} x1="6" y1="54" x2="90" y2="46" gradientUnits="userSpaceOnUse">
          <stop stopColor="#F4B962" />
          <stop offset="0.5" stopColor="#FFF6EE" />
          <stop offset="1" stopColor="#F0BA72" />
        </linearGradient>
        <radialGradient id={glowGradient} cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(49 41) rotate(90) scale(24)">
          <stop stopColor="#FFF8F0" stopOpacity="0.96" />
          <stop offset="0.55" stopColor="#FFD5B7" stopOpacity="0.54" />
          <stop offset="1" stopColor="#FFD5B7" stopOpacity="0" />
        </radialGradient>
      </defs>

      <ellipse cx="49" cy="41" rx="22" ry="20" fill={`url(#${glowGradient})`} />

      <path
        d="M48.5 10.5L78 24v23.6c0 18.5-11.8 31.4-29.5 38.4C30.8 79 19 66.1 19 47.6V24l29.5-13.5Z"
        fill={`url(#${shieldGradient})`}
      />
      <path
        d="M48.5 17.4L72.2 28v18.8c0 14.5-8.9 24.5-23.7 30.6C33.7 71.3 24.8 61.3 24.8 46.8V28l23.7-10.6Z"
        fill="#5A260F"
        stroke={`url(#${shieldEdge})`}
        strokeWidth="3"
      />

      <circle cx="48.5" cy="42.2" r="18.8" fill={`url(#${coreGradient})`} />

      <path
        d="M48.5 30.7C44 30.7 40.6 34 40.6 38.4v2.3h-1.7c-1.8 0-3.2 1.4-3.2 3.2v11.6c0 1.8 1.4 3.2 3.2 3.2h19.2c1.8 0 3.2-1.4 3.2-3.2V43.9c0-1.8-1.4-3.2-3.2-3.2h-1.7v-2.3c0-4.4-3.4-7.7-7.9-7.7Zm0 4.1c2.1 0 3.7 1.5 3.7 3.6v2.3h-7.4v-2.3c0-2.1 1.6-3.6 3.7-3.6Z"
        fill="#7E3416"
      />

      <path
        d="M8 56.3c11.4-5.7 24-7.9 41.6-7.9 16.1 0 28.1 1.7 38.4 6"
        stroke={`url(#${orbitGradient})`}
        strokeWidth="5.8"
        strokeLinecap="round"
      />
      <path
        d="M12 57.8c12-8.7 23.9-12.5 37.8-12.5 16.5 0 27.7 3.8 34.5 10.2"
        stroke="#FFF6EE"
        strokeOpacity="0.78"
        strokeWidth="2.1"
        strokeLinecap="round"
      />

      <circle cx="34.2" cy="29.2" r="1.9" fill="#FFF5E9" />
      <circle cx="62.9" cy="26.9" r="2.3" fill="#FFE6C9" />
      <circle cx="66.1" cy="41.5" r="1.8" fill="#FFF7F1" />
      <circle cx="33.8" cy="43.9" r="1.8" fill="#FFD8B9" />
    </svg>
  );
}
