"use client";

import { createContext, useContext, useState } from "react";
import type { EntreeScoring, ResultatScoring } from "@/lib/contracts";

interface Previsualisation {
  entree: EntreeScoring;
  resultat: ResultatScoring;
  societaireNom: string;
}

interface PrevisualisationContextValue {
  previsualisation: Previsualisation | null;
  definirPrevisualisation: (p: Previsualisation | null) => void;
}

const PrevisualisationContext = createContext<PrevisualisationContextValue | null>(null);

export function PrevisualisationProvider({ children }: { children: React.ReactNode }) {
  const [previsualisation, definirPrevisualisation] = useState<Previsualisation | null>(null);
  return (
    <PrevisualisationContext.Provider value={{ previsualisation, definirPrevisualisation }}>
      {children}
    </PrevisualisationContext.Provider>
  );
}

export function usePrevisualisation(): PrevisualisationContextValue {
  const contexte = useContext(PrevisualisationContext);
  if (!contexte) {
    throw new Error("usePrevisualisation doit être utilisé sous PrevisualisationProvider.");
  }
  return contexte;
}
