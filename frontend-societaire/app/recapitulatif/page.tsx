"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { envoyerDemande } from "@/lib/services/portail";
import { mettreEnFile } from "@/lib/offline-queue";
import { presentationResultat } from "@/lib/presentation-resultat";
import type { DemandePreVerificationReponse } from "@/lib/contracts";

/**
 * C8 : "la pré-vérification, en langage clair" est calculée automatiquement à
 * l'arrivée sur cet écran (un seul aller-retour réseau, celui qui enregistre aussi
 * la demande côté backend — pas de second appel "d'envoi" distinct, rien dans la
 * documentation ne justifie une étape brouillon/soumission séparée). Le bouton
 * "Envoyer à mon agent" confirme et passe à C9. Si l'appel échoue faute de réseau,
 * la demande part dans la file hors-ligne (section 6) et l'écran l'indique
 * clairement au lieu d'une erreur technique.
 */
export default function RecapitulatifPage() {
  const router = useRouter();
  const { jetonSession, montant, objet, dureeMois, resultat, enregistrerResultat } = useDemande();
  // "pret" se déduit directement de la présence du résultat en contexte : pas de
  // duplication d'état côté effet (évite le setState synchrone dans un effet que
  // signale react-hooks/set-state-in-effect).
  const [horsLigne, setHorsLigne] = React.useState(false);
  const etat = resultat ? "pret" : horsLigne ? "hors_ligne" : "chargement";

  React.useEffect(() => {
    if (!jetonSession || !montant || !objet || !dureeMois) {
      router.replace("/numero-compte");
      return;
    }
    if (resultat) return;
    let annule = false;
    envoyerDemande(jetonSession, { montant, objet, duree_mois: dureeMois })
      .then((reponse) => {
        if (!annule) enregistrerResultat(reponse);
      })
      .catch(async () => {
        if (annule) return;
        await mettreEnFile({
          jeton_session: jetonSession,
          montant,
          objet,
          duree_mois: dureeMois,
          mise_en_file_le: new Date().toISOString(),
        });
        if (!annule) setHorsLigne(true);
      });
    return () => {
      annule = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jetonSession, montant, objet, dureeMois, resultat]);

  if (etat === "chargement") {
    return (
      <EcranEtape etape={6} titre="Vérifions ensemble" pied={null}>
        <div className="animate-shimmer flex flex-col gap-3 pt-4">
          <div className="h-24 rounded-lg bg-neutre-100" />
          <div className="h-4 w-2/3 rounded bg-neutre-100" />
          <div className="h-4 w-1/2 rounded bg-neutre-100" />
        </div>
      </EcranEtape>
    );
  }

  if (etat === "hors_ligne") {
    return (
      <EcranEtape
        etape={6}
        titre="Vérifions ensemble"
        pied={<Button onClick={() => router.push("/confirmation")}>Terminer</Button>}
      >
        <div className="rounded-lg border-2 border-alerte/30 bg-solida-gold-100 p-5 text-base">
          Votre connexion est instable. Pas d&apos;inquiétude : votre demande est conservée sur ce
          téléphone et partira dès que la connexion reviendra.
        </div>
      </EcranEtape>
    );
  }

  return <ResultatPreVerification resultat={resultat!} />;
}

function ResultatPreVerification({ resultat }: { resultat: DemandePreVerificationReponse }) {
  const router = useRouter();
  const { montantRecommande, styleAmbiance } = presentationResultat(resultat);

  return (
    <EcranEtape
      etape={6}
      titre="Vérifions ensemble"
      pied={<Button onClick={() => router.push("/confirmation")}>Envoyer à mon agent</Button>}
    >
      <div className={`rounded-lg border-2 p-5 text-base ${styleAmbiance}`}>{resultat.message}</div>
      {montantRecommande ? (
        <p className="mt-4 text-center font-mono text-xl font-semibold text-solida-teal-800">
          {new Intl.NumberFormat("fr-FR").format(montantRecommande)} FCFA
        </p>
      ) : null}
      <p className="mt-6 text-sm text-muted-foreground">
        Votre agent examinera votre demande et vous recontactera. C&apos;est toujours lui qui
        décide.
      </p>
    </EcranEtape>
  );
}
