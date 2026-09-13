import Image from "next/image";
import type { ContributionVariable, FicheJustification, ProduitCreditApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { TRANCHE_COLOR, LABEL_OBJET_CREDIT, LABEL_TRANCHE } from "@/lib/labels";
import { findProduit } from "@/lib/produits";

interface FicheApercuProps {
  fiche: FicheJustification;
  versionApplication: string;
  produits: ProduitCreditApi[];
}

function FactorsBlock({ title, factors }: { title: string; factors: ContributionVariable[] }) {
  return (
    <div className="flex flex-1 flex-col gap-2">
      <span className="text-[11px] font-medium tracking-wide text-neutre-500 uppercase">
        {title}
      </span>
      <ul className="flex flex-col gap-2">
        {factors.map((f) => (
          <li key={f.code_variable} className="text-[11px] text-neutre-700">
            <span className="font-medium text-neutre-950">
              {f.libelle} : {f.valeur}
            </span>
            <br />
            {f.explication}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function FicheApercu({ fiche, versionApplication, produits }: FicheApercuProps) {
  const { resultat: result, demande } = fiche;
  const couleurs = TRANCHE_COLOR[result.tranche];
  const produit = findProduit(produits, demande.produit_id);

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
          <span>{produit?.libelle ?? demande.produit_id}</span>
          <span>{formatAmount(demande.montant_demande)} sollicités</span>
          <span>{demande.duree_demandee_mois} mois</span>
          <span>{LABEL_OBJET_CREDIT[demande.objet_credit]}</span>
        </div>
      </div>

      <div
        className={`flex flex-col gap-1 rounded border-l-3 ${couleurs.border} ${couleurs.background} p-3`}
      >
        <span className="text-[11px] text-neutre-500">Résultat</span>
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-xl">{Math.round(result.score)}</span>
          <span className={`text-sm font-semibold ${couleurs.text}`}>
            {LABEL_TRANCHE[result.tranche]}
          </span>
        </div>
        {result.tranche !== "refus" && (
          <span className="text-[11px]">
            Montant recommandé : {formatAmount(result.montant_recommande)}
          </span>
        )}
      </div>

      {result.trajectoire_progression.length > 0 && (
        <div className="flex flex-col gap-1">
          <span className="text-[11px] font-medium text-neutre-500 uppercase">
            Trajectoire de progression
          </span>
          <div className="flex gap-4 text-[11px]">
            {result.trajectoire_progression.map((p) => (
              <span key={p.cycle}>
                Cycle +{p.cycle} : {formatAmount(p.plafond_accessible)}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-6 border-t border-neutre-200 pt-3">
        <FactorsBlock title="Éléments favorables" factors={fiche.facteurs_favorables} />
        <FactorsBlock title="Points de vigilance" factors={fiche.facteurs_defavorables} />
      </div>

      {fiche.conditions_reexamen.length > 0 && result.tranche !== "accord" && (
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
            Modèle {result.version_modele} · Grille {result.version_grille} · {versionApplication}
          </span>
          <span>Page 1/1</span>
        </div>
      </div>
    </div>
  );
}
