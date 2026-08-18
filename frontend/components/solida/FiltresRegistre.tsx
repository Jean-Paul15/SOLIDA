"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LIBELLE_TRANCHE } from "@/lib/libelles";
import { TOUS } from "./useFiltresRegistre";

const PERIODES = [
  { valeur: "7", libelle: "7 derniers jours" },
  { valeur: "30", libelle: "30 derniers jours" },
  { valeur: "90", libelle: "90 derniers jours" },
  { valeur: "tout", libelle: "Toute la période" },
];

interface FiltresRegistreProps {
  periode: string;
  setPeriode: (v: string) => void;
  agence: string;
  setAgence: (v: string) => void;
  agences: string[];
  agent: string;
  setAgent: (v: string) => void;
  agents: string[];
  tranche: string;
  setTranche: (v: string) => void;
}

export function FiltresRegistre({
  periode,
  setPeriode,
  agence,
  setAgence,
  agences,
  agent,
  setAgent,
  agents,
  tranche,
  setTranche,
}: FiltresRegistreProps) {
  return (
    <div className="flex flex-wrap gap-3">
      <Select value={periode} onValueChange={setPeriode}>
        <SelectTrigger className="w-[180px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {PERIODES.map((p) => (
            <SelectItem key={p.valeur} value={p.valeur}>
              {p.libelle}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={agence} onValueChange={setAgence}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Toutes les agences" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={TOUS}>Toutes les agences</SelectItem>
          {agences.map((a) => (
            <SelectItem key={a} value={a}>
              {a}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={agent} onValueChange={setAgent}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Tous les agents" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={TOUS}>Tous les agents</SelectItem>
          {agents.map((a) => (
            <SelectItem key={a} value={a}>
              {a}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={tranche} onValueChange={setTranche}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Toutes les tranches" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={TOUS}>Toutes les tranches</SelectItem>
          {Object.entries(LIBELLE_TRANCHE).map(([valeur, libelle]) => (
            <SelectItem key={valeur} value={valeur}>
              {libelle}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
