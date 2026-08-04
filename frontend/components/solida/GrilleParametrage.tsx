"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { LIBELLE_TRANCHE } from "@/lib/libelles";
import {
  probabiliteDepuisScore,
  scoreDepuisProbabilite,
  seuilEconomique,
  trancheDepuisProbabilite,
} from "@/lib/scorecard";

const ODDS_REFERENCE = 50;

interface GrilleParametrageProps {
  scoresHistoriques: number[];
  versionInitiale: string;
}

export function GrilleParametrage({ scoresHistoriques, versionInitiale }: GrilleParametrageProps) {
  const [marge, setMarge] = useState(0.15);
  const [lgd, setLgd] = useState(0.75);
  const [multiplicateurAccord, setMultiplicateurAccord] = useState(0.6);
  const [multiplicateurExamen, setMultiplicateurExamen] = useState(1.6);
  const [pdo, setPdo] = useState(20);
  const [scoreReference, setScoreReference] = useState(600);
  const [version, setVersion] = useState(versionInitiale);
  const [enregistrementEnCours, setEnregistrementEnCours] = useState(false);

  const parametresScorecard = { pdo, scoreReference, oddsReference: ODDS_REFERENCE };
  const parametresGrille = { marge, lgd, multiplicateurAccord, multiplicateurExamen };
  const seuil = seuilEconomique(parametresGrille);

  const repartition = useMemo(() => {
    const parametresScorecardLocaux = { pdo, scoreReference, oddsReference: ODDS_REFERENCE };
    const parametresGrilleLocaux = { marge, lgd, multiplicateurAccord, multiplicateurExamen };
    const compte: Record<string, number> = {
      accord: 0,
      accord_sous_condition: 0,
      comite_de_credit: 0,
      refus: 0,
    };
    for (const score of scoresHistoriques) {
      const p = probabiliteDepuisScore(score, parametresScorecardLocaux);
      compte[trancheDepuisProbabilite(p, parametresGrilleLocaux)] += 1;
    }
    return compte;
  }, [
    scoresHistoriques,
    marge,
    lgd,
    multiplicateurAccord,
    multiplicateurExamen,
    pdo,
    scoreReference,
  ]);

  function compte(tranche: string): number {
    return repartition[tranche] ?? 0;
  }

  const total = scoresHistoriques.length;
  const tauxApprobation =
    total > 0 ? (compte("accord") + compte("accord_sous_condition")) / total : 0;

  async function enregistrer() {
    setEnregistrementEnCours(true);
    await new Promise((r) => setTimeout(r, 400));
    const [major, minor] = version.replace(/^v/, "").split(".").map(Number);
    const nouvelleVersion = `v${major}.${(minor ?? 0) + 1}`;
    setVersion(nouvelleVersion);
    setEnregistrementEnCours(false);
    toast.success(`Grille ${nouvelleVersion} enregistrée`);
  }

  return (
    <div className="grid grid-cols-12 gap-6">
      <div className="col-span-5 flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <div className="flex justify-between text-sm">
            <Label>Marge nette</Label>
            <span className="font-mono text-neutre-950">{(marge * 100).toFixed(0)}%</span>
          </div>
          <Slider
            value={[marge]}
            onValueChange={([v]) => setMarge(v)}
            min={0.05}
            max={0.3}
            step={0.01}
          />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex justify-between text-sm">
            <Label>Perte en cas de défaut (LGD)</Label>
            <span className="font-mono text-neutre-950">{(lgd * 100).toFixed(0)}%</span>
          </div>
          <Slider
            value={[lgd]}
            onValueChange={([v]) => setLgd(v)}
            min={0.4}
            max={0.9}
            step={0.01}
          />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex justify-between text-sm">
            <Label>Multiplicateur zone d&rsquo;accord</Label>
            <span className="font-mono text-neutre-950">× {multiplicateurAccord.toFixed(2)}</span>
          </div>
          <Slider
            value={[multiplicateurAccord]}
            onValueChange={([v]) => setMultiplicateurAccord(v)}
            min={0.3}
            max={0.95}
            step={0.05}
          />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex justify-between text-sm">
            <Label>Multiplicateur zone d&rsquo;examen</Label>
            <span className="font-mono text-neutre-950">× {multiplicateurExamen.toFixed(2)}</span>
          </div>
          <Slider
            value={[multiplicateurExamen]}
            onValueChange={([v]) => setMultiplicateurExamen(v)}
            min={1.2}
            max={2.5}
            step={0.05}
          />
        </div>

        <div className="flex gap-4">
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="pdo">PDO</Label>
            <Input
              id="pdo"
              type="number"
              value={pdo}
              onChange={(e) => setPdo(Number(e.target.value))}
            />
          </div>
          <div className="flex flex-1 flex-col gap-1.5">
            <Label htmlFor="score-ref">Score de référence</Label>
            <Input
              id="score-ref"
              type="number"
              value={scoreReference}
              onChange={(e) => setScoreReference(Number(e.target.value))}
            />
          </div>
        </div>

        <Button onClick={enregistrer} disabled={enregistrementEnCours} className="self-start">
          {enregistrementEnCours ? "Enregistrement…" : "Enregistrer la grille"}
        </Button>
      </div>

      <div className="col-span-7 flex flex-col gap-4">
        <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">Seuils résultants</span>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-neutre-500">Seuil économique</span>
              <div className="font-mono text-neutre-950">{(seuil * 100).toFixed(1)}%</div>
            </div>
            <div>
              <span className="text-neutre-500">Score accord</span>
              <div className="font-mono text-neutre-950">
                {scoreDepuisProbabilite(seuil * multiplicateurAccord, parametresScorecard)}
              </div>
            </div>
            <div>
              <span className="text-neutre-500">Score refus</span>
              <div className="font-mono text-neutre-950">
                {scoreDepuisProbabilite(seuil * multiplicateurExamen, parametresScorecard)}
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">
            Répartition sur l&rsquo;historique ({total} dossiers)
          </span>
          {(["accord", "accord_sous_condition", "comite_de_credit", "refus"] as const).map((t) => (
            <div key={t} className="flex items-center gap-3">
              <span className="w-40 text-sm text-neutre-700">{LIBELLE_TRANCHE[t]}</span>
              <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-neutre-200">
                <div
                  className="absolute h-full bg-solida-teal-600"
                  style={{ width: `${total > 0 ? (compte(t) / total) * 100 : 0}%` }}
                />
              </div>
              <span className="w-10 text-right font-mono text-sm text-neutre-950">{compte(t)}</span>
            </div>
          ))}
          <span className="text-xs text-neutre-500">
            Taux d&rsquo;approbation : {(tauxApprobation * 100).toFixed(0)}%
          </span>
        </div>

        <span className="text-xs text-neutre-500">Version active : {version}</span>
      </div>
    </div>
  );
}
