# Rôles applicatifs vs organigramme réel (CEF-MF Lomé)

Ce fichier suit le même statut que `10-politique-credit-decisions-en-attente.md` : ce qui suit
n'est pas tranché, c'est un point de départ documenté pour qu'un futur arbitrage humain sur les
rôles applicatifs s'appuie sur l'organigramme réel plutôt que sur une supposition.

Organigramme de référence : capture d'écran fournie par l'utilisateur le 2026-08-13 (« Annexe 1 :
Organigramme de CEF-MF Lomé »), non versionnée dans le dépôt — 6 agences : Agbalépédo, Kégué,
Zongo, Port, Adétikopé, Légbassito.

## Rapprochement avec les 4 rôles actuels

`ROLES_VALIDES` (`backend/solida/adapters/persistence/modeles_sqlalchemy.py:17`) : `agent`,
`superviseur`, `auditeur`, `administrateur`.

| Rôle SOLIDA | Portée actuelle | Correspondance dans l'organigramme | Statut |
|---|---|---|---|
| `agent` | une seule `agence_id` | Agent de Crédit | Correspond |
| `auditeur` | réseau entier | Contrôle Interne | Correspond |
| `superviseur` | réseau entier (« responsable risque », `10-politique-credit-decisions-en-attente.md:55`) | Directeur d'Epargne et Crédit (niveau siège, pas Chef d'Agence) | À confirmer |
| `administrateur` | réseau entier, opère via l'outillage MLOps externe (`10-politique-credit-decisions-en-attente.md:82-86`) | Aucun équivalent direct — rôle technique/IT, pas une case de l'organigramme métier | Nommage à clarifier |
| — | — | Chef d'Agence (supervision au niveau d'une seule agence) | **Absent de SOLIDA** |
| — | — | Agent de Promotion, Caissier | Absents de SOLIDA (probablement hors périmètre volontaire, cf. `[[perimetre_produit_agent_centrique]]`) |

## Écart principal : aucun rôle scopé à une seule agence en supervision

Vérifié dans le code (`infrastructure/routeurs/scoring.py`, `societaires.py`) : seul le rôle
`agent` filtre par `agence_id`. Tous les rôles au-dessus (`superviseur`, `auditeur`,
`administrateur`) voient l'ensemble du réseau sans restriction. L'organigramme réel place un
**Chef d'Agence** entre l'Agent de Crédit et le niveau siège, avec une supervision limitée à sa
propre agence — ce niveau n'a aucun équivalent applicatif aujourd'hui.

## Décision en attente : faut-il un rôle `chef_agence` ?

Options identifiées (aucune tranchée) :

- **A) Ajouter un 5ᵉ rôle** `chef_agence`, scopé à son `agence_id` comme `agent`, mais avec des
  droits de supervision (ex. lecture de toutes les décisions de sa propre agence, pas seulement
  les siennes). Fidèle à l'organigramme réel ; ajoute une migration, un rôle en base, et une
  logique de cloisonnement à tester.
- **B) Ne rien ajouter** : `superviseur` reste réseau entier, un Chef d'Agence supervise
  humainement sans compte système dédié. Le plus simple, mais s'éloigne de l'organigramme réel
  si un besoin de compte Chef d'Agence apparaît.
- **C) Réutiliser `agent` avec un indicateur optionnel** (ex. `chef_agence: bool`) plutôt qu'un
  rôle distinct. Évite une migration de rôle, mais mélange deux niveaux hiérarchiques dans un
  même rôle — contraire au style « erreurs explicites » du projet (`CLAUDE.md` §6).

Aucune recommandation appliquée pour l'instant : à trancher quand un besoin concret (accès
Chef d'Agence demandé, ou retour terrain de la coopérative) se présente.

## Autres écarts notés, non urgents

- Les comptes de démonstration (`cli_provisionner_comptes.py`, `COMPTES_DEMO`) utilisent des
  codes d'agence fictifs (`CAI-00`, `CAI-01`) plutôt que les 6 agences réelles de l'organigramme.
  À aligner si une démonstration doit un jour refléter fidèlement CEF-MF Lomé — pas un problème
  fonctionnel en soi.
- Le nom `administrateur` désigne aujourd'hui un rôle technique (MLOps/système), pas la direction
  générale de l'organigramme métier. Pas d'action requise, mais à garder en tête pour éviter une
  confusion si ce rôle est un jour présenté à quelqu'un en dehors de l'équipe technique.
