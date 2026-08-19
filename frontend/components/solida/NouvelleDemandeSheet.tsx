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
import { ChampsActualisation } from "@/components/solida/ChampsActualisation";
import { ChampsPret } from "@/components/solida/ChampsPret";
import { ResumePret } from "@/components/solida/ResumePret";
import { useNouvelleDemande } from "@/components/solida/useNouvelleDemande";
import type { ActiviteEconomique, ProduitCreditApi } from "@/lib/contracts";

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
  const {
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
  } = useNouvelleDemande({ societaireId, nomComplet, activite, produits });

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
          <ChampsPret
            produits={produits}
            produit={produit}
            produitId={produitId}
            onChangeProduit={choisirProduit}
            montant={montant}
            onChangeMontant={setMontant}
            duree={duree}
            onChangeDuree={setDuree}
            dureePersonnalisee={dureePersonnalisee}
            dureesValides={dureesValides}
            onChoisirDuree={choisirDuree}
          />

          <ChampsActualisation
            objet={objet}
            onChangeObjet={setObjet}
            actualisationOuverte={actualisationOuverte}
            onToggleActualisation={() => setActualisationOuverte((v) => !v)}
            revenu={revenu}
            onChangeRevenu={setRevenu}
            charges={charges}
            onChangeCharges={setCharges}
          />

          <ResumePret echeance={echeance} tauxEndettement={tauxEndettement} />
        </div>

        {erreur && (
          <div className="px-4">
            <Alert variant="destructive">
              <AlertDescription>{erreur}</AlertDescription>
            </Alert>
          </div>
        )}

        <SheetFooter className="flex-row justify-end gap-2">
          <Button variant="outline" onClick={annuler} disabled={enCours}>
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
