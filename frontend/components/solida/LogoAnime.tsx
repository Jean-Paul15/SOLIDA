"use client";

import { motion, useReducedMotion } from "framer-motion";
import Image from "next/image";

/**
 * Meme logique que SavingsFlowBeam.tsx en arriere-plan : une entree douce, puis un
 * flottement continu tres subtil, jamais une animation qui distrait de la connexion.
 */
export function LogoAnime() {
  const reduitMotion = useReducedMotion();

  if (reduitMotion) {
    return (
      <Image
        src="/solida-logo.png"
        alt="SOLIDA"
        width={220}
        height={168}
        priority
        className="relative"
      />
    );
  }

  return (
    <motion.div
      className="relative"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 4, delay: 0.8, repeat: Infinity, ease: "easeInOut" }}
      >
        <Image
          src="/solida-logo.png"
          alt="SOLIDA"
          width={220}
          height={168}
          priority
          className="relative"
        />
      </motion.div>
    </motion.div>
  );
}
