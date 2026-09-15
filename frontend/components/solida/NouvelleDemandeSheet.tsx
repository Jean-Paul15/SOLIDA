"use client";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { RefreshFields } from "@/components/solida/RefreshFields";
import { LoanFields } from "@/components/solida/LoanFields";
import { LoanSummary } from "@/components/solida/LoanSummary";
import { useNewRequest } from "@/components/solida/useNewRequest";
import type { ActiviteEconomique, ProduitCreditApi } from "@/lib/contracts";

interface NouvelleDemandeSheetProps {
  societaireId: string;
  nomComplet: string;
  activite: ActiviteEconomique;
  produits: ProduitCreditApi[];
  /** Absent pour un sociétaire hors groupe : `useNewRequest` ne le transmet alors jamais. */
  groupeId?: string;
}

export function NouvelleDemandeSheet({
  societaireId,
  nomComplet,
  activite,
  produits,
  groupeId,
}: NouvelleDemandeSheetProps) {
  const {
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
  } = useNewRequest({ societaireId, nomComplet, activite, produits, groupeId });

  return (
    <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
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
          <LoanFields
            produits={produits}
            produit={produit}
            produitId={produitId}
            onChangeProduit={choisirProduit}
            montant={montant}
            onChangeMontant={setMontant}
            duree={duree}
            onChangeDuree={setDuree}
            customDuration={customDuration}
            dureesValides={dureesValides}
            onChoisirDuree={choisirDuree}
          />

          <RefreshFields
            objet={objet}
            onChangeObjet={setObjet}
            objetImplicite={produit?.objet_implicite ?? null}
            refreshOpen={refreshOpen}
            onToggleActualisation={() => setRefreshOpen((v) => !v)}
            revenu={revenu}
            onChangeRevenu={setRevenu}
            charges={charges}
            onChangeCharges={setCharges}
          />

          <LoanSummary echeance={echeance} tauxEndettement={tauxEndettement} />
        </div>

        {error && (
          <div className="px-4">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </div>
        )}

        <SheetFooter className="flex-row justify-end gap-2">
          <Button variant="outline" onClick={annuler} loading={inProgress}>
            Annuler
          </Button>
          <Button onClick={calculerLeScore} loading={inProgress} disabled={montant <= 0}>
            {inProgress ? "Calcul…" : "Calculer le score"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}
