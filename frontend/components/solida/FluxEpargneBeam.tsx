"use client";

import { motion, useReducedMotion } from "framer-motion";

const CHEMINS = [
  "M -100 400 C 200 250, 400 550, 700 380 S 1100 200, 1400 350",
  "M -100 550 C 250 420, 450 680, 750 500 S 1150 380, 1400 520",
  "M -100 250 C 200 380, 500 150, 800 300 S 1150 450, 1400 220",
];

export function FluxEpargneBeam() {
  const reduitMotion = useReducedMotion();

  return (
    <svg
      aria-hidden
      viewBox="0 0 1300 800"
      preserveAspectRatio="xMidYMid slice"
      className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.08]"
    >
      {CHEMINS.map((d, i) => (
        <motion.path
          key={d}
          d={d}
          fill="none"
          stroke="var(--color-solida-gold-500)"
          strokeWidth={2}
          strokeLinecap="round"
          strokeDasharray="10 18"
          initial={{ strokeDashoffset: 0 }}
          animate={reduitMotion ? undefined : { strokeDashoffset: -280 }}
          transition={{ duration: 14 + i * 3, repeat: Infinity, ease: "linear" }}
        />
      ))}
    </svg>
  );
}
