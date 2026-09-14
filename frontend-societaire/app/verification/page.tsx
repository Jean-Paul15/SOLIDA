"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { NumericInput } from "@/components/ui/numeric-input";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { verifierCompte } from "@/lib/services/portail";
import { afficherErreur } from "@/lib/services/error-service";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

export default function VerificationPage() {
  const router = useRouter();
  const { numeroCompte, enregistrerVerification } = useDemande();
  const [montant, setMontant] = React.useState("");
  const [envoiEnCours, setEnvoiEnCours] = React.useState(false);
  const pret = useEtapeProtegee(numeroCompte);

  const valide = montant.length > 0;

  async function valider() {
    if (!valide || !numeroCompte) return;
    setEnvoiEnCours(true);
    try {
      const reponse = await verifierCompte({
        numero_compte: numeroCompte,
        montant_dernier_depot: Number(montant),
      });
      enregistrerVerification(reponse.jeton_session, reponse.prenom);
      router.push("/bonjour");
    } catch (erreur) {
      afficherErreur(
        erreur,
        "Numéro de compte ou montant incorrect. Vérifiez et réessayez, ou rendez-vous à votre agence.",
      );
      setMontant("");
    } finally {
      setEnvoiEnCours(false);
    }
  }

  if (!pret) return null;

  return (
    <EcranEtape
      etape={2}
      titre="Pour vérifier que c'est bien vous"
      sousTitre="Quel est le montant de votre dernier dépôt ?"
      pied={
        <Button onClick={valider} disabled={!valide} loading={envoiEnCours}>
          Valider
        </Button>
      }
    >
      <Label htmlFor="montant-depot">Montant en FCFA</Label>
      <NumericInput
        id="montant-depot"
        value={montant}
        onChange={(event) => setMontant(event.target.value.replace(/\D/g, ""))}
        placeholder="0"
        autoFocus
      />
    </EcranEtape>
  );
}
