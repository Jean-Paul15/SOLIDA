"use client";

import { motion, useReducedMotion } from "framer-motion";

const CHEMINS = [
  { d: "M -100 400 C 200 250, 400 550, 700 380 S 1100 200, 1400 350", largeur: 2.5, opacite: 0.22 },
  { d: "M -100 550 C 250 420, 450 680, 750 500 S 1150 380, 1400 520", largeur: 1.5, opacite: 0.14 },
  { d: "M -100 250 C 200 380, 500 150, 800 300 S 1150 450, 1400 220", largeur: 1.5, opacite: 0.14 },
  { d: "M -100 650 C 300 560, 550 750, 850 620 S 1200 520, 1400 640", largeur: 1, opacite: 0.09 },
];

const PARTICULES = [
  { x: 180, decalage: 0 },
  { x: 460, decalage: 3 },
  { x: 760, decalage: 6 },
  { x: 1020, decalage: 1.5 },
  { x: 1260, decalage: 4.5 },
];

export function FluxEpargneBeam() {
  const reduitMotion = useReducedMotion();

  return (
    <svg
      aria-hidden
      viewBox="0 0 1300 800"
      preserveAspectRatio="xMidYMid slice"
      className="pointer-events-none absolute inset-0 h-full w-full"
    >
      <defs>
        <radialGradient id="lueurCentrale" cx="50%" cy="45%" r="60%">
          <stop offset="0%" stopColor="var(--color-solida-teal-600)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--color-solida-teal-600)" stopOpacity="0" />
        </radialGradient>
      </defs>

      <rect width="1300" height="800" fill="url(#lueurCentrale)" />

      {CHEMINS.map((chemin, i) => (
        <motion.path
          key={chemin.d}
          d={chemin.d}
          fill="none"
          stroke="var(--color-solida-gold-500)"
          strokeWidth={chemin.largeur}
          strokeLinecap="round"
          strokeDasharray="10 18"
          strokeOpacity={chemin.opacite}
          initial={{ strokeDashoffset: 0 }}
          animate={reduitMotion ? undefined : { strokeDashoffset: -280 }}
          transition={{ duration: 14 + i * 3, repeat: Infinity, ease: "linear" }}
        />
      ))}

      {!reduitMotion &&
        PARTICULES.map((p) => (
          <motion.circle
            key={p.x}
            cx={p.x}
            r={3}
            fill="var(--color-solida-gold-100)"
            initial={{ cy: 780, opacity: 0 }}
            animate={{ cy: -20, opacity: [0, 0.6, 0.6, 0] }}
            transition={{
              duration: 9,
              delay: p.decalage,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
    </svg>
  );
}
