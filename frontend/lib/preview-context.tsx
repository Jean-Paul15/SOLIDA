"use client";

import { createContext, useContext, useState } from "react";
import type { ScoringInput, ScoringResult } from "@/lib/contracts";

interface Preview {
  entree: ScoringInput;
  resultat: ScoringResult;
  societaireNom: string;
}

interface PreviewContextValue {
  previsualisation: Preview | null;
  definirPrevisualisation: (p: Preview | null) => void;
}

const PreviewContext = createContext<PreviewContextValue | null>(null);

export function PreviewProvider({ children }: { children: React.ReactNode }) {
  const [previsualisation, definirPrevisualisation] = useState<Preview | null>(null);
  return (
    <PreviewContext.Provider value={{ previsualisation, definirPrevisualisation }}>
      {children}
    </PreviewContext.Provider>
  );
}

export function usePreview(): PreviewContextValue {
  const contexte = useContext(PreviewContext);
  if (!contexte) {
    throw new Error("usePreview doit être utilisé sous PreviewProvider.");
  }
  return contexte;
}
