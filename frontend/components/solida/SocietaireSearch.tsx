"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Command, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Skeleton } from "@/components/ui/skeleton";
import type { SocietaireSearchResult } from "@/lib/contracts";
import { ApiError, apiFetch, useApiErrorToast } from "@/lib/services/error-service";

type RequestState = "idle" | "loading" | "success" | "error";

export function SocietaireSearch() {
  const router = useRouter();
  const gererErreur = useApiErrorToast();
  const [terme, setTerme] = useState("");
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [messageErreur, setMessageErreur] = useState<string | null>(null);
  const [resultats, setResultats] = useState<SocietaireSearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [recents, setRecents] = useState<SocietaireSearchResult[]>([]);
  const [navigatingId, setNavigatingId] = useState<string | null>(null);
  const [tentative, setTentative] = useState(0);

  function navigateTo(societaireId: string): void {
    setNavigatingId(societaireId);
    router.push(`/societaires/${societaireId}`);
  }

  useEffect(() => {
    apiFetch("/api/v1/societaires/recent")
      .then((r) => r.json())
      .then((donnees) => setRecents(donnees.elements))
      .catch((e: unknown) => {
        setRecents([]);
        if (e instanceof ApiError && e.kind === "session_expiree") {
          gererErreur(e, "");
        }
      });
  }, [gererErreur]);

  useEffect(() => {
    if (terme.trim().length < 2) {
      return;
    }

    let annule = false;
    const delai = setTimeout(async () => {
      try {
        const reponse = await apiFetch(
          `/api/v1/societaires/search?terme=${encodeURIComponent(terme)}&limite=8`
        );
        const donnees = await reponse.json();
        if (annule) return;
        setResultats(donnees.elements);
        setTotal(donnees.total);
        setRequestState("success");
      } catch (e) {
        if (annule) return;
        setRequestState("error");
        setMessageErreur(
          e instanceof ApiError ? e.message : "La recherche est momentanément indisponible."
        );
        if (e instanceof ApiError && e.kind === "session_expiree") {
          gererErreur(e, "");
        }
      }
    }, 250);

    return () => {
      annule = true;
      clearTimeout(delai);
    };
    // `tentative` ne sert qu'à forcer une nouvelle exécution depuis le bouton "Réessayer" :
    // sans elle, remettre requestState à "idle" ne relance rien puisque `terme` n'a pas changé.
  }, [terme, gererErreur, tentative]);

  const enRepos = terme.trim().length < 2;
  const chargement = !enRepos && requestState === "idle";
  const vide = requestState === "success" && resultats.length === 0;

  return (
    <div className="mx-auto mt-24 flex w-full max-w-[560px] flex-col items-center gap-8">
      <h1 className="font-serif-title text-xl font-semibold text-neutre-950">
        Rechercher un sociétaire
      </h1>

      <Command shouldFilter={false} className="w-full border border-neutre-200 shadow-1">
        <CommandInput
          value={terme}
          onValueChange={setTerme}
          wrapperClassName="h-11!"
          placeholder="Nom, numéro de membre ou numéro de compte"
          onKeyDown={(e) => {
            if (e.key === "Escape") setTerme("");
          }}
        />
        {!enRepos && (
          <CommandList>
            {chargement && (
              <div className="flex flex-col gap-2 p-2">
                <Skeleton className="h-[52px] w-full" />
                <Skeleton className="h-[52px] w-full" />
                <Skeleton className="h-[52px] w-full" />
              </div>
            )}

            {requestState === "error" && (
              <div className="flex flex-col items-center gap-2 py-6 text-sm text-neutre-700">
                <p>{messageErreur ?? "La recherche est momentanément indisponible."}</p>
                <button
                  type="button"
                  onClick={() => {
                    setRequestState("idle");
                    setTentative((t) => t + 1);
                  }}
                  className="cursor-pointer text-solida-teal-800 underline"
                >
                  Réessayer
                </button>
              </div>
            )}

            {vide && (
              <p className="py-6 text-center text-sm text-neutre-500">
                Aucun sociétaire ne correspond à « {terme} ». Vérifiez l&rsquo;orthographe ou
                essayez le numéro de membre.
              </p>
            )}

            {requestState === "success" &&
              !vide &&
              resultats.map((r) => (
                <CommandItem
                  key={r.societaire_id}
                  value={r.societaire_id}
                  onSelect={() => navigateTo(r.societaire_id)}
                  className={`flex h-[52px] flex-col items-start justify-center gap-0.5 border-l-2 border-l-transparent data-selected:border-l-solida-teal-800 data-selected:bg-solida-teal-50 ${
                    navigatingId === r.societaire_id ? "bg-solida-teal-50" : ""
                  }`}
                >
                  <div className="flex w-full items-center justify-between">
                    <span className="text-sm font-medium text-neutre-950">{r.nom_complet}</span>
                    {r.a_credit_en_cours && (
                      <span className="text-xs text-neutre-500">● Crédit en cours</span>
                    )}
                  </div>
                  <span className="text-xs text-neutre-500">
                    N° {r.numero_membre} · {r.agence} · {r.zone.replace("_", "-")}
                  </span>
                </CommandItem>
              ))}

            {requestState === "success" && total > resultats.length && (
              <p className="py-2 text-center text-xs text-neutre-500">
                {total - resultats.length} autres résultats. Précisez votre recherche.
              </p>
            )}
          </CommandList>
        )}
      </Command>

      {enRepos && recents.length > 0 && (
        <div className="flex w-full flex-col gap-2">
          <span className="text-xs font-medium text-neutre-500">Consultés récemment</span>
          <div className="flex flex-col divide-y divide-neutre-200 rounded-lg border border-neutre-200">
            {recents.map((r) => (
              <button
                key={r.societaire_id}
                type="button"
                onClick={() => navigateTo(r.societaire_id)}
                className={`flex h-[52px] cursor-pointer flex-col items-start justify-center gap-0.5 px-3 text-left hover:bg-neutre-50 ${
                  navigatingId === r.societaire_id ? "bg-solida-teal-50" : ""
                }`}
              >
                <div className="flex w-full items-center justify-between">
                  <span className="text-sm font-medium text-neutre-950">{r.nom_complet}</span>
                  {r.a_credit_en_cours && (
                    <span className="text-xs text-neutre-500">● Crédit en cours</span>
                  )}
                </div>
                <span className="text-xs text-neutre-500">
                  N° {r.numero_membre} · {r.agence} · {r.zone.replace("_", "-")}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
