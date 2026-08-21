"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Command, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Skeleton } from "@/components/ui/skeleton";
import type { SocietaireSearchResult } from "@/lib/contracts";

type RequestState = "idle" | "loading" | "success" | "error";

export function SocietaireSearch() {
  const router = useRouter();
  const [terme, setTerme] = useState("");
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [resultats, setResultats] = useState<SocietaireSearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [recents, setRecents] = useState<SocietaireSearchResult[]>([]);

  useEffect(() => {
    fetch("/api/v1/societaires/recent")
      .then((r) => (r.ok ? r.json() : { elements: [] }))
      .then((donnees) => setRecents(donnees.elements))
      .catch(() => setRecents([]));
  }, []);

  useEffect(() => {
    if (terme.trim().length < 2) {
      return;
    }

    let annule = false;
    const delai = setTimeout(async () => {
      try {
        const reponse = await fetch(
          `/api/v1/societaires/search?terme=${encodeURIComponent(terme)}&limite=8`
        );
        if (!reponse.ok) throw new Error("erreur serveur");
        const donnees = await reponse.json();
        if (annule) return;
        setResultats(donnees.elements);
        setTotal(donnees.total);
        setRequestState("success");
      } catch {
        if (!annule) setRequestState("error");
      }
    }, 250);

    return () => {
      annule = true;
      clearTimeout(delai);
    };
  }, [terme]);

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
                <p>La recherche est momentanément indisponible.</p>
                <button
                  type="button"
                  onClick={() => setRequestState("idle")}
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
                  onSelect={() => router.push(`/societaires/${r.societaire_id}`)}
                  className="flex h-[52px] flex-col items-start justify-center gap-0.5 border-l-2 border-l-transparent data-selected:border-l-solida-teal-800 data-selected:bg-solida-teal-50"
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
                onClick={() => router.push(`/societaires/${r.societaire_id}`)}
                className="flex h-[52px] cursor-pointer flex-col items-start justify-center gap-0.5 px-3 text-left hover:bg-neutre-50"
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
