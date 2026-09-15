import type { GridParametersApi, ScorecardParametersApi, Tranche } from "@/lib/contracts";

export interface ParametresScorecard {
  pdo: number;
  scoreReference: number;
  oddsReference: number;
}

export interface ParametresGrille {
  marge: number;
  lgd: number;
  multiplicateurAccord: number;
}

export function parametresScorecardDepuisApi(api: ScorecardParametersApi): ParametresScorecard {
  return { pdo: api.pdo, scoreReference: api.score_reference, oddsReference: api.odds_reference };
}

export function parametresGrilleDepuisApi(api: GridParametersApi): ParametresGrille {
  return {
    marge: api.marge,
    lgd: api.lgd,
    multiplicateurAccord: api.multiplicateur_accord,
  };
}

/**
 * Inverse de la transformation PDO (voir backend `domain.rules.scorecard.calculer_score`) :
 * retrouve la probabilité implicite d'un score déjà calculé. Approximatif pour les décisions du
 * registre mock, dont le score n'a pas été produit par cette même transformation à l'origine —
 * suffisant pour l'aperçu en direct de E8, pas pour une vraie décision.
 */
export function probabiliteDepuisScore(score: number, parametres: ParametresScorecard): number {
  const facteur = parametres.pdo / Math.log(2);
  const decalage = parametres.scoreReference - facteur * Math.log(parametres.oddsReference);
  const logOdds = (score - decalage) / facteur;
  return 1 / (1 + Math.exp(logOdds));
}

export function scoreDepuisProbabilite(p: number, parametres: ParametresScorecard): number {
  const facteur = parametres.pdo / Math.log(2);
  const decalage = parametres.scoreReference - facteur * Math.log(parametres.oddsReference);
  const logOdds = Math.log((1 - p) / p);
  return Math.round(decalage + facteur * logOdds);
}

export function seuilEconomique(parametres: ParametresGrille): number {
  return parametres.marge / (parametres.marge + parametres.lgd);
}

/** 3 tranches vivantes : l'ancienne zone d'examen (comité de crédit) est fusionnée dans
 * refus depuis le passage à 3 tranches — la frontière est le seuil économique pur. */
export function trancheDepuisProbabilite(p: number, parametres: ParametresGrille): Tranche {
  const seuil = seuilEconomique(parametres);
  if (p < seuil * parametres.multiplicateurAccord) return "accord";
  if (p < seuil) return "accord_sous_condition";
  return "refus";
}
