"use client";

/**
 * File d'attente hors-ligne pour l'envoi de la demande (C8 -> C9). Section 6 de
 * SOLIDA_Flux_Societaire.md : "si le lien tombe pendant la saisie, la demande est
 * conservée localement et part dès le retour du réseau [...] aucune donnée
 * personnelle stockée sur le téléphone au-delà de la session" — la file est donc
 * l'exception explicitement prévue par le document, pas une violation de cette
 * règle : elle ne contient qu'une demande en transit, effacée dès l'envoi réussi.
 *
 * IndexedDB plutôt que localStorage : c'est la même doctrine que le frontend agent
 * (03-MODELE/13-connectivite-et-connecteur-donnees.md : jamais de donnée métier en
 * localStorage/sessionStorage) — IndexedDB n'est pas nommément interdit par cette
 * règle et convient mieux à une file (transactionnel, pas de limite de taille
 * pratique), mais reste un stockage navigateur : à vider systématiquement après
 * envoi réussi, jamais conservé "au cas où".
 */

const NOM_BASE = "solida-portail-file-attente";
const NOM_MAGASIN = "demandes-en-attente";
const CLE_UNIQUE = "demande-courante";

export interface DemandeEnAttente {
  jeton_session: string;
  montant: number;
  objet: string;
  duree_mois: number;
  revenu_mensuel_declare: number | null;
  charges_mensuelles: number | null;
  mise_en_file_le: string;
}

function ouvrirBase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const requete = indexedDB.open(NOM_BASE, 1);
    requete.onupgradeneeded = () => {
      requete.result.createObjectStore(NOM_MAGASIN);
    };
    requete.onsuccess = () => resolve(requete.result);
    requete.onerror = () => reject(requete.error);
  });
}

export async function mettreEnFile(demande: DemandeEnAttente): Promise<void> {
  const base = await ouvrirBase();
  await new Promise<void>((resolve, reject) => {
    const transaction = base.transaction(NOM_MAGASIN, "readwrite");
    transaction.objectStore(NOM_MAGASIN).put(demande, CLE_UNIQUE);
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
  base.close();
}

export async function lireFile(): Promise<DemandeEnAttente | undefined> {
  const base = await ouvrirBase();
  const resultat = await new Promise<DemandeEnAttente | undefined>(
    (resolve, reject) => {
      const transaction = base.transaction(NOM_MAGASIN, "readonly");
      const requete = transaction.objectStore(NOM_MAGASIN).get(CLE_UNIQUE);
      requete.onsuccess = () =>
        resolve(requete.result as DemandeEnAttente | undefined);
      requete.onerror = () => reject(requete.error);
    },
  );
  base.close();
  return resultat;
}

export async function viderFile(): Promise<void> {
  const base = await ouvrirBase();
  await new Promise<void>((resolve, reject) => {
    const transaction = base.transaction(NOM_MAGASIN, "readwrite");
    transaction.objectStore(NOM_MAGASIN).delete(CLE_UNIQUE);
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
  base.close();
}
