import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import type {
  ActiviteEconomique,
  ObjetCredit,
  ProduitCreditApi,
  ScoringInput,
} from "@/lib/contracts";
import {
  calculateMonthlyInstallment,
  calculateDebtRatio,
  TAUX_MENSUEL_DEMONSTRATION,
} from "@/lib/credit";
import { usePreview } from "@/lib/preview-context";
import { findProduit } from "@/lib/produits";
import { ApiError } from "@/lib/services/error-service";
import { previewScore } from "@/lib/services/scoring";
import { withMinDuration } from "@/lib/timing";

// Catalogue de durees "standard" (aligne sur simulateur/config.yaml, duree_mois_choix) : filtre
// ensuite aux bornes reelles du produit selectionne plutot qu'affiche une liste universelle qui
// laisserait choisir une duree hors du produit (meme incoherence que l'ancrage de la courbe
// d'epargne, voir SavingsMovements.tsx).
const DUREES_STANDARD = [3, 6, 9, 12, 18, 24];

interface UseNewRequestParams {
  societaireId: string;
  nomComplet: string;
  activite: ActiviteEconomique;
  produits: ProduitCreditApi[];
}

export function useNewRequest({
  societaireId,
  nomComplet,
  activite,
  produits,
}: UseNewRequestParams) {
  const router = useRouter();
  const { setPreview } = usePreview();
  const [sheetOpen, setSheetOpen] = useState(false);
  const [produitId, setProduitId] = useState(produits[0]?.produit_id ?? "");
  const [montant, setMontant] = useState(500000);
  const [duree, setDuree] = useState(() => Math.min(12, produits[0]?.duree_max_mois ?? 12));
  const [customDuration, setCustomDuration] = useState(false);
  const [objet, setObjet] = useState<ObjetCredit>("fonds_roulement");
  const [refreshOpen, setRefreshOpen] = useState(false);
  const [revenu, setRevenu] = useState(activite.revenu_mensuel_declare ?? 0);
  const [charges, setCharges] = useState(activite.charges_mensuelles ?? 0);
  const [inProgress, setInProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const produit = findProduit(produits, produitId);
  const dureesValides = produit
    ? DUREES_STANDARD.filter((d) => d >= produit.duree_min_mois && d <= produit.duree_max_mois)
    : DUREES_STANDARD;

  function choisirProduit(id: string): void {
    setProduitId(id);
    const nouveauProduit = findProduit(produits, id);
    if (
      nouveauProduit &&
      (duree < nouveauProduit.duree_min_mois || duree > nouveauProduit.duree_max_mois)
    ) {
      setCustomDuration(false);
      setDuree(nouveauProduit.duree_max_mois);
    }
  }

  function choisirDuree(v: string): void {
    if (v === "autre") {
      setCustomDuration(true);
    } else {
      setCustomDuration(false);
      setDuree(Number(v));
    }
  }

  const echeance = useMemo(
    () => calculateMonthlyInstallment(montant, duree, TAUX_MENSUEL_DEMONSTRATION),
    [montant, duree]
  );
  const tauxEndettement = useMemo(
    () => calculateDebtRatio(charges, revenu, echeance),
    [charges, revenu, echeance]
  );

  function annuler(): void {
    setError(null);
    setSheetOpen(false);
  }

  async function calculerLeScore() {
    setInProgress(true);
    setError(null);
    const input: ScoringInput = {
      societaire_id: societaireId,
      produit_id: produitId,
      montant_demande: montant,
      duree_demandee_mois: duree,
      objet_credit: objet,
      actualisation: refreshOpen
        ? { revenu_mensuel_declare: revenu, charges_mensuelles: charges }
        : undefined,
    };
    try {
      const result = await withMinDuration(previewScore(input));
      setPreview({ input, result, societaireNom: nomComplet });
      setSheetOpen(false);
      router.push("/scoring/preview");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Le calcul du score a échoué.");
    } finally {
      setInProgress(false);
    }
  }

  return {
    sheetOpen,
    setSheetOpen,
    produit,
    produitId,
    choisirProduit,
    dureesValides,
    montant,
    setMontant,
    duree,
    setDuree,
    customDuration,
    choisirDuree,
    objet,
    setObjet,
    refreshOpen,
    setRefreshOpen,
    revenu,
    setRevenu,
    charges,
    setCharges,
    echeance,
    tauxEndettement,
    inProgress,
    error,
    annuler,
    calculerLeScore,
  };
}
