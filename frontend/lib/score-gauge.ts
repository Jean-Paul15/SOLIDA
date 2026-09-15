import type { ConfigurationGrilleApi, Tranche } from "./contracts";
import {
  parametresGrilleDepuisApi,
  parametresScorecardDepuisApi,
  scoreDepuisProbabilite,
  seuilEconomique,
} from "./scorecard";

export const SCORE_MIN = 300;
export const SCORE_MAX = 850;

export const FOND_TRANCHE_JAUGE: Record<Tranche, string> = {
  refus: "bg-decision-refus",
  accord_sous_condition: "bg-decision-conditionnel",
  accord: "bg-decision-accord",
  // Historique uniquement : aucun nouveau segment de jauge ne produit plus cette tranche
  // (voir zoneBounds/gaugeSegments ci-dessous, 3 zones désormais).
  comite_de_credit: "bg-decision-comite",
};

/** Convertit un score en position (%) sur la jauge [SCORE_MIN, SCORE_MAX]. */
export function gaugePosition(score: number): number {
  return Math.min(100, Math.max(0, ((score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)) * 100));
}

/**
 * Bornes de score des zones de la grille active, dérivées des mêmes formules que
 * l'écran de paramétrage (`PolitiqueCredit`) — pour qu'un score affiché ici et les
 * seuils affichés là-bas désignent toujours le même repère, sans calcul mental.
 * Note : la grille peut avoir été recalibrée depuis qu'une décision déjà enregistrée
 * a été prise ; ces bornes reflètent la grille active aujourd'hui, pas nécessairement
 * celle utilisée au moment exact de la décision (le score lui, oui).
 */
/**
 * Bornes des 3 zones vivantes de la grille active. Depuis le passage à 3 tranches,
 * l'ancienne zone d'examen (comité de crédit) est fusionnée dans refus : la frontière
 * accord_sous_condition/refus est donc le seuil économique pur (multiplicateur implicite
 * de 1), sans `multiplicateur_examen`.
 */
export function zoneBounds(configuration: ConfigurationGrilleApi) {
  const { grille, scorecard } = configuration;
  const parametresScorecard = parametresScorecardDepuisApi(scorecard);
  const seuil = seuilEconomique(parametresGrilleDepuisApi(grille));
  return {
    scoreAccord: scoreDepuisProbabilite(seuil * grille.multiplicateur_accord, parametresScorecard),
    scoreVigilance: scoreDepuisProbabilite(seuil, parametresScorecard),
  };
}

export type Zones = ReturnType<typeof zoneBounds>;

/** Les 3 tranches vivantes de la jauge, bornes et légende de survol, score croissant. */
export function gaugeSegments(zones: Zones) {
  const arrondi = (n: number) => Math.round(n);
  return [
    {
      tranche: "refus" as const,
      gauche: 0,
      droite: gaugePosition(zones.scoreVigilance),
      legende: `score < ${arrondi(zones.scoreVigilance)}`,
    },
    {
      tranche: "accord_sous_condition" as const,
      gauche: gaugePosition(zones.scoreVigilance),
      droite: gaugePosition(zones.scoreAccord),
      legende: `score ${arrondi(zones.scoreVigilance)} à ${arrondi(zones.scoreAccord)}`,
    },
    {
      tranche: "accord" as const,
      gauche: gaugePosition(zones.scoreAccord),
      droite: 100,
      legende: `score ≥ ${arrondi(zones.scoreAccord)}`,
    },
  ];
}
