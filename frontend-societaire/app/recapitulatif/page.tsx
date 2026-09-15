"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { envoyerDemande } from "@/lib/services/portail";
import { mettreEnFile } from "@/lib/offline-queue";
import { ApiError } from "@/lib/services/error-service";

/**
 * C8 : plus d'écran de résultat côté sociétaire — le calcul complet (score, tranche,
 * conditions) tourne toujours et part intact vers l'agent (`resultat` stocké sur la
 * demande, visible dans son centre de notifications), mais le sociétaire ne voit
 * jamais ce raisonnement : dès l'envoi réussi, on passe directement à C9
 * ("transmis à votre agent"). Décision explicite du métier, déroge à la description
 * initiale de cet écran dans SOLIDA_Flux_Societaire.md ("pré-vérification en langage
 * clair"). Seul un échec RÉSEAU (`ApiError.kind === "network"`) part dans la file
 * hors-ligne ; une réponse d'erreur du serveur (session expirée, règle métier, panne)
 * est un message clair et actionnable, jamais confondu avec un problème de connexion.
 */
export default function RecapitulatifPage() {
  const router = useRouter();
  const {
    jetonSession,
    montant,
    objet,
    dureeMois,
    revenuMensuelDeclare,
    chargesMensuelles,
    resultat,
    enregistrerResultat,
  } = useDemande();
  const [etatReseau, setEtatReseau] = React.useState<
    "chargement" | "hors_ligne" | "erreur"
  >("chargement");
  const [messageErreur, setMessageErreur] = React.useState<string | null>(null);
  const [tentative, setTentative] = React.useState(0);

  React.useEffect(() => {
    if (!jetonSession || !montant || !objet || !dureeMois) {
      router.replace("/numero-compte");
      return;
    }
    if (resultat) {
      router.replace("/confirmation");
      return;
    }
    let annule = false;
    envoyerDemande(jetonSession, {
      montant,
      objet,
      duree_mois: dureeMois,
      ...(revenuMensuelDeclare !== null && { revenu_mensuel_declare: revenuMensuelDeclare }),
      ...(chargesMensuelles !== null && { charges_mensuelles: chargesMensuelles }),
    })
      .then((reponse) => {
        if (annule) return;
        enregistrerResultat(reponse);
        router.replace("/confirmation");
      })
      .catch(async (erreur: unknown) => {
        if (annule) return;
        if (erreur instanceof ApiError && erreur.kind === "network") {
          await mettreEnFile({
            jeton_session: jetonSession,
            montant,
            objet,
            duree_mois: dureeMois,
            revenu_mensuel_declare: revenuMensuelDeclare,
            charges_mensuelles: chargesMensuelles,
            mise_en_file_le: new Date().toISOString(),
          });
          if (!annule) setEtatReseau("hors_ligne");
          return;
        }
        setMessageErreur(
          erreur instanceof ApiError
            ? erreur.message
            : "Une erreur technique est survenue.",
        );
        setEtatReseau("erreur");
      });
    return () => {
      annule = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    jetonSession,
    montant,
    objet,
    dureeMois,
    revenuMensuelDeclare,
    chargesMensuelles,
    resultat,
    tentative,
  ]);

  if (etatReseau === "hors_ligne") {
    return (
      <EcranEtape
        etape={7}
        titre="Vérifions ensemble"
        pied={
          <Button onClick={() => router.push("/confirmation")}>Terminer</Button>
        }
      >
        <div className="rounded-lg border-2 border-alerte/30 bg-solida-gold-100 p-4 text-base">
          Votre connexion est instable. Pas d&apos;inquiétude : votre demande
          est conservée sur ce téléphone et partira dès que la connexion
          reviendra.
        </div>
      </EcranEtape>
    );
  }

  if (etatReseau === "erreur") {
    return (
      <EcranEtape
        etape={7}
        titre="Vérifions ensemble"
        pied={
          <Button
            onClick={() => {
              setEtatReseau("chargement");
              setTentative((t) => t + 1);
            }}
          >
            Réessayer
          </Button>
        }
      >
        <div className="rounded-lg border-2 border-decision-refus/30 bg-decision-refus-fond p-4 text-base">
          {messageErreur}
        </div>
      </EcranEtape>
    );
  }

  return (
    <EcranEtape etape={7} titre="Vérifions ensemble" pied={null}>
      <div className="animate-shimmer flex flex-col gap-3 pt-4">
        <div className="h-24 rounded-lg bg-neutre-100" />
        <div className="h-4 w-2/3 rounded bg-neutre-100" />
        <div className="h-4 w-1/2 rounded bg-neutre-100" />
      </div>
    </EcranEtape>
  );
}
