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
  comite_de_credit: "bg-decision-comite",
  accord_sous_condition: "bg-decision-conditionnel",
  accord: "bg-decision-accord",
};

/** Convertit un score en position (%) sur la jauge [SCORE_MIN, SCORE_MAX]. */
export function positionSurJauge(score: number): number {
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
export function bornesZones(configuration: ConfigurationGrilleApi) {
  const { grille, scorecard } = configuration;
  const parametresScorecard = parametresScorecardDepuisApi(scorecard);
  const seuil = seuilEconomique(parametresGrilleDepuisApi(grille));
  return {
    scoreAccord: scoreDepuisProbabilite(seuil * grille.multiplicateur_accord, parametresScorecard),
    scoreVigilance: scoreDepuisProbabilite(seuil, parametresScorecard),
    scoreExamen: scoreDepuisProbabilite(seuil * grille.multiplicateur_examen, parametresScorecard),
  };
}

export type Zones = ReturnType<typeof bornesZones>;

/** Les 4 tranches de la jauge, bornes et légende de survol, dans l'ordre score croissant. */
export function segmentsJauge(zones: Zones) {
  const arrondi = (n: number) => Math.round(n);
  return [
    {
      tranche: "refus" as const,
      gauche: 0,
      droite: positionSurJauge(zones.scoreExamen),
      legende: `score < ${arrondi(zones.scoreExamen)}`,
    },
    {
      tranche: "comite_de_credit" as const,
      gauche: positionSurJauge(zones.scoreExamen),
      droite: positionSurJauge(zones.scoreVigilance),
      legende: `score ${arrondi(zones.scoreExamen)} à ${arrondi(zones.scoreVigilance)}`,
    },
    {
      tranche: "accord_sous_condition" as const,
      gauche: positionSurJauge(zones.scoreVigilance),
      droite: positionSurJauge(zones.scoreAccord),
      legende: `score ${arrondi(zones.scoreVigilance)} à ${arrondi(zones.scoreAccord)}`,
    },
    {
      tranche: "accord" as const,
      gauche: positionSurJauge(zones.scoreAccord),
      droite: 100,
      legende: `score ≥ ${arrondi(zones.scoreAccord)}`,
    },
  ];
}
