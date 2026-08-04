import type { EntreeScoring, ResultatScoring } from "@/lib/contracts";
import { calculerScoring } from "@/lib/mocks/scoring";

export interface DecisionEnregistree {
  decisionId: string;
  societaireId: string;
  demande: EntreeScoring;
  resultat: ResultatScoring;
  horodatage: string;
  agentNom: string;
  /** `undefined` : l'agent n'a pas encore enregistré de décision finale (E4, bouton non câblé). */
  montantAccorde?: number;
}

declare global {
  var __solidaDecisionsMock: Map<string, DecisionEnregistree> | undefined;
  var __solidaDecisionsSeminees: boolean | undefined;
}

// globalThis (et non un simple module-level const) : Turbopack en mode dev peut charger ce module
// dans plus d'une instance selon le graphe (routeur HTTP vs page), ce qui viderait une Map locale
// entre l'ecriture et la lecture. globalThis est un singleton au niveau du processus Node, insensible
// a cette duplication.
const decisions = globalThis.__solidaDecisionsMock ?? new Map<string, DecisionEnregistree>();
globalThis.__solidaDecisionsMock = decisions;

export function enregistrerDecision(
  demande: EntreeScoring,
  resultatSansId: Omit<ResultatScoring, "decision_id">,
  agentNom: string
): ResultatScoring {
  const decisionId = crypto.randomUUID();
  const resultat: ResultatScoring = { ...resultatSansId, decision_id: decisionId };
  decisions.set(decisionId, {
    decisionId,
    societaireId: demande.societaire_id,
    demande,
    resultat,
    horodatage: new Date().toISOString(),
    agentNom,
  });
  return resultat;
}

export function lireDecision(decisionId: string): DecisionEnregistree | undefined {
  return decisions.get(decisionId);
}

export function listerDecisions(): DecisionEnregistree[] {
  return [...decisions.values()].sort((a, b) => b.horodatage.localeCompare(a.horodatage));
}

export interface DecisionRegistreVue extends DecisionEnregistree {
  societaireNom: string;
  agence: string;
}

/**
 * Historique de démonstration pour l'écran E7 (registre), sinon vide au démarrage. Un vrai
 * historique viendrait de `decision_scoring` (insertion seule) une fois le backend construit.
 */
function joursAvant(jours: number): string {
  const date = new Date();
  date.setDate(date.getDate() - jours);
  return date.toISOString();
}

const SEED: {
  entree: EntreeScoring;
  joursDans: number;
  agentNom: string;
  montantAccorde?: number;
}[] = [
  {
    entree: {
      societaire_id: "soc-adjo",
      produit_id: "prod-commerce",
      montant_demande: 400_000,
      duree_demandee_mois: 12,
      objet_credit: "fonds_roulement",
    },
    joursDans: 21,
    agentNom: "Agent Bè",
  },
  {
    entree: {
      societaire_id: "soc-kossi",
      produit_id: "prod-commerce",
      montant_demande: 500_000,
      duree_demandee_mois: 12,
      objet_credit: "fonds_roulement",
    },
    joursDans: 14,
    agentNom: "Agent Bè",
    montantAccorde: 350_000,
  },
  {
    entree: {
      societaire_id: "soc-akossiwa",
      produit_id: "prod-agricole",
      montant_demande: 600_000,
      duree_demandee_mois: 9,
      objet_credit: "intrants_agricoles",
    },
    joursDans: 9,
    agentNom: "Agent Agoè",
  },
  {
    entree: {
      societaire_id: "soc-mawuli",
      produit_id: "prod-agricole",
      montant_demande: 300_000,
      duree_demandee_mois: 6,
      objet_credit: "intrants_agricoles",
    },
    joursDans: 4,
    agentNom: "Agent Agoè",
    montantAccorde: 0,
  },
  {
    entree: {
      societaire_id: "soc-koffi",
      produit_id: "prod-equipement",
      montant_demande: 250_000,
      duree_demandee_mois: 18,
      objet_credit: "equipement",
    },
    joursDans: 1,
    agentNom: "Agent Bè",
  },
];

if (!globalThis.__solidaDecisionsSeminees) {
  globalThis.__solidaDecisionsSeminees = true;
  for (const { entree, joursDans, agentNom, montantAccorde } of SEED) {
    const decisionId = crypto.randomUUID();
    const resultatSansId = calculerScoring(entree);
    const resultat: ResultatScoring = { ...resultatSansId, decision_id: decisionId };
    decisions.set(decisionId, {
      decisionId,
      societaireId: entree.societaire_id,
      demande: entree,
      resultat,
      horodatage: joursAvant(joursDans),
      agentNom,
      montantAccorde: montantAccorde ?? resultat.montant_recommande,
    });
  }
}
