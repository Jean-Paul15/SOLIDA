"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import type { ConfigurationGrilleApi, ProduitCreditApi } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";
import { LIBELLE_TRANCHE } from "@/lib/libelles";
import { peutModifierGrille } from "@/lib/roles";
import { ErreurService, leverSiEnErreur } from "@/lib/services/erreur-service";
import {
  probabiliteDepuisScore,
  scoreDepuisProbabilite,
  seuilEconomique,
  trancheDepuisProbabilite,
} from "@/lib/scorecard";

interface GrilleParametrageProps {
  scoresHistoriques: number[];
  configurationInitiale: ConfigurationGrilleApi;
  role: string | undefined;
  produits: ProduitCreditApi[];
}

export function GrilleParametrage({
  scoresHistoriques,
  configurationInitiale,
  role,
  produits,
}: GrilleParametrageProps) {
  const autoriseAModifier = peutModifierGrille(role);
  const [plafondsProduits, setPlafondsProduits] = useState<Record<string, number>>(
    configurationInitiale.progressif.plafonds_produits
  );
  const oddsReference = configurationInitiale.scorecard.odds_reference;
  const [marge, setMarge] = useState(configurationInitiale.grille.marge);
  const [lgd, setLgd] = useState(configurationInitiale.grille.lgd);
  const [multiplicateurAccord, setMultiplicateurAccord] = useState(
    configurationInitiale.grille.multiplicateur_accord
  );
  const [multiplicateurExamen, setMultiplicateurExamen] = useState(
    configurationInitiale.grille.multiplicateur_examen
  );
  const [pdo, setPdo] = useState(configurationInitiale.scorecard.pdo);
  const [scoreReference, setScoreReference] = useState(
    configurationInitiale.scorecard.score_reference
  );
  const [version, setVersion] = useState(configurationInitiale.version_grille);
  const [enregistrementEnCours, setEnregistrementEnCours] = useState(false);

  const parametresScorecard = { pdo, scoreReference, oddsReference };
  const parametresGrille = { marge, lgd, multiplicateurAccord, multiplicateurExamen };
  const seuil = seuilEconomique(parametresGrille);

  const repartition = useMemo(() => {
    const parametresScorecardLocaux = { pdo, scoreReference, oddsReference };
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
    oddsReference,
  ]);

  function compte(tranche: string): number {
    return repartition[tranche] ?? 0;
  }

  const total = scoresHistoriques.length;
  const tauxApprobation =
    total > 0 ? (compte("accord") + compte("accord_sous_condition")) / total : 0;

  async function enregistrer() {
    if (!autoriseAModifier) return;
    setEnregistrementEnCours(true);
    const [major, minor] = version.replace(/^v/, "").split(".").map(Number);
    const nouvelleVersion = `v${major}.${(minor ?? 0) + 1}`;
    try {
      const reponse = await fetch("/api/v1/parametrage/grille", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          version_grille: nouvelleVersion,
          grille: {
            marge,
            lgd,
            multiplicateur_accord: multiplicateurAccord,
            multiplicateur_vigilance: configurationInitiale.grille.multiplicateur_vigilance,
            multiplicateur_examen: multiplicateurExamen,
          },
          progressif: { ...configurationInitiale.progressif, plafonds_produits: plafondsProduits },
          scorecard: { pdo, score_reference: scoreReference, odds_reference: oddsReference },
        }),
      });
      await leverSiEnErreur(reponse);
      setVersion(nouvelleVersion);
      toast.success(`Grille ${nouvelleVersion} enregistrée`);
    } catch (e) {
      toast.error(e instanceof ErreurService ? e.message : "L'enregistrement a échoué.");
    } finally {
      setEnregistrementEnCours(false);
    }
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

        <Button
          onClick={enregistrer}
          disabled={enregistrementEnCours || !autoriseAModifier}
          className="self-start"
        >
          {enregistrementEnCours ? "Enregistrement…" : "Enregistrer la grille"}
        </Button>
        {!autoriseAModifier && (
          <p className="text-xs text-neutre-500">
            Lecture seule : la modification de la grille est réservée à la supervision. Les curseurs
            simulent l&rsquo;effet d&rsquo;un réglage sans l&rsquo;enregistrer.
          </p>
        )}
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

        <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">Plafonds par produit</span>
          {produits.map((p) => (
            <div key={p.produit_id} className="flex items-center gap-3 text-sm">
              <div className="flex flex-1 flex-col">
                <span className="text-neutre-950">{p.libelle}</span>
                <span className="text-xs text-neutre-500">
                  {p.duree_min_mois}–{p.duree_max_mois} mois · {(p.taux_annuel * 100).toFixed(0)}% ·{" "}
                  {p.type_garantie}
                </span>
              </div>
              {autoriseAModifier ? (
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    className="w-32"
                    value={plafondsProduits[p.produit_id] ?? p.montant_max}
                    onChange={(e) =>
                      setPlafondsProduits((precedent) => ({
                        ...precedent,
                        [p.produit_id]: Number(e.target.value),
                      }))
                    }
                    min={p.montant_min}
                  />
                  <span className="text-xs text-neutre-500">FCFA</span>
                </div>
              ) : (
                <span className="font-mono text-neutre-950">
                  {formaterMontant(plafondsProduits[p.produit_id] ?? p.montant_max)}
                </span>
              )}
            </div>
          ))}
        </div>

        <span className="text-xs text-neutre-500">Version active : {version}</span>
      </div>
    </div>
  );
}
