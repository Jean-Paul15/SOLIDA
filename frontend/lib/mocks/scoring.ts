import { societaires } from "@/lib/mocks/societaires";
import type { ContributionVariable, EntreeScoring, ResultatScoring } from "@/lib/contracts";

const POINTS_DE_BASE = 500;
const VERSION_MODELE = "mock-0.1.0";
const VERSION_GRILLE = "mock-0.1.0";

// Seuils provisoires, en attendant la grille réelle issue du modèle entraîné.
function trancheDepuisScore(score: number): ResultatScoring["tranche"] {
  if (score >= 700) return "accord";
  if (score >= 600) return "accord_sous_condition";
  if (score >= 500) return "comite_de_credit";
  return "refus";
}

export function calculerScoring(entree: EntreeScoring): ResultatScoring {
  const fiche = societaires[entree.societaire_id];
  if (!fiche) {
    throw new Error(`societaire introuvable: ${entree.societaire_id}`);
  }
  const { dossier, groupe } = fiche;
  const decomposition: ContributionVariable[] = [];

  const moisAvecDepot = dossier.epargne.nb_mois_avec_depot_12m;
  decomposition.push({
    code_variable: "nb_mois_avec_depot_12m",
    libelle: "Régularité de l'épargne",
    valeur: `${moisAvecDepot}/12 mois`,
    points: Math.round((moisAvecDepot - 6) * 5),
    sens: moisAvecDepot >= 6 ? "favorable" : "defavorable",
    famille: "epargne",
    explication: "Le sociétaire a déposé une épargne régulière au cours des 12 derniers mois.",
  });

  const anciennete = dossier.identite.anciennete_mois;
  decomposition.push({
    code_variable: "anciennete_societaire_mois",
    libelle: "Ancienneté de sociétariat",
    valeur: `${Math.round(anciennete / 12)} an(s)`,
    points: Math.round(anciennete / 6),
    sens: "favorable",
    famille: "profil",
    explication:
      "Une relation d'épargne ancienne réduit l'incertitude sur le comportement du sociétaire.",
  });

  const tendancePoints = { hausse: 15, stable: 0, erosion: -20 }[dossier.epargne.tendance_12m];
  decomposition.push({
    code_variable: "tendance_epargne_12m",
    libelle: "Tendance de l'épargne",
    valeur: dossier.epargne.tendance_12m,
    points: tendancePoints,
    sens: tendancePoints > 0 ? "favorable" : tendancePoints < 0 ? "defavorable" : "neutre",
    famille: "epargne",
    explication: "L'évolution du solde d'épargne sur 12 mois indique la trajectoire du sociétaire.",
  });

  const retardMax = dossier.historique_credit.reduce((m, c) => Math.max(m, c.max_jours_retard), 0);
  const pointsRetard = retardMax > 90 ? -40 : retardMax > 30 ? -25 : retardMax > 0 ? -15 : 10;
  decomposition.push({
    code_variable: "max_jours_retard_historique",
    libelle: "Historique de remboursement",
    valeur:
      dossier.historique_credit.length === 0
        ? "premier crédit"
        : `${retardMax} jour(s) de retard maximum`,
    points: pointsRetard,
    sens: pointsRetard >= 0 ? "favorable" : "defavorable",
    famille: "historique",
    explication:
      "Le retard maximal observé sur les crédits précédents est un signal direct de risque.",
  });

  const revenu = dossier.activite.revenu_mensuel_declare;
  let ratioEndettement: number | null = null;
  if (revenu && revenu > 0) {
    ratioEndettement = dossier.activite.charges_mensuelles
      ? dossier.activite.charges_mensuelles / revenu
      : 0;
    const pointsEndettement = ratioEndettement > 0.7 ? -18 : ratioEndettement > 0.5 ? -8 : 6;
    decomposition.push({
      code_variable: "ratio_endettement",
      libelle: "Taux d'endettement",
      valeur: ratioEndettement.toFixed(2),
      points: pointsEndettement,
      sens: pointsEndettement >= 0 ? "favorable" : "defavorable",
      famille: "activite",
      explication:
        "Le rapport entre charges déclarées et revenu déclaré mesure la capacité de remboursement.",
    });
  }

  const modeCalcul = dossier.identite.segment === "femme_gie" && groupe ? "enrichi" : "socle_seul";
  if (modeCalcul === "enrichi" && groupe && groupe.taux_remboursement_groupe !== null) {
    const taux = groupe.taux_remboursement_groupe;
    const pointsGroupe = taux >= 0.9 ? 12 : taux >= 0.6 ? -5 : -25;
    decomposition.push({
      code_variable: "taux_remboursement_groupe",
      libelle: "Réputation du groupe",
      valeur: `${Math.round(taux * 100)}% remb.`,
      points: pointsGroupe,
      sens: pointsGroupe >= 0 ? "favorable" : "defavorable",
      famille: "solidaire",
      explication:
        "Le taux de remboursement du groupe de caution, hors sociétaire évalué, influence la décision.",
    });
  }

  const montantMaxHistorique = dossier.historique_credit.reduce(
    (m, c) => Math.max(m, c.montant_octroye),
    0
  );
  const referenceMontant = montantMaxHistorique || (revenu ? revenu * 6 : entree.montant_demande);
  const ratioMontant = entree.montant_demande / referenceMontant;
  const pointsMontant = ratioMontant > 1.5 ? -14 : ratioMontant > 1 ? -4 : 4;
  decomposition.push({
    code_variable: "montant_sur_historique",
    libelle: "Montant / historique",
    valeur: `× ${ratioMontant.toFixed(1)}`,
    points: pointsMontant,
    sens: pointsMontant >= 0 ? "favorable" : "defavorable",
    famille: "demande",
    explication:
      "Le montant sollicité est comparé au plus haut montant déjà remboursé ou à la capacité déclarée.",
  });

  decomposition.sort((a, b) => Math.abs(b.points) - Math.abs(a.points));

  const score = Math.min(
    850,
    Math.max(300, POINTS_DE_BASE + decomposition.reduce((s, c) => s + c.points, 0))
  );
  const tranche = trancheDepuisScore(score);

  const avertissements: string[] = [];
  if (!revenu) {
    avertissements.push(
      "Revenu déclaré absent du dossier ; une valeur médiane du secteur a été imputée."
    );
  }

  const conditionsReexamen: string[] = [];
  if (tranche !== "accord") {
    if (moisAvecDepot < 9) {
      conditionsReexamen.push("Porter la régularité d'épargne à 9 mois sur 12.");
    }
    if (ratioEndettement !== null && ratioEndettement > 0.5) {
      conditionsReexamen.push("Réduire le taux d'endettement en dessous de 0,5.");
    }
    if (conditionsReexamen.length === 0) {
      conditionsReexamen.push("Maintenir la régularité de remboursement sur le cycle en cours.");
    }
  }

  const plafondProgressif = Math.round(entree.montant_demande * 1.2);

  return {
    score,
    tranche,
    montant_recommande:
      tranche === "refus" ? 0 : Math.min(entree.montant_demande, plafondProgressif),
    montant_demande: entree.montant_demande,
    mode_calcul: modeCalcul,
    motif_mode: modeCalcul === "socle_seul" ? "primo-emprunteur sans groupe historisé" : undefined,
    decomposition,
    points_de_base: POINTS_DE_BASE,
    plafond_progressif: plafondProgressif,
    trajectoire_progression: [1, 2, 3].map((cycle) => ({
      cycle,
      plafond_accessible: Math.round(plafondProgressif * (1 + cycle * 0.15)),
    })),
    conditions_reexamen: conditionsReexamen,
    version_modele: VERSION_MODELE,
    version_grille: VERSION_GRILLE,
    horodatage: new Date().toISOString(),
    avertissements,
  };
}

const resultatsCalcules = new Map<string, ResultatScoring>();

export function enregistrerResultat(societaireId: string, resultat: ResultatScoring) {
  resultatsCalcules.set(societaireId, resultat);
}

export function lireResultat(societaireId: string): ResultatScoring | undefined {
  return resultatsCalcules.get(societaireId);
}
