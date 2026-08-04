# Ce que SOLIDA stocke et ce qu'il trace

Ce fichier répond à deux questions précises : **quelles données SOLIDA détient**, et **quels
événements il enregistre**. Il sert de référence pour l'audit, la gouvernance et le pitch.

Rappel : SOLIDA **ne stocke rien dans CORE-SIM** (frontière, `01-ARCHITECTURE/06`). Tout ce qui
suit vit dans la base `solida`, distincte.

---

## 1. Ce que SOLIDA stocke

### Copié de CORE-SIM (le strict nécessaire)

| Donnée | Pourquoi | Classe |
|---|---|---|
| Tables du segment de groupe (`groupe_caution`, `appartenance_groupe`, `garantie`) | Calcul des agrégats de la couche solidaire | technique |
| Index de recherche (nom normalisé, numéro, agence, statut) | Recherche au guichet sans toucher CORE-SIM | nominatif |
| Valeurs de features par sociétaire et date | Scoring rapide, rejeu | financier + technique |

**Ce qui n'est PAS copié :** adresse, téléphone, pièce d'identité, données de santé, coordonnées
bancaires. Elles ne servent pas au modèle. C'est la minimisation, et elle est vérifiable dans le
code de l'adaptateur de lecture.

### Produit par SOLIDA

| Donnée | Contenu | Immuable |
|---|---|---|
| Décisions de scoring | Entrées, features utilisées, score, tranche, décomposition, versions | Oui, insertion seule |
| Décisions finales | Choix de l'agent, montant accordé, motif d'écart | Oui |
| Fiches de justification | PDF archivés dans MinIO | Oui, jamais réécrites |
| Modèles et grilles | Artefacts, métriques, versions | Versionné |
| Utilisateurs et sessions | Identifiant, empreinte de mot de passe, rôle, agence | Mutable (utilisateur), révocable (session) |
| Journal d'audit | Voir section 2 | Oui, insertion seule |

**Le mot de passe n'est jamais stocké en clair** : seulement son empreinte Argon2id (via
FastAPI-Users). SOLIDA ne peut pas retrouver un mot de passe, seulement le vérifier.

---

## 2. Ce que SOLIDA trace

Trois familles d'événements, toutes horodatées et attribuées à un acteur identifié.

### Événements d'accès

| Événement | Données enregistrées |
|---|---|
| Connexion réussie | utilisateur, horodatage, adresse IP |
| Échec de connexion | identifiant tenté, horodatage, adresse IP |
| Déconnexion | utilisateur, horodatage |
| Accès refusé | utilisateur, ressource visée, horodatage |
| Consultation d'un dossier | agent, sociétaire (identifiant opaque), horodatage |

### Événements métier

| Événement | Données enregistrées |
|---|---|
| Scoring rendu | agent, sociétaire, entrée, features, score, tranche, mode, versions |
| Décision finale enregistrée | agent, décision, montant, motif d'écart |
| Fiche générée | agent, décision liée, clé MinIO |
| Écart à la recommandation | sens, ampleur, motif |

### Événements d'administration

| Événement | Données enregistrées |
|---|---|
| Création / modification d'utilisateur | administrateur, cible, changement |
| Changement de rôle | administrateur, cible, ancien et nouveau rôle |
| Modification de la grille | superviseur, ancienne et nouvelle version |
| Promotion / retrait de modèle | administrateur, modèle, version |

---

## 3. Ce que SOLIDA ne trace jamais

| Jamais journalisé | Raison |
|---|---|
| Mot de passe ou jeton, même partiel | Sécurité |
| Nom complet d'un sociétaire dans les journaux techniques | Un identifiant opaque suffit au diagnostic |
| Montant associé à un identifiant nominatif dans les journaux | Minimisation |
| Contenu d'une fiche dans les journaux | Le PDF est dans MinIO, pas dans les logs |
| Adresse IP au-delà de la durée de rétention des journaux | Purge automatique à 90 jours |

Cette discipline distingue un système exploitable en institution financière d'un prototype.

---

## 4. Propriétés du journal d'audit

| Propriété | Mise en œuvre |
|---|---|
| Insertion seule | Aucun `UPDATE` ni `DELETE`, droits base restreints |
| Horodaté | `TIMESTAMPTZ`, horloge serveur |
| Attribué | Toujours un acteur identifié |
| Complet | Une action sensible sans trace est un défaut bloquant |
| Consultable | Écran E7, filtrable |
| Exportable | CSV, selon le rôle |
| Purge encadrée | Uniquement après la durée de rétention, par le job de gouvernance |

---

## 5. Rejeu : la traçabilité qui sert vraiment

Étant donné un identifiant de décision, on recharge les entrées et features **persistées**, le
modèle et la grille de l'époque, on recalcule, et on vérifie l'identité du résultat. Un test de la
CI rejoue un échantillon de décisions à chaque exécution ; si le rejeu diverge, la reproductibilité
est cassée.

C'est ce qui rend réels, et non théoriques : le droit à la contestation du sociétaire, le contrôle
interne, et le recalibrage futur sur données réelles.
