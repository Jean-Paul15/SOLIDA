"use client";

import { createContext, useContext, useState } from "react";
import type { ScoringInput, ScoringResult } from "@/lib/contracts";

interface Preview {
  input: ScoringInput;
  result: ScoringResult;
  societaireNom: string;
}

interface PreviewContextValue {
  preview: Preview | null;
  setPreview: (p: Preview | null) => void;
}

const PreviewContext = createContext<PreviewContextValue | null>(null);

export function PreviewProvider({ children }: { children: React.ReactNode }) {
  const [preview, setPreview] = useState<Preview | null>(null);
  return (
    <PreviewContext.Provider value={{ preview, setPreview }}>{children}</PreviewContext.Provider>
  );
}

export function usePreview(): PreviewContextValue {
  const context = useContext(PreviewContext);
  if (!context) {
    throw new Error("usePreview doit être utilisé sous PreviewProvider.");
  }
  return context;
}
