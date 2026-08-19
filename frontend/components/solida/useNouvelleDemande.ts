import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import type {
  ActiviteEconomique,
  ObjetCredit,
  ProduitCreditApi,
  ScoringInput,
} from "@/lib/contracts";
import {
  calculerEcheanceMensuelle,
  calculerTauxEndettement,
  TAUX_MENSUEL_DEMONSTRATION,
} from "@/lib/credit";
import { usePreview } from "@/lib/preview-context";
import { trouverProduit } from "@/lib/produits";
import { ApiError } from "@/lib/services/error-service";
import { previewScore } from "@/lib/services/scoring";

// Catalogue de durees "standard" (aligne sur simulateur/config.yaml, duree_mois_choix) : filtre
// ensuite aux bornes reelles du produit selectionne plutot qu'affiche une liste universelle qui
// laisserait choisir une duree hors du produit (meme incoherence que l'ancrage de la courbe
// d'epargne, voir MouvementsEpargne.tsx).
const DUREES_STANDARD = [3, 6, 9, 12, 18, 24];

interface UseNouvelleDemandeParams {
  societaireId: string;
  nomComplet: string;
  activite: ActiviteEconomique;
  produits: ProduitCreditApi[];
}

export function useNouvelleDemande({
  societaireId,
  nomComplet,
  activite,
  produits,
}: UseNouvelleDemandeParams) {
  const router = useRouter();
  const { definirPrevisualisation } = usePreview();
  const [sheetOuvert, setSheetOuvert] = useState(false);
  const [produitId, setProduitId] = useState(produits[0]?.produit_id ?? "");
  const [montant, setMontant] = useState(500000);
  const [duree, setDuree] = useState(() => Math.min(12, produits[0]?.duree_max_mois ?? 12));
  const [dureePersonnalisee, setDureePersonnalisee] = useState(false);
  const [objet, setObjet] = useState<ObjetCredit>("fonds_roulement");
  const [actualisationOuverte, setActualisationOuverte] = useState(false);
  const [revenu, setRevenu] = useState(activite.revenu_mensuel_declare ?? 0);
  const [charges, setCharges] = useState(activite.charges_mensuelles ?? 0);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const produit = trouverProduit(produits, produitId);
  const dureesValides = produit
    ? DUREES_STANDARD.filter((d) => d >= produit.duree_min_mois && d <= produit.duree_max_mois)
    : DUREES_STANDARD;

  function choisirProduit(id: string): void {
    setProduitId(id);
    const nouveauProduit = trouverProduit(produits, id);
    if (
      nouveauProduit &&
      (duree < nouveauProduit.duree_min_mois || duree > nouveauProduit.duree_max_mois)
    ) {
      setDureePersonnalisee(false);
      setDuree(nouveauProduit.duree_max_mois);
    }
  }

  function choisirDuree(v: string): void {
    if (v === "autre") {
      setDureePersonnalisee(true);
    } else {
      setDureePersonnalisee(false);
      setDuree(Number(v));
    }
  }

  const echeance = useMemo(
    () => calculerEcheanceMensuelle(montant, duree, TAUX_MENSUEL_DEMONSTRATION),
    [montant, duree]
  );
  const tauxEndettement = useMemo(
    () => calculerTauxEndettement(charges, revenu, echeance),
    [charges, revenu, echeance]
  );

  function annuler(): void {
    setErreur(null);
    setSheetOuvert(false);
  }

  async function calculerLeScore() {
    setEnCours(true);
    setErreur(null);
    const entree: ScoringInput = {
      societaire_id: societaireId,
      produit_id: produitId,
      montant_demande: montant,
      duree_demandee_mois: duree,
      objet_credit: objet,
      actualisation: actualisationOuverte
        ? { revenu_mensuel_declare: revenu, charges_mensuelles: charges }
        : undefined,
    };
    try {
      const resultat = await previewScore(entree);
      definirPrevisualisation({ entree, resultat, societaireNom: nomComplet });
      setSheetOuvert(false);
      router.push("/scoring/previsualisation");
    } catch (e) {
      setErreur(e instanceof ApiError ? e.message : "Le calcul du score a échoué.");
    } finally {
      setEnCours(false);
    }
  }

  return {
    sheetOuvert,
    setSheetOuvert,
    produit,
    produitId,
    choisirProduit,
    dureesValides,
    montant,
    setMontant,
    duree,
    setDuree,
    dureePersonnalisee,
    choisirDuree,
    objet,
    setObjet,
    actualisationOuverte,
    setActualisationOuverte,
    revenu,
    setRevenu,
    charges,
    setCharges,
    echeance,
    tauxEndettement,
    enCours,
    erreur,
    annuler,
    calculerLeScore,
  };
}
