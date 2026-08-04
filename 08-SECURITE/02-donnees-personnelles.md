# Données personnelles

## Cadre

Le Togo dispose d'une législation sur la protection des données personnelles, et l'UEMOA d'un
cadre communautaire. **L'équipe n'est pas juriste** : ce document énonce des principes de
conception défendables, pas un avis juridique. Un déploiement réel exigerait une vérification par
un juriste et, le cas échéant, une déclaration auprès de l'autorité compétente.

Cette réserve doit être dite telle quelle si le jury pose la question. Elle est plus solide qu'une
affirmation de conformité que nous ne pouvons pas étayer.

## Principes appliqués

### Minimisation
Seules les données nécessaires au scoring sont copiées de CORE-SIM vers SOLIDA. Nous ne copions ni
adresse, ni numéro de téléphone, ni pièce d'identité, ni données de santé : elles ne servent pas au
modèle.

Ce point est vérifiable dans le code et se démontre.

### Finalité
Les données servent au scoring d'octroi et à rien d'autre. Le score n'est pas une note de
moralité, il n'est pas partagé avec des tiers, il ne sert pas à des fins commerciales.

### Exactitude
Le sociétaire doit pouvoir faire corriger une donnée erronée. La correction se fait **dans CORE-SIM**,
c'est-à-dire dans le système de la coopérative, et se propage au batch suivant. SOLIDA n'est pas la
source de vérité et ne doit jamais le devenir.

### Conservation
| Donnée | Durée |
|---|---|
| Feature store | 24 mois glissants |
| Décisions de scoring | Durée légale de conservation des dossiers de crédit |
| Fiches de justification | Idem |
| Journal d'audit | 5 ans |
| Journaux techniques | 90 jours |

### Sécurité
Voir `01-principes-securite.md`.

### Transparence
Le sociétaire est informé qu'un outil d'aide à la décision est utilisé, et reçoit une fiche
expliquant les facteurs. C'est le rôle de la fiche de justification.

## Données sensibles

| Donnée | Traitement |
|---|---|
| Sexe | Généré dans CORE-SIM, **exclu du modèle**, utilisé pour le contrôle de non-discrimination |
| Appartenance ethnique ou religieuse | **Non collectée, non générée** |
| Données de santé | Non collectées. L'objet « urgence santé » est une catégorie de crédit, pas une donnée médicale |
| Opinions politiques | Non collectées |
| Données biométriques | Non collectées |

## Anonymisation en développement

Pendant le hackathon, toutes les données sont **synthétiques**. Aucune donnée réelle de sociétaire
n'est utilisée. C'est un point de conformité fort à mettre en avant.

Lors d'un futur rejeu sur données réelles d'une IMF pilote :
- Pseudonymisation avant transfert
- Aucun nom en clair dans l'environnement de développement
- Traitement dans le périmètre de l'IMF si possible

## Droits des personnes

| Droit | Mise en œuvre |
|---|---|
| Accès | La coopérative peut extraire toutes les décisions concernant un sociétaire |
| Rectification | Via CORE-SIM, propagation au batch suivant |
| Explication | Fiche de justification |
| Contestation | Rejeu de la décision avec le modèle et la grille d'époque |
| Intervention humaine | La décision finale est toujours humaine |

Les deux derniers points sont des exigences classiques en matière de décision automatisée. Notre
architecture les satisfait par construction, ce qui est un argument solide.
