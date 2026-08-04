# Démonstration et pitch

## Structure du pitch

Durée à confirmer sur place. Prévoir une version de 5 minutes et une de 3 minutes.

| Temps | Contenu |
|---|---|
| 0:00 – 0:40 | **Le problème**, chiffré. Taux de dégradation du portefeuille au Togo : 6,7 % en 2025 contre une norme BCEAO de 3 %. Instruction manuelle, subjective, lente |
| 0:40 – 1:10 | **L'idée en une phrase** : la donnée la plus prédictive dont dispose une coopérative n'est pas à chercher chez un tiers, c'est la trajectoire d'épargne et le comportement de remboursement qu'elle enregistre déjà pour chaque membre |
| 1:10 – 3:10 | **Démonstration en direct** |
| 3:10 – 4:00 | **Les résultats** : comparatif des trois modèles, gain de la couche solidaire, taux d'approbation à risque constant |
| 4:00 – 4:40 | **Le déploiement** : contrat d'intégration, aucune dépendance externe, un adaptateur à écrire |
| 4:40 – 5:00 | **Conclusion** : ce que la CIF gagne à l'échelle du réseau |

## Déroulé de la démonstration — 2 minutes, répété

Chaque étape est chronométrée et répétée. Aucune improvisation.

1. **Recherche.** Taper un nom partiel avec une faute d'orthographe volontaire. Les résultats
   apparaissent. *« L'agent tape un nom, c'est tout ce qu'il saisit sur ce sociétaire. »* (15 s)

2. **Dossier 360°.** *« Tout ceci existe déjà dans le système de la coopérative. Nous ne
   demandons aucune donnée nouvelle. »* Pointer la bande des 12 mois d'épargne et sa tendance.
   (25 s)

3. **Demande.** Ouvrir le panneau. *« Quatre champs. L'agent ne ressaisit rien de ce que
   l'institution sait déjà. »* (15 s)

4. **Score.** Le score s'affiche. Pointer la tranche, le montant recommandé, puis les
   contributions. *« Chaque point est attribué à une variable, et la somme fait exactement le
   score. Ce n'est pas une approximation. »* (35 s)

5. **Trajectoire de progression.** Pointer le bloc de plafond conseillé et les trois cycles
   suivants. *« Le système ne s'arrête pas à un chiffre : il montre au sociétaire le chemin s'il
   rembourse sans incident. C'est le crédit progressif, rendu explicite. »* Si le dossier
   appartient au segment groupement, ouvrir E5 : *« Sur ce segment, le remboursement du groupe
   entre aussi dans le score — c'est un tableau, pas un graphe : la structure réelle d'un groupe
   de dix membres se lit plus vite ainsi. »* (20 s)

6. **Cas démarrage à froid.** Basculer sur un primo-emprunteur. *« Aucun historique, aucun groupe.
   Le système fonctionne quand même, sur le socle individuel, et applique le crédit progressif.
   C'est le cas le plus fréquent en microfinance. »* (20 s)

7. **Fiche.** Générer le PDF. *« Ce document est remis au sociétaire. Dans une coopérative, le
   demandeur est un sociétaire : il a droit à une explication. »* (15 s)

**L'étape 6 est celle qui distingue une équipe qui a réfléchi d'une équipe qui a codé.** Ne pas la
sauter, même en version courte.

## Règles de démonstration

| Règle | Motif |
|---|---|
| Une seule personne manipule | Deux mains sur un clavier = confusion |
| Données figées et vérifiées le matin même | Un cas qui plante devant le jury est irrattrapable |
| Aucune fenêtre de terminal visible | On montre le produit, pas le code |
| Aucune fonctionnalité découverte en direct | Chaque clic a été répété |
| Vidéo de secours prête | Wi-Fi saturé, projecteur capricieux |

## Questions attendues et réponses préparées

**« D'où viennent vos données ? »**
Synthétiques, calibrées sur les statistiques publiques du secteur — taux de dégradation togolais,
encours moyen UEMOA, plafond du taux d'usure. Nous l'assumons et le documentons. La validation
réelle passe par le rejeu sur un extrait anonymisé d'une coopérative pilote, qui est l'étape 1 de
notre trajectoire.

**« Pourquoi ne pas exploiter le graphe de garanties avec des méthodes de graph ML (GNN, PageRank, centralité) ? »**
Nous l'avons envisagé, puis vérifié la structure réelle d'un portefeuille COOPEC avant de trancher :
le crédit y est majoritairement individuel, adossé à l'épargne nantie ; le crédit de groupe est un
segment minoritaire. La densité de réseau qu'exigent ces méthodes — documentée dans la littérature
sur le crédit P2P ou les réseaux de garanties d'entreprises — n'existe pas ici. Les appliquer
produirait un signal essentiellement bruité, pas une amélioration. Sur le segment de groupe, nous
calculons trois agrégats simples (remboursement du groupe, taille, « déjà secouru »), qui captent
l'essentiel de ce que la structure réelle porte. C'est une décision d'ingénierie, pas un renoncement
par manque de temps — et elle tient devant un expert qui connaît la structure réelle d'un
portefeuille mutualiste.

