import type { SVGProps } from 'react';

export const HarcLogo = (props: SVGProps<SVGSVGElement>) => (
  <svg {...props} viewBox="0 0 200 20">
    <defs>
      <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="2" result="coloredBlur" />
        <feMerge>
          <feMergeNode in="coloredBlur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <text
      x="0"
      y="15"
      fontFamily="Orbitron, sans-serif"
      fontSize="18"
      fontWeight="700"
      fill="hsl(var(--primary))"
      filter="url(#glow)"
      letterSpacing="2"
    >
      H.A.R.C.
    </text>
  </svg>
);
