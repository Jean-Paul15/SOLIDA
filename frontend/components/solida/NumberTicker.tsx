"use client";

import { useEffect, useRef } from "react";
import { animate, useMotionValue, useReducedMotion } from "framer-motion";

export function NumberTicker({ valeur, className }: { valeur: number; className?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const compteur = useMotionValue(0);
  const reduitMotion = useReducedMotion();

  useEffect(() => {
    if (!ref.current) return;

    if (reduitMotion) {
      ref.current.textContent = String(valeur);
      return;
    }

    const controls = animate(compteur, valeur, {
      duration: 0.6,
      ease: "easeOut",
      onUpdate: (v) => {
        if (ref.current) ref.current.textContent = String(Math.round(v));
      },
    });

    return () => controls.stop();
  }, [valeur, compteur, reduitMotion]);

  return (
    <span ref={ref} className={className}>
      0
    </span>
  );
}