**« Comment obtenez-vous les données mobile money ? »**
Nous n'en dépendons pas. Un accord de partage avec un opérateur télécom prend des mois. Notre
système fonctionne uniquement sur les données que la coopérative détient déjà. C'est précisément ce
qui le rend déployable à court terme.

**« En quoi est-ce lié à ce que la CIF fait déjà ? »**
Le projet DigiCoop-WA a digitalisé la collecte de l'épargne et l'octroi de crédit sur le socle
SAB-AT, déployé en temps réel dans les six réseaux. SOLIDA n'ajoute aucune infrastructure : c'est
la couche de décision qui exploite cette donnée déjà centralisée. C'est le prolongement de
DigiCoop-WA vers DigiCoop-WA+, pas un projet parallèle.

**« Quelle est votre accuracy ? »**
Nous ne présentons pas d'accuracy. Sur un portefeuille à 7-9 % de défaut, un modèle qui prédit
toujours « pas de défaut » dépasse 90 % et ne sert à rien. Nous rapportons AUC, Gini et AUPRC, avec
la calibration, qui sont les métriques du scoring de crédit.

**« Comment gérez-vous un nouveau client sans historique ? »**
C'est l'architecture en cascade. Socle individuel toujours actif — porté par l'épargne, disponible
dès la première demande — enrichissement solidaire conditionnel sur le seul segment de groupe,
repli avec crédit progressif. 45 % des dossiers sont des primo-emprunteurs ; un système qui ne les
traite pas ne traite pas le cas majoritaire. Démonstration à l'appui.

**« Combien de temps pour déployer chez une IMF ? »**
Le contrat d'intégration définit des champs standards dans un système de gestion de microfinance,
déjà centralisés pour les réseaux CIF sur SAB-AT. Trois modes d'intégration, dont l'export
périodique qui ne demande rien à l'éditeur du SI. Côté code, un seul fichier change : l'adaptateur
de lecture.

**« Et la protection des données personnelles ? »**
Minimisation appliquée : nous ne copions ni adresse, ni téléphone, ni pièce d'identité. Données
sensibles exclues du modèle. Aucun appel sortant. Nous ne sommes pas juristes : un déploiement réel
exigerait une vérification juridique, et nous le disons.

**« Et le changement climatique, les saisons qui ne sont plus régulières ? »**
On ne fixe pas de calendrier agricole, justement parce que les saisons sont devenues irrégulières :
le début de la saison des pluies varie de plusieurs semaines d'une année à l'autre. À la place, on
capte la santé micro-économique de chaque secteur à partir de vos propres données de portefeuille,
de façon adaptative : quand un secteur souffre, ça se voit dans les retraits d'épargne puis dans les
impayés, sans aucune donnée météo externe. L'intégration de données climatiques externes est notre
feuille de route quand l'infrastructure le permettra ; aujourd'hui elle n'est ni souveraine ni
déployable dans une IMF à faible connectivité.

**« Quel est l'impact financier concret de votre modèle ? »**
On ne s'arrête pas à l'AUC. On fixe le seuil de décision par une matrice de coûts : refuser un bon
client coûte la marge nette, accorder à un défaillant coûte la perte en capital après garantie. Le
seuil optimal C_FP/(C_FP+C_FN) tombe autour de 17 %, pas 50 %. Sur notre portefeuille de test, passer
du seuil naïf au seuil optimal économise environ 17 % du coût des erreurs, et les 20 % de dossiers
les plus risqués concentrent environ 40 % des créances en souffrance : l'agent qui concentre sa
vigilance sur un dossier sur cinq en capte deux sur cinq. Le modèle n'est pas une prouesse
statistique, c'est de l'argent économisé et du temps d'agent mieux ciblé.

**« Qui décide finalement ? »**
L'agent et le comité de crédit. Le système recommande. Nous mesurons d'ailleurs le taux d'écart
entre recommandation et décision : un taux nul signalerait que l'outil se substitue à l'humain, ce
que nous ne voulons pas.

## Slides — 10 maximum

1. Titre, logo, thématique
2. Le problème, en trois chiffres
3. L'idée en une phrase
4. Architecture en cascade, schéma
5. La trajectoire d'épargne dynamique et la couche solidaire, schéma
6. Démonstration (slide de transition)
7. Résultats comparatifs
8. Déploiement et contrat d'intégration
9. Éthique et gouvernance
10. Ce que la CIF y gagne

Peu de texte. Une idée par slide. Les slides accompagnent, elles ne sont pas lues.

## Erreurs à ne pas commettre

| Erreur | Pourquoi c'est grave |
|---|---|
| Parler d'IA plutôt que de scoring | Le TDR demande un système de scoring |
| Montrer du code | Le jury évalue un produit |
| Annoncer une performance sans dire que les données sont générées | Un jury sectoriel le devinera et la confiance s'effondre |
| Promettre du mobile money | Un membre du jury saura que c'est irréaliste |
| Dépasser le temps | Coupé net |
| Répondre « on n'a pas eu le temps » | Répondre « c'est hors de notre périmètre, voici pourquoi » |
