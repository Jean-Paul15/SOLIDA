# Principes de sécurité

SOLIDA manipule des données financières nominatives dans une institution financière. Le niveau
d'exigence n'est pas celui d'un prototype.

## Les six principes

### 1. Moindre privilège
Chaque composant a le minimum de droits. `solida_lecteur` ne peut que lire CORE-SIM. Un agent
n'accède qu'à son agence. L'administrateur ne score pas. L'auditeur ne décide pas.

### 2. Défense en profondeur
Aucun contrôle unique. Un contrôle d'accès est vérifié à l'endpoint **et** dans le cas d'usage.
Un secret est absent du dépôt **et** bloqué par un hook **et** analysé en intégration continue.

### 3. Sécurité par défaut
Tout est refusé sauf autorisation explicite. Un nouvel endpoint sans annotation de rôle est
inaccessible, il n'est pas ouvert à tous.

### 4. Aucune confiance dans le client
Toute validation faite côté front est refaite côté serveur. Un filtre d'agence côté client est un
confort d'affichage, jamais une sécurité.

### 5. Traçabilité
Toute action sensible est journalisée avec acteur, objet, horodatage. Le journal est en insertion
seule.

### 6. Souveraineté
Aucune donnée de sociétaire ne sort du périmètre. Aucun appel sortant, aucune télémétrie
contenant des données métier.

## Contrôles techniques obligatoires

| Domaine | Contrôle |
|---|---|
| Injection SQL | ORM ou requêtes paramétrées. **Jamais de concaténation de chaîne** |
| XSS | Échappement par défaut de React ; `dangerouslySetInnerHTML` interdit |
| CSRF | Cookies `SameSite=Lax` + jeton anti-CSRF sur les mutations |
| Clickjacking | En-tête `X-Frame-Options: DENY` |
| Sniffing MIME | `X-Content-Type-Options: nosniff` |
| Transport | HTTPS obligatoire, HSTS en production |
| CORS | Liste blanche stricte. **Jamais `*`** |
| Débit | Limitation sur la connexion et le scoring |
| Chargement de fichier | Aucun dans le périmètre — surface d'attaque évitée |
| Dépendances | Analyse automatisée, mise à jour des vulnérabilités critiques |

## Politique de mot de passe

12 caractères minimum, vérification contre les corpus de mots de passe compromis, hachage Argon2id,
changement obligatoire à la première connexion, aucune règle de complexité arbitraire (elle produit
des mots de passe prévisibles), aucune expiration périodique (elle produit des incréments).

## Secrets

Voir `04-secrets-et-config.md`.

## Ce que nous ne faisons pas, et pourquoi c'est un choix

| Non implémenté | Motif |
|---|---|
| Double authentification | Reporté. Documenté comme évolution |
| Chiffrement au niveau colonne | Le chiffrement disque suffit au périmètre |
| WAF | Hors périmètre d'une coopérative |
| Audit de sécurité externe | À prévoir avant tout déploiement réel |

**Le dernier point doit être dit honnêtement au jury s'il pose la question :** un déploiement réel
en institution financière exige un audit de sécurité indépendant. Nous avons conçu pour, nous ne
prétendons pas l'avoir fait.

## Périmètre hackathon

P0 : requêtes paramétrées, Argon2, cookies `httpOnly`, CORS strict, contrôle des rôles, aucun
secret dans le dépôt.
P2 : limitation de débit, en-têtes complets, analyse de dépendances.
