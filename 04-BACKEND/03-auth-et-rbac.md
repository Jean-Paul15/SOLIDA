# Authentification et autorisation

## Décision : FastAPI-Users, pas d'auth écrite à la main, pas de service séparé

Voir ADR-009. On ne construit rien from scratch et on n'ajoute pas de service d'IAM.

**Brique retenue : FastAPI-Users** (librairie Python, licence MIT), embarquée dans le backend
FastAPI. Elle fournit, maintenu et testé par une communauté : gestion des utilisateurs, hachage
Argon2, sessions par cookie ou JWT, vérification, réinitialisation. On l'habille de nos rôles et de
notre cloisonnement par agence, rien de plus.

**Pourquoi cette brique plutôt que les autres :**

| Option étudiée | Écartée pour SOLIDA parce que |
|---|---|
| Supabase (GoTrue + RLS) | Le RLS ne prend son sens que si le client parle directement à la base ; notre backend FastAPI passe devant et l'utilise via le rôle de service, donc le RLS est contourné. On paierait 7 services pour n'en exploiter que deux, à moitié. Contredit la légèreté |
| Zitadel / Authentik / Keycloak | Vrais IAM (OIDC, MFA, fédération) surdimensionnés pour 4 rôles et un cloisonnement par agence. Un service de plus à exploiter dans une coopérative |
| Auth écrite à la main | Inutile et risqué : une librairie maintenue fait mieux et déjà testé |

**Pourquoi c'est le bon niveau :** FastAPI-Users n'est pas « from scratch » (c'est une librairie
maintenue) mais n'ajoute pas non plus un service à exploiter. L'auth vit dans le backend, donc le
journal d'audit reste co-localisé avec les décisions, et un auditeur relie une décision à un agent
par une simple clé, pas par une correspondance approximative entre deux référentiels.

**Évolution documentée :** le jour où une coopérative demande du SSO d'entreprise, de la fédération
LDAP ou du MFA matériel, on introduit Zitadel (Go, léger, OIDC) comme fournisseur d'identité en
amont, sans réécrire la logique de rôles. C'est prévu, pas fait maintenant.

## Mécanique

| Élément | Choix | Fourni par |
|---|---|---|
| Hachage | Argon2id (`argon2-cffi`), paramètres OWASP à vérifier à l'implémentation | FastAPI-Users |
| Jeton d'accès | JWT, durée courte (15 minutes) | FastAPI-Users |
| Renouvellement | Stratégie base de données, empreinte stockée, révocable, 8 heures | FastAPI-Users |
| Transport | Cookie `httpOnly`, `Secure`, `SameSite=Lax` | Notre configuration |
| Modèle utilisateur | Étendu avec `role` et `agence_id` | Notre code |

**Le jeton n'est jamais dans `localStorage`.** Cookie `httpOnly`, inaccessible au JavaScript, donc
immunisé contre le vol par XSS. FastAPI-Users supporte nativement le transport par cookie.

**Durée de session de 8 heures :** une journée de travail en agence. L'agent se connecte le matin
et n'est pas interrompu.

## Rôles

FastAPI-Users gère l'authentification ; **les rôles et le cloisonnement sont notre logique métier**,
implémentés dans la couche cas d'usage, pas dans la librairie.

| Rôle | Droits |
|---|---|
| `agent` | Rechercher, consulter un dossier, créer une demande, scorer, générer une fiche, enregistrer une décision — **limité à son agence** |
| `superviseur` | Tout l'agent, sur toutes les agences, + registre + paramétrage de la grille |
| `auditeur` | **Lecture seule** du registre et des fiches. Ne score pas |
| `administrateur` | Utilisateurs, rôles, supervision du modèle. **Ne score pas** |

**Séparation délibérée :** l'administrateur ne score pas, l'auditeur ne décide pas. Principe de
contrôle interne élémentaire dans une institution financière, et qui se remarque favorablement
devant un jury sectoriel.

## Cloisonnement par agence

Un agent n'accède qu'aux sociétaires de son agence. **Contrôle appliqué côté serveur, dans le cas
d'usage**, jamais par filtrage côté client. Un filtre client est un affichage, pas une sécurité.

## Autorisation en deux temps

1. **À l'endpoint** : une dépendance FastAPI vérifie que le rôle a accès à l'opération.
2. **Dans le cas d'usage** : vérification que cet utilisateur a accès à cette ressource précise.

Le second point est celui qu'on oublie et qui produit les failles d'accès direct par identifiant.

Mise en œuvre concrète : FastAPI-Users expose `current_active_user` comme dépendance ; on la
compose avec une dépendance `exige_role(...)` et une vérification d'agence dans le cas d'usage.

## Ce qui est journalisé

Connexion réussie, échec de connexion, déconnexion, changement de rôle, accès refusé, consultation
d'un dossier, scoring, génération de fiche, modification de la grille, création ou modification
d'utilisateur.

Chaque entrée : acteur, action, objet, horodatage, adresse IP. Voir
`08-SECURITE/03-audit-et-tracabilite.md` et `08-SECURITE/05-inventaire-et-tracabilite.md`.

## Mesures complémentaires

| Mesure | Détail | Périmètre |
|---|---|---|
| Limitation de débit sur la connexion | 5 tentatives par identifiant / 15 min | P2 |
| Verrouillage temporaire | 15 min après 10 échecs | P2 |
| Politique de mot de passe | 12 caractères min, contrôle contre corpus compromis | P2 |
| Premier mot de passe | Changé à la première connexion | P1 |
| Révocation de session | Renouvellement révocable côté serveur | P0, fourni par FastAPI-Users |

## Périmètre hackathon

**P0 :** intégration de FastAPI-Users, transport par cookie, les 4 rôles, cloisonnement par agence.
C'est peu de code puisque la librairie porte l'essentiel.
**P1 :** changement de mot de passe au premier accès, journal d'audit complet.
**P2 :** limitation de débit, verrouillage, corpus de mots de passe compromis, MFA.

Ces reports sont **documentés comme prévus**, ce qui vaut mieux que de les implémenter à moitié.
