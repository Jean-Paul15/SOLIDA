# Périmètre : ce qui est dans le hackathon, ce qui n'y est pas

Ce fichier prime sur tout enthousiasme technique. En 72 heures, **le risque numéro un est la dérive
de périmètre**, pas le manque d'ambition.

## Principe de priorité

> Une démonstration complète et cohérente d'un périmètre réduit bat une démonstration partielle
> d'un périmètre ambitieux. Toujours.

L'ordre de livraison est strict. On ne commence P2 que si P1 est entièrement fonctionnel.

## P0 — Sans cela, il n'y a pas de démonstration

| Élément | Critère de réussite |
|---|---|
| Générateur CORE-SIM | Base peuplée, cohérente, rejouable via une graine fixe |
| Socle EBM entraîné | Modèle sérialisé, métriques calculées |
| Transformation score + grille | Un dossier entre, un score entier et une tranche sortent |
| API de scoring | Un endpoint répond avec un score et une décomposition |
| Recherche de sociétaire + fiche 360° | L'agent saisit un nom, obtient le dossier complet |
| Écran de résultat de scoring | Score, tranche, montant recommandé, facteurs |

## P1 — Ce qui fait la différence sur les critères de notation

| Élément | Sert quel critère |
|---|---|
| Trajectoire d'épargne dynamique (tendance, régularité, effort) | Originalité (20 %) |
| Moteur de décision : crédit progressif + fiche actionnable | Originalité, Impact |
| Variables solidaires (segment GIE) + modèle enrichi | Originalité, Pertinence |
| Comparatif à trois modèles (logistique / EBM socle / EBM + solidaire) | Faisabilité et réalisme (20 %) |
| Fiche de justification exportable en PDF, avec conditions de réexamen | Pertinence, Impact |
| Cas de démonstration « démarrage à froid » | Faisabilité, Impact |
| Écran du groupe de caution (segment GIE) | Originalité, effet en démo |

## P2 — Si et seulement si P0 et P1 sont finis

- Paramétrage de la grille par le superviseur depuis l'interface
- Registre d'audit consultable
- MLflow branché avec comparaison d'expériences visible
- Tableau de bord agent avec indicateurs
- Détection de dérive (calcul PSI sur un jeu décalé)

## Hors périmètre — à ne pas commencer, même si le temps semble le permettre

| Écarté | Raison |
|---|---|
| Intégration mobile money (Flooz, Mixx by Yas) | Accord de partage impossible à court terme |
| Suivi IFRS 9 / staging / provisionnement | Relève du suivi de portefeuille, pas de l'octroi |
| Mode hors ligne avec synchronisation | Trop coûteux pour 72 h, mentionné en perspective |
| Application mobile | Le poste agent est un poste fixe en agence |
| Multi-tenant / multi-coopérative | Une seule institution simulée suffit |
| Kubernetes | Docker Compose suffit et se démontre |
| Authentification SSO / LDAP | JWT interne suffit pour la démonstration |
| Internationalisation | Français uniquement |

## Ce qui est préparé AVANT le hackathon

Autorisé : le dossier de candidature permet de joindre un « prototype existant ».

- Ce dossier de principes
- Le générateur CORE-SIM (mécanique complète, paramètres externalisés)
- Le squelette des dépôts, la configuration Docker, les hooks Git
- Le design system et les composants de base du front
- Les contrats d'interface et leurs implémentations factices
- Les tests de la logique métier pure (scorecard, cascade, grille)
- La trame du pitch

## Ce qui se fait SUR PLACE

- Entraînement effectif et comparaison des modèles
- Construction des agrégats de la couche solidaire (segment de groupe)
- Câblage API ↔ modèle ↔ interface
- Fiche de justification et export PDF
- Jeu de cas de démonstration
- Répétition du pitch
