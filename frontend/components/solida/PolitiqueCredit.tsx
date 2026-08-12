"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
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

interface PolitiqueCreditProps {
  scoresHistoriques: number[];
  configurationInitiale: ConfigurationGrilleApi;
  role: string | undefined;
  produits: ProduitCreditApi[];
}

type Preregl = "prudent" | "equilibre" | "expansion";

export function PolitiqueCredit({
  scoresHistoriques,
  configurationInitiale,
  role,
  produits,
}: PolitiqueCreditProps) {
  const autoriseAModifier = peutModifierGrille(role);
  const [plafondsProduits, setPlafondsProduits] = useState<Record<string, number>>(
    configurationInitiale.progressif.plafonds_produits
  );
  // PDO, score de référence et rapport de référence ne sont plus édités depuis cet écran
  // (administration du modèle hors périmètre SOLIDA) : ils sont retransmis inchangés à
  // l'enregistrement.
  const {
    pdo,
    score_reference: scoreReference,
    odds_reference: oddsReference,
  } = configurationInitiale.scorecard;
  const [marge, setMarge] = useState(configurationInitiale.grille.marge);
  const [lgd, setLgd] = useState(configurationInitiale.grille.lgd);
  const [multiplicateurAccord, setMultiplicateurAccord] = useState(
    configurationInitiale.grille.multiplicateur_accord
  );
  const [multiplicateurExamen, setMultiplicateurExamen] = useState(
    configurationInitiale.grille.multiplicateur_examen
  );
  const [version, setVersion] = useState(configurationInitiale.version_grille);
  const [enregistrementEnCours, setEnregistrementEnCours] = useState(false);
  const [preregl, setPreregl] = useState<Preregl>("equilibre");

  const parametresScorecard = { pdo, scoreReference, oddsReference };
  const parametresGrille = { marge, lgd, multiplicateurAccord, multiplicateurExamen };
  const seuil = seuilEconomique(parametresGrille);

  const repartition = useMemo(() => {
    const compte: Record<string, number> = {
      accord: 0,
      accord_sous_condition: 0,
      comite_de_credit: 0,
      refus: 0,
    };
    for (const score of scoresHistoriques) {
      const p = probabiliteDepuisScore(score, parametresScorecard);
      compte[trancheDepuisProbabilite(p, parametresGrille)] += 1;
    }
    return compte;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scoresHistoriques, marge, lgd, multiplicateurAccord, multiplicateurExamen]);

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
      toast.success(`Politique de crédit ${nouvelleVersion} enregistrée`);
    } catch (e) {
      toast.error(e instanceof ErreurService ? e.message : "L'enregistrement a échoué.");
    } finally {
      setEnregistrementEnCours(false);
    }
  }

  return (
    <Tabs defaultValue="seuils" className="gap-6">
      <TabsList>
        <TabsTrigger value="seuils">Seuils</TabsTrigger>
        <TabsTrigger value="produits">Produits</TabsTrigger>
        <TabsTrigger value="simulation">Simulation d&rsquo;impact</TabsTrigger>
      </TabsList>

      <TabsContent value="seuils" className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <Rubrique
            titre="Préréglage de politique"
            description="Prudent et Expansion contrôlée seront activés après validation par le comité risque."
          />
          <div className="flex gap-2">
            {(
              [
                ["prudent", "Prudent"],
                ["equilibre", "Équilibré"],
                ["expansion", "Expansion contrôlée"],
              ] as const
            ).map(([valeur, libelle]) => {
              const desactive = valeur !== "equilibre";
              const bouton = (
                <Button
                  key={valeur}
                  type="button"
                  variant={preregl === valeur ? "default" : "outline"}
                  size="sm"
                  disabled={desactive}
                  onClick={() => setPreregl(valeur)}
                >
                  {libelle}
                </Button>
              );
              if (!desactive) return bouton;
              return (
                <Tooltip key={valeur}>
                  <TooltipTrigger asChild>
                    <span>{bouton}</span>
                  </TooltipTrigger>
                  <TooltipContent>
                    Bientôt disponible, après validation par le comité risque.
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-5 flex flex-col gap-5">
            <Rubrique
              titre="Matrice de coûts"
              description="Détermine le seuil économique, recalculé en direct à droite."
            />
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

            <Separator />
            <Rubrique
              titre="Largeur des zones de la grille"
              description="Écarte accord et refus du seuil économique central."
            />

            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-sm">
                <Label>Multiplicateur zone d&rsquo;accord</Label>
                <span className="font-mono text-neutre-950">
                  × {multiplicateurAccord.toFixed(2)}
                </span>
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
                <span className="font-mono text-neutre-950">
                  × {multiplicateurExamen.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[multiplicateurExamen]}
                onValueChange={([v]) => setMultiplicateurExamen(v)}
                min={1.2}
                max={2.5}
                step={0.05}
              />
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
                Lecture seule : la modification de la grille est réservée à la supervision. Les
                curseurs simulent l&rsquo;effet d&rsquo;un réglage sans l&rsquo;enregistrer.
              </p>
            )}
          </div>

          <div className="col-span-7 flex flex-col gap-4 rounded-lg bg-solida-teal-50 p-4">
            <Rubrique
              titre="Seuils résultants"
              description="Recalculé en direct à partir des réglages de gauche, rien n'est encore enregistré."
            />

            <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 bg-blanc p-4">
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

            <p className="mt-auto text-xs text-neutre-500">
              Score accord et score refus sont les mêmes seuils que ceux affichés sous forme de
              jauge colorée sur l&rsquo;écran de résultat d&rsquo;un score.
            </p>
          </div>
        </div>
      </TabsContent>

      <TabsContent value="produits" className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <Rubrique
            titre="Plafonds par produit"
            description="Indépendant des curseurs de l'onglet Seuils : plafond maximal appliqué quel que soit le score."
          />
          <span className="text-xs text-neutre-500">Version active : {version}</span>
        </div>
        <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
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
      </TabsContent>

      <TabsContent value="simulation" className="flex flex-col gap-3">
        <Rubrique
          titre="Simulation sur portefeuille de démonstration"
          description="Recalculée en direct à partir des réglages de l'onglet Seuils."
        />
        <div className="rounded-lg border border-alerte/40 bg-alerte/10 p-3 text-xs text-neutre-700">
          Résultats fournis à titre d&rsquo;exemple, non représentatifs du portefeuille réel.
        </div>
        <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
          <span className="text-xs font-medium text-neutre-500">
            Répartition sur {total} dossiers
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
      </TabsContent>
    </Tabs>
  );
}

function Rubrique({ titre, description }: { titre: string; description: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] font-medium tracking-wide text-neutre-500 uppercase">
        {titre}
      </span>
      <p className="text-xs text-neutre-500">{description}</p>
    </div>
  );
}
