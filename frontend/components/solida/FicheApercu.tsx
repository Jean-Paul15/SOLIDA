import Image from "next/image";
import type { ContributionVariable, FicheJustification } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";
import { COULEUR_TRANCHE, LIBELLE_OBJET_CREDIT, LIBELLE_TRANCHE } from "@/lib/libelles";
import { trouverProduit } from "@/lib/produits";

interface FicheApercuProps {
  fiche: FicheJustification;
  versionApplication: string;
}

function BlocFacteurs({ titre, facteurs }: { titre: string; facteurs: ContributionVariable[] }) {
  return (
    <div className="flex flex-1 flex-col gap-2">
      <span className="text-[11px] font-medium tracking-wide text-neutre-500 uppercase">
        {titre}
      </span>
      <ul className="flex flex-col gap-2">
        {facteurs.map((f) => (
          <li key={f.code_variable} className="text-[11px] text-neutre-700">
            <span className="font-medium text-neutre-950">
              {f.libelle} — {f.valeur}
            </span>
            <br />
            {f.explication}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function FicheApercu({ fiche, versionApplication }: FicheApercuProps) {
  const { resultat, demande } = fiche;
  const couleurs = COULEUR_TRANCHE[resultat.tranche];
  const produit = trouverProduit(demande.produit_id);

  return (
    <div
      id="fiche-apercu"
      className="mx-auto flex aspect-[210/297] w-full max-w-[800px] flex-col gap-4 border border-neutre-200 bg-blanc p-[6%] text-neutre-950 shadow-1"
    >
      <div className="flex items-center justify-between border-b border-neutre-200 pb-3">
        <div>
          <h1 className="font-serif-title text-base font-semibold">
            Fiche de justification de décision de crédit
          </h1>
          <span className="text-[11px] text-neutre-500">
            Référence {fiche.fiche_id} · édité le{" "}
            {new Date(fiche.date_edition).toLocaleString("fr-FR", {
              dateStyle: "long",
              timeStyle: "short",
            })}
          </span>
        </div>
        <Image src="/solida-logo.png" alt="SOLIDA" width={28} height={21} />
      </div>

      <div className="grid grid-cols-2 gap-4 text-[11px]">
        <div className="flex flex-col gap-1">
          <span className="font-medium text-neutre-500 uppercase">Sociétaire</span>
          <span>{fiche.societaire_nom}</span>
          <span>N° {fiche.numero_membre}</span>
          <span>{fiche.agence}</span>
          <span>Agent instructeur : {fiche.agent_nom}</span>
        </div>
        <div className="flex flex-col gap-1">
          <span className="font-medium text-neutre-500 uppercase">Demande</span>
          <span>{produit.nom}</span>
          <span>{formaterMontant(demande.montant_demande)} sollicités</span>
          <span>{demande.duree_demandee_mois} mois</span>
          <span>{LIBELLE_OBJET_CREDIT[demande.objet_credit]}</span>
        </div>
      </div>

      <div
        className={`flex flex-col gap-1 rounded border-l-3 ${couleurs.bordure} ${couleurs.fond} p-3`}
      >
        <span className="text-[11px] text-neutre-500">Résultat</span>
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-xl">{resultat.score}</span>
          <span className={`text-sm font-semibold ${couleurs.texte}`}>
            {LIBELLE_TRANCHE[resultat.tranche]}
          </span>
        </div>
        {resultat.tranche !== "refus" && (
          <span className="text-[11px]">
            Montant recommandé : {formaterMontant(resultat.montant_recommande)}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-[11px] font-medium text-neutre-500 uppercase">
          Trajectoire de progression
        </span>
        <div className="flex gap-4 text-[11px]">
          {resultat.trajectoire_progression.map((p) => (
            <span key={p.cycle}>
              Cycle +{p.cycle} : {formaterMontant(p.plafond_accessible)}
            </span>
          ))}
        </div>
      </div>

      <div className="flex gap-6 border-t border-neutre-200 pt-3">
        <BlocFacteurs titre="Éléments favorables" facteurs={fiche.facteurs_favorables} />
        <BlocFacteurs titre="Points de vigilance" facteurs={fiche.facteurs_defavorables} />
      </div>

      {fiche.conditions_reexamen.length > 0 && resultat.tranche !== "accord" && (
        <div className="flex flex-col gap-1 border-t border-neutre-200 pt-3">
          <span className="text-[11px] font-medium text-neutre-500 uppercase">
            Conditions de réexamen
          </span>
          <ul className="list-disc pl-4 text-[11px] text-neutre-700">
            {fiche.conditions_reexamen.slice(0, 3).map((c) => (
              <li key={c}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-auto flex items-end justify-between border-t border-neutre-200 pt-2 text-[9px] text-neutre-500">
        <span className="max-w-[75%]">{fiche.mention_legale}</span>
        <div className="flex flex-col items-end">
          <span>
            Modèle {resultat.version_modele} · Grille {resultat.version_grille} ·{" "}
            {versionApplication}
          </span>
          <span>Page 1/1</span>
        </div>
      </div>
    </div>
  );
}
