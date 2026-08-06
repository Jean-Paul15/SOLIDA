"use client";

import { ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import type {
  ActiviteEconomique,
  EntreeScoring,
  ObjetCredit,
  ProduitCreditApi,
} from "@/lib/contracts";
import {
  calculerEcheanceMensuelle,
  calculerTauxEndettement,
  TAUX_MENSUEL_DEMONSTRATION,
} from "@/lib/credit";
import { formaterMontant } from "@/lib/format";
import { LIBELLE_OBJET_CREDIT } from "@/lib/libelles";
import { usePrevisualisation } from "@/lib/previsualisation-context";
import { trouverProduit } from "@/lib/produits";
import { ErreurService } from "@/lib/services/erreur-service";
import { previsualiserScore } from "@/lib/services/scoring";

// Catalogue de durees "standard" (aligne sur simulateur/config.yaml, duree_mois_choix) : filtre
// ensuite aux bornes reelles du produit selectionne plutot qu'affiche une liste universelle qui
// laisserait choisir une duree hors du produit (meme incoherence que l'ancrage de la courbe
// d'epargne, voir MouvementsEpargne.tsx).
const DUREES_STANDARD = [3, 6, 9, 12, 18, 24];

const OBJETS = Object.entries(LIBELLE_OBJET_CREDIT).map(([valeur, libelle]) => ({
  valeur: valeur as ObjetCredit,
  libelle,
}));

interface NouvelleDemandeSheetProps {
  societaireId: string;
  nomComplet: string;
  activite: ActiviteEconomique;
  produits: ProduitCreditApi[];
}

export function NouvelleDemandeSheet({
  societaireId,
  nomComplet,
  activite,
  produits,
}: NouvelleDemandeSheetProps) {
  const router = useRouter();
  const { definirPrevisualisation } = usePrevisualisation();
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

  const echeance = useMemo(
    () => calculerEcheanceMensuelle(montant, duree, TAUX_MENSUEL_DEMONSTRATION),
    [montant, duree]
  );
  const tauxEndettement = useMemo(
    () => calculerTauxEndettement(charges, revenu, echeance),
    [charges, revenu, echeance]
  );

  async function calculerLeScore() {
    setEnCours(true);
    setErreur(null);
    const entree: EntreeScoring = {
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
      const resultat = await previsualiserScore(entree);
      definirPrevisualisation({ entree, resultat, societaireNom: nomComplet });
      setSheetOuvert(false);
      router.push("/scoring/previsualisation");
    } catch (e) {
      setErreur(e instanceof ErreurService ? e.message : "Le calcul du score a échoué.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <Sheet open={sheetOuvert} onOpenChange={setSheetOuvert}>
      <SheetTrigger asChild>
        <Button>Nouvelle demande</Button>
      </SheetTrigger>
      <SheetContent className="w-[460px] gap-6 sm:max-w-[460px]">
        <SheetHeader>
          <SheetTitle>Nouvelle demande : {nomComplet}</SheetTitle>
          <SheetDescription className="sr-only">
            Saisie de la demande de crédit du jour
          </SheetDescription>
        </SheetHeader>

        <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto px-4">
          <div className="flex flex-col gap-1.5">
            <Label>Produit de crédit</Label>
            <Select value={produitId} onValueChange={choisirProduit}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {produits.map((p) => (
                  <SelectItem key={p.produit_id} value={p.produit_id}>
                    {p.libelle}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="montant">Montant sollicité</Label>
            <div className="flex items-center gap-2">
              <Input
                id="montant"
                type="number"
                value={montant}
                onChange={(e) => setMontant(Number(e.target.value))}
                min={0}
                max={produit?.montant_max}
              />
              <span className="text-sm text-neutre-500">FCFA</span>
            </div>
            {produit && (
              <span className="text-xs text-neutre-500">
                Plafond du produit : {formaterMontant(produit.montant_max)}
              </span>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label>Durée</Label>
            <Select
              value={dureePersonnalisee ? "autre" : String(duree)}
              onValueChange={(v) => {
                if (v === "autre") {
                  setDureePersonnalisee(true);
                } else {
                  setDureePersonnalisee(false);
                  setDuree(Number(v));
                }
              }}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {dureesValides.map((d) => (
                  <SelectItem key={d} value={String(d)}>
                    {d} mois
                  </SelectItem>
                ))}
                <SelectItem value="autre">Autre (préciser)</SelectItem>
              </SelectContent>
            </Select>
            {produit && (
              <span className="text-xs text-neutre-500">
                Durée du produit : {produit.duree_min_mois}–{produit.duree_max_mois} mois
              </span>
            )}
            {dureePersonnalisee && (
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  min={produit?.duree_min_mois ?? 1}
                  max={produit?.duree_max_mois ?? 60}
                  value={duree}
                  onChange={(e) => setDuree(Number(e.target.value))}
                  autoFocus
                />
                <span className="text-sm text-neutre-500">mois</span>
              </div>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <Label>Objet du crédit</Label>
            <Select value={objet} onValueChange={(v) => setObjet(v as ObjetCredit)}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {OBJETS.map((o) => (
                  <SelectItem key={o.valeur} value={o.valeur}>
                    {o.libelle}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <button
            type="button"
            onClick={() => setActualisationOuverte((v) => !v)}
            className="flex cursor-pointer items-center gap-1 text-left text-sm text-neutre-700"
          >
            <ChevronRight
              className={
                actualisationOuverte
                  ? "size-4 rotate-90 transition-transform"
                  : "size-4 transition-transform"
              }
            />
            Actualiser la situation économique
          </button>

          {actualisationOuverte && (
            <div className="flex flex-col gap-3 border-l border-neutre-200 pl-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="revenu">Revenu mensuel</Label>
                <Input
                  id="revenu"
                  type="number"
                  value={revenu}
                  onChange={(e) => setRevenu(Number(e.target.value))}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="charges">Charges mensuelles</Label>
                <Input
                  id="charges"
                  type="number"
                  value={charges}
                  onChange={(e) => setCharges(Number(e.target.value))}
                />
              </div>
            </div>
          )}

          <div className="flex flex-col gap-1 border-t border-neutre-200 pt-4">
            <div className="flex justify-between text-sm">
              <span className="text-neutre-500">Échéance mensuelle estimée</span>
              <span className="font-mono text-neutre-950">{formaterMontant(echeance)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-neutre-500">Taux d&rsquo;endettement résultant</span>
              <span
                className={
                  tauxEndettement > 0.7 ? "font-mono text-alerte" : "font-mono text-neutre-950"
                }
              >
                {tauxEndettement.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {erreur && (
          <div className="px-4">
            <Alert variant="destructive">
              <AlertDescription>{erreur}</AlertDescription>
            </Alert>
          </div>
        )}

        <SheetFooter className="flex-row justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => {
              setErreur(null);
              setSheetOuvert(false);
            }}
            disabled={enCours}
          >
            Annuler
          </Button>
          <Button onClick={calculerLeScore} disabled={enCours || montant <= 0}>
            {enCours ? "Calcul…" : "Calculer le score"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
