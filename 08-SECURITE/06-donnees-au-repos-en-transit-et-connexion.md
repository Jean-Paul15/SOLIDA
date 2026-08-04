# Sécurité des données : au repos, en transit, et connexion au système partenaire

Ce fichier regroupe et organise ce qui était dispersé, parce que SOLIDA se connecte au système
d'information d'une institution financière et manipule des données nominatives. C'est la partie que
le jury et, plus tard, un auditeur regarderont en premier.

Principe directeur, déjà posé (`01-principes-securite.md`, principe 6) : **aucune donnée de
sociétaire ne quitte le périmètre de la coopérative.** Tout ce qui suit en découle.

---

## 1. Données en transit (chiffrement des flux)

Aucun flux en clair, nulle part, même à l'intérieur du périmètre.

| Flux | Protection |
|---|---|
| Navigateur de l'agent ↔ API | HTTPS obligatoire, HSTS en production, TLS 1.2 minimum |
| API ↔ PostgreSQL (SOLIDA et CORE-SIM) | TLS sur la connexion base, `sslmode=verify-full` en production |
| API ↔ MinIO (fiches, modèles, DVC) | HTTPS sur l'API S3, jamais en clair |
| Services internes entre conteneurs | Réseau Docker isolé ; TLS dès que le trafic sort de l'hôte |
| Connexion au système partenaire (voir §3) | TLS de bout en bout, jamais d'extraction en clair |

**Le cookie de session** est `Secure` (transmis uniquement sur HTTPS), `httpOnly` (inaccessible au
JavaScript) et `SameSite=Lax`. Un jeton n'existe jamais en clair côté client.

**Interdits :** HTTP en clair, TLS auto-signé accepté sans vérification, downgrade de version,
transport d'un secret dans une URL ou un journal.

---

## 2. Données au repos (chiffrement du stockage)

| Élément stocké | Protection au repos |
|---|---|
| Base PostgreSQL SOLIDA | Chiffrement du volume (disque/LUKS ou chiffrement natif du fournisseur) |
| MinIO (fiches PDF, modèles, cache DVC, instantanés) | Chiffrement côté serveur (SSE) activé sur les compartiments |
| Sauvegardes | **Chiffrées avant stockage**, jamais une sauvegarde en clair |
| Mots de passe utilisateurs | Empreinte **Argon2id**, jamais le mot de passe en clair (voir auth) |
| Secrets d'application | Hors du dépôt, injectés par variables d'environnement / gestionnaire de secrets |

**Choix assumé :** on retient le **chiffrement au niveau du disque/volume**, pas le chiffrement
colonne par colonne. Motif : au périmètre d'une coopérative, le chiffrement disque protège contre
le vol de support et la mise au rebut, et le chiffrement colonne ajouterait une gestion de clés
lourde pour un gain marginal derrière un backend déjà cloisonné. Documenté comme tel, pas passé sous
silence. Le chiffrement colonne reste une évolution possible si une donnée ultra-sensible l'exige.

**Gestion des clés :** les clés de chiffrement et les secrets ne sont **jamais** dans le dépôt ni
dans une image Docker. En production, gestionnaire de secrets dédié ; au minimum, variables
d'environnement hors du contrôle de version. Rotation documentée.

---

## 3. Connexion au système partenaire — le point sensible

C'est ta préoccupation, et c'est la bonne : SOLIDA lit les données dans le système de la coopérative
(CORE-SIM, ou le SIG de la CIF). Cette connexion est conçue pour être **la plus contrainte
possible**.

| Garde-fou | Mise en œuvre |
|---|---|
| **Lecture seule stricte** | Rôle PostgreSQL `solida_lecteur` avec `GRANT SELECT` **uniquement**. SOLIDA ne peut techniquement pas écrire dans le système de la coopérative |
| **Aucune écriture en retour** | SOLIDA ne modifie jamais CORE-SIM (`01-ARCHITECTURE/06`). La frontière est mécanique, pas une simple règle |
| **Moindre privilège sur les colonnes** | Pas de `SELECT *` ; seules les colonnes du contrat d'intégration sont lues |
| **Transport chiffré** | TLS sur la connexion à la base source, certificat vérifié |
| **Un seul adaptateur** | Toute la connexion passe par le module `adapters.core_sim` ; la surface est un seul fichier, auditable |
| **Aucune exfiltration** | Aucun appel sortant vers Internet contenant des données métier. Pas de télémétrie de données. Les données restent dans le périmètre |
| **Copie minimale** | SOLIDA ne recopie que le strict nécessaire (voir `05-inventaire-et-tracabilite.md`), pas la base entière |

**Formulation pour le jury :** « Nous nous branchons sur votre système en lecture seule, par un
compte qui ne peut techniquement rien écrire chez vous. Vos données ne quittent pas votre
périmètre : aucun appel sortant, aucune copie externe. » C'est l'argument de souveraineté, et il
répond à la première inquiétude d'une institution financière.

---

## 4. Isolation et réseau

| Mesure | Détail |
|---|---|
| Segmentation | La base et MinIO ne sont pas exposés à Internet ; seuls l'API et le front le sont |
| Réseau interne | Conteneurs sur un réseau Docker privé, ports non publiés sauf nécessité |
| Surface réduite | Aucun chargement de fichier dans le périmètre (surface d'attaque évitée) |
| En-têtes | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, CORS en liste blanche stricte |

---

## 5. Récapitulatif des bonnes pratiques appliquées

Défense en profondeur (aucun contrôle unique), moindre privilège (jusqu'au rôle base en SELECT
seul), sécurité par défaut (tout refusé sauf autorisation), aucune confiance dans le client
(revalidation serveur), souveraineté (rien ne sort du périmètre), traçabilité (journal en insertion
seule), secrets hors dépôt, dépendances analysées. Chiffrement **en transit partout** et **au repos
sur le stockage**.

---

## 6. Ce qui est P0 pour le hackathon, et ce qui est conçu pour la production

**Réellement en place en 72 h (P0) :** HTTPS, cookie `Secure`/`httpOnly`, TLS vers la base,
empreintes Argon2id, rôle `solida_lecteur` en lecture seule, CORS strict, aucun secret dans le
dépôt, aucun appel sortant.

**Conçu et documenté, à finaliser pour un déploiement réel :** chiffrement de volume et sauvegardes
chiffrées avec gestion de clés dédiée, `sslmode=verify-full` avec PKI, rotation des secrets, et
surtout un **audit de sécurité indépendant** — qu'on ne prétend pas avoir réalisé.

**À dire honnêtement au jury s'il creuse :** un déploiement en institution financière exige cet
audit externe. L'architecture est faite pour le passer ; le prototype ne l'a pas subi. Cette
honnêteté vaut mieux, devant un jury sectoriel, qu'une prétention de sécurité parfaite.
