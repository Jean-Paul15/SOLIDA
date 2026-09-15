# SOLIDA — Une décision comprise. Une confiance préservée.

**Discours national révisé le 14 septembre 2026**  
**Format : 8 minutes de présentation, puis 2 minutes de questions.**  
**Cible de répétition : 7 min 30 s, démonstration et transitions comprises.**

**Volume oral : environ 820 mots.** À 135 mots par minute, cela représente environ 6 minutes de parole et laisse environ 1 min 30 s pour les manipulations, pauses et transitions avant la cible de 7 min 30 s. Cette estimation ne remplace pas un passage chronométré.

Ce document contient le discours à prononcer, le conducteur, les sources vérifiées et une évaluation critique. Seuls les paragraphes en citation de la partie 1 se récitent. Les indications en italique, les appels de source et les annexes ne se lisent pas.

Les horaires sont des objectifs de répétition, pas une durée mesurée. La répartition des prises de parole reprend le document fourni ; elle ne présume pas des métiers ou des contributions individuelles. Le bilan des 72 heures reprend la précision donnée par l’équipe : seule l’interface agence préexistait ; le modèle, son entraînement, son intégration et le parcours sociétaire ont été réalisés pendant le concours.

## 1. Discours à prononcer

### 0:00–0:50 — Junior — Donner un visage à l’enjeu

*Slide 1. Regarder le jury. Prendre une courte pause après la question.*

> Mesdames et Messieurs, imaginez Afi. Elle demande un crédit pour financer une dépense de scolarité. Sa première question sera : « Est-ce possible ? » Mais si la réponse est non, une deuxième compte tout autant : « Pourquoi, et que puis-je faire ? »
>
> Afi est un personnage de démonstration. L’enjeu est bien réel : fin 2025, dans l’échantillon togolais suivi par la BCEAO, près de 30 milliards de francs CFA de créances étaient en souffrance.[S1]
>
> L’agent doit protéger les ressources de son institution tout en accompagnant ses sociétaires. Pour cela, il lui faut une évaluation du risque qu’il puisse comprendre et expliquer.

### 0:50–1:25 — Junior — Poser la promesse et montrer le travail accompli

*Slide 2. Trois mots dominent : comprendre, expliquer, accompagner.*

> C’est ce que nous construisons avec SOLIDA : une aide à la décision de crédit, qui transforme les données disponibles en une recommandation expliquée.
>
> En arrivant, nous avions l’interface agence, sans modèle. Pendant ces 72 heures, nous avons construit et entraîné le modèle, intégré son calcul et ajouté le parcours sociétaire.
>
> Voici le résultat : un scénario, deux points de vue. Celui d’Afi, puis celui de l’agent.

### 1:25–2:25 — Gédéon parle, Jean-Paul manipule — La demande d’Afi

*Portail sociétaire en plein écran, sur l’accueil de la caisse. Afi est une sociétaire réelle du jeu de démonstration (numéro de compte 113686, dernier dépôt 14 807 FCFA), déjà suivie par un agent : sa demande s’affectera donc directement à lui, sans passer par le superviseur. Rejouer le cas répété : 3 000 000 FCFA, produit Crédit Épargne avec Éducation, scolarité, puis 12 mois. Ne pas changer les paramètres sans refaire la démo.*

> Afi choisit « Faire une demande ». Aucun compte à créer, aucun mot de passe à retenir : elle indique son numéro de compte, puis le montant de son dernier dépôt.
>
> Reconnue par son prénom, elle saisit le montant souhaité, choisit son produit, l’usage si nécessaire, puis la durée.
>
> Le calcul se déroule en coulisse. Afi voit simplement : « C’est parti ! » Sa demande est transmise ; son agent la recontactera. Aucun score ni verdict à interpréter.
>
> Côté agence, cette même demande apparaît maintenant, sans copie ni préparation : Afi est déjà suivie par cet agent, elle lui est donc affectée directement, sans passer par la file d’attente du superviseur.

*Laisser voir la demande apparaître dans la liste de l’agent. C’est la même demande qu’Afi vient d’envoyer, pas une copie : l’affectation directe est automatique parce qu’Afi a déjà un agent habituel. Un nouveau sociétaire, sans historique, passerait lui par la file du superviseur — les deux mécanismes coexistent.*

### 2:25–4:10 — Gédéon parle, Jean-Paul manipule — Le moment qui doit convaincre

*Ouvrir le cas défavorable répété. Montrer successivement la recommandation, les contributions, les pistes de réexamen et l’enregistrement. Laisser quelques secondes de lecture à chaque étape.*

> Ici, la recommandation est défavorable à la demande dans sa forme actuelle.
>
> Regardez ce qui accompagne le résultat : les éléments qui ont pesé favorablement ou défavorablement dans le calcul. L’agent peut comprendre comment le modèle a construit son score.
>
> SOLIDA examine la capacité issue des flux, la stabilité de cette capacité et son adéquation avec l’échéancier. L’épargne apporte un historique de liquidité ; la garantie est traitée séparément de la probabilité de remboursement. L’agent examine ces pistes de réexamen avec Afi, selon sa situation. Ce sont des points à retravailler, pas la promesse d’un futur accord.
>
> La fiche montrée aujourd’hui valide le mécanisme d’explication d’un modèle additif. Les coefficients du modèle synthétique actuel ne constituent pas une politique de crédit ; ils seront affinés après validation sur des données réelles autorisées.
>
> L’agent peut enregistrer la recommandation examinée. SOLIDA en conserve la trace et les versions utilisées. La décision finale de crédit reste dans le processus de l’institution.
>
> C’est là que nous voulons faire la différence : donner à l’agent les moyens de justifier son analyse, et au sociétaire les moyens de comprendre la suite.

*Jean-Paul enregistre. Montrer la trace ou la fiche si elle s’ouvre dans le temps prévu. Ne réciter aucun score numérique mémorisé : seul le résultat réellement affiché fait foi.*

### 4:10–4:40 — Gédéon — Expliquer la technologie sans perdre la salle

> Nous utilisons l’EBM de la bibliothèque ouverte InterpretML, un modèle dont le calcul est décomposable.[S3] Notre apport est de l’intégrer au parcours de crédit des SFD, avec les règles de réexamen et la traçabilité.
>
> Les rôles sont contrôlés côté serveur. L’accès à la source est en lecture seule.
>
> Les données de cette démonstration sont synthétiques, conformément aux règles du concours. Le modèle devra ensuite être évalué sur des données réelles autorisées.

### 4:40–5:20 — Charlie — Rendre le déploiement crédible

*Slide 3. Montrer seulement « Aujourd’hui » et « Pilote ».*

> Pour être utile, SOLIDA doit pouvoir rejoindre le quotidien d’une caisse.
>
> Aujourd’hui, le connecteur PostgreSQL fonctionne avec notre système simulé. Le pilote devra adapter cette liaison au système de l’institution et vérifier la qualité des données.
>
> L’application peut être hébergée sur l’infrastructure du réseau, sans carte graphique dédiée. Les autres connecteurs et le fonctionnement d’une agence durablement isolée restent des étapes à valider.
>
> Nous proposons de commencer dans deux agences, avec un responsable risque et un référent informatique.

### 5:20–6:10 — Charlie — Donner une valeur et un coût compréhensibles

*Slide 4. Afficher distinctement « Hypothèses de pilote ».*

> Premier bénéfice à mesurer : le temps consacré à l’analyse et à sa justification. À titre d’illustration, dix minutes économisées sur vingt dossiers représentent trois heures vingt de travail. C’est une hypothèse à tester, pas un résultat déjà obtenu.
>
> Pour deux agences et 90 jours, notre enveloppe de services est de 3,5 millions de francs CFA, si une infrastructure adaptée est disponible. Elle couvre l’intégration, l’évaluation, la formation et l’accompagnement. Ce budget reste à confirmer après diagnostic.
>
> Notre modèle économique proposé : une intégration initiale, puis un contrat de support. Aucun prélèvement par crédit, aucune revente de données.

### 6:10–7:05 — Jean-Paul — Passer de la démonstration à une ambition mesurable

*Slide 5. Trois preuves attendues : temps, qualité de l’évaluation, utilité pour les agents.*

> Le réseau CIF représente plus de 5,7 millions de sociétaires à fin 2025.[S2] Notre ambition est de construire une aide à la décision qui puisse servir cette échelle. Notre preuve commence dans deux agences.
>
> Pendant le pilote, nous comparerons SOLIDA à la pratique actuelle : le temps nécessaire, la qualité de l’évaluation du risque et l’utilité des explications pour les agents.
>
> Nous vérifierons aussi les écarts entre profils. Un modèle explicable doit encore faire la preuve de sa fiabilité et de son équité.
>
> En 90 jours, nous pouvons évaluer l’intégration et l’usage. Mesurer une baisse durable des impayés demandera davantage de recul.
>
> Notre demande est concrète : deux agences, un accès encadré aux données et un binôme risque-informatique pour conduire ce pilote.

### 7:05–7:30 — Junior — Laisser une image positive

*Slide 6. Revenir au regard du jury. Ralentir sur les deux dernières phrases.*

> Revenons à Afi. Elle mérite une réponse qu’elle puisse comprendre. L’agent mérite un outil qu’il puisse expliquer. L’institution mérite une décision qu’elle puisse retracer.
>
> Avec SOLIDA, nous voulons faire grandir la confiance autour de chaque décision de crédit.
>
> Donnez-nous deux agences pour commencer. Merci.

### 7:30–8:00 — Marge de sécurité

Aucun contenu supplémentaire. La marge absorbe les transitions et les clics. Une question du jury ne se traite pas au milieu de la démo sauf demande explicite de sa part.

## 2. Conducteur et supports

### Six slides, une démonstration

| Support | Message principal | Éléments à afficher |
|---|---|---|
| 1 — Afi | « Comprendre la réponse. Préserver la confiance. » | Une demande de crédit ; en pied, statistique BCEAO datée et périmètre de l’échantillon. |
| 2 — SOLIDA et les 72 heures | « Comprendre. Expliquer. Accompagner. » | Avant : interface agence sans modèle. Pendant les 72 h : modèle construit et entraîné, intégration, parcours sociétaire. |
| Démo | « Une demande. Deux points de vue. » | Portail sociétaire, puis la même demande affectée automatiquement côté agent. Badge visible « Données synthétiques ». |
| 3 — Déploiement | « Commencer dans deux agences » | Aujourd’hui : PostgreSQL / système simulé. Pilote : adaptation au SI, données autorisées, essais de connectivité. |
| 4 — Valeur et budget | « Mesurer le bénéfice, maîtriser le coût » | Hypothèse : 10 min × 20 dossiers = 3 h 20. Services : 3,5 M FCFA avec infrastructure adaptée, à confirmer. Intégration + support. |
| 5 — Pilote | « 90 jours pour éprouver l’intégration et l’usage » | Temps d’analyse ; évaluation du risque sur historique exploitable ; utilité pour les agents. Demande : 2 agences + binôme risque/SI. |
| 6 — Conclusion | « Une décision comprise. Une confiance préservée. » | SOLIDA ; les quatre prénoms, accompagnés des fonctions réellement exercées. |

Ajouter des références courtes et lisibles sur les slides concernées. Mettre les URL complètes en notes ou sur un support de référence. L’EBM/InterpretML est cité oralement ; les autres bibliothèques, modèles, données publiques et outils d’IA effectivement utilisés doivent également être crédités dans le pitch et le README, selon le briefing. Une ligne de crédits visible sur le support permet de compléter l’attribution sans réciter une liste. Pour cette révision du discours : assistance rédactionnelle et recherche avec Codex. Faire correspondre les crédits de développement à l’usage réel de l’équipe.

### Ce qui a été réalisé pendant les 72 heures

**Déclaration de l’équipe recueillie le 14 septembre 2026 ; pas un audit des dates de commits.**

| À l’arrivée | Pendant les 72 heures |
|---|---|
| Interface côté agence, sans modèle de scoring | Construction et entraînement du modèle ; intégration dans l’application ; ajout de l’interface et du parcours sociétaire. |

Cette présentation répond à l’attente de contextualisation d’une solution préexistante décrite pour le Track B. Employer le libellé de track effectivement déclaré à l’organisation. Conserver une preuve courte de l’état initial et des ajouts : capture initiale, versions du code, capture finale. Ne pas attribuer une réalisation à un membre sur la seule base de son rôle au micro.

### Le détail qui change la crédibilité de la démo

**Parcours sociétaire actualisé d’après la description fournie par l’équipe après la première révision ; ces changements n’ont pas fait l’objet d’une nouvelle exécution de l’application.**

1. Accueil à l’identité de la caisse, avec un seul appel à l’action : « Faire une demande ».
2. Saisie du numéro de compte, puis vérification par le montant du dernier dépôt. Ne pas présenter cette information comme un secret que « lui seul connaît » ni ce mécanisme comme une garantie absolue d’identité. En cas d’erreur, message de reprise ou orientation vers l’agence et champ vidé.
3. Reconnaissance par le prénom. Conserver le prénom réellement affiché pendant toute la démonstration : si le compte préparé affiche « Awa », remplacer « Afi » dans le récit et les supports avant la répétition.
4. Saisie libre du montant, entre 50 000 et 100 000 000 FCFA selon le parcours décrit. Cette plage de saisie ne constitue pas une promesse d’éligibilité ou d’accord. Les 3 millions du scénario sont une valeur de démonstration, pas le plafond du champ.
5. Choix du produit **avant** l’usage. Si le produit impose l’usage, l’écran correspondant est sauté ; sinon, choix dans la liste proposée.
6. Choix de la durée parmi les options filtrées par produit, ou saisie d’une durée dans les bornes autorisées.
7. Transition « Vérifions ensemble » pendant le calcul, sans score, tranche ni conditions affichés au sociétaire.
8. Confirmation « C’est parti ! », identique quelle que soit la recommandation calculée : transmission de la demande et reprise par l’agent. Elle ne signifie pas que le crédit est accordé.

Les points ci-dessus décrivent les écrans et comportements, pas le nombre d’étapes affiché par l’interface. Le retour, la progression visible et l’identité de la caisse soutiennent la simplicité du parcours ; il suffit de les laisser voir, sans les commenter un à un. La promesse de recontact doit correspondre à l’organisation du suivi par l’agence.

Le parcours montre deux vues d’un même scénario métier, sans copie ni préparation intermédiaire : Afi est une sociétaire réelle du jeu de démonstration, déjà suivie par un agent, et sa nouvelle demande s’affecte directement à cet agent (mécanisme vérifié en direct, de bout en bout, le 15 septembre 2026).

Le code distingue deux mécanismes d’affectation, tous deux vérifiés : un sociétaire déjà suivi par un agent voit sa demande affectée directement à cet agent habituel ; un nouveau sociétaire, sans historique, passe par la file d’attente du superviseur. La démo montre le premier cas avec Afi ; le second reste disponible pour une question du jury.

### Répétition et secours

1. Répéter deux fois avec le projecteur, les mêmes comptes et le même cas ; viser 7 min 30 s au maximum.
2. Vérifier avant la scène le résultat défavorable, les facteurs, l’affectation automatique et l’ouverture de la trace. Le score « 459/850 » du texte initial n’est pas confirmé par une exécution dans cette révision.
3. Garder la pile locale prête et les comptes authentifiés ; ne pas dépendre du Wi-Fi de la salle. Vérifier séparément le fonctionnement sur les terminaux visés.
4. En cas de blocage de plus de cinq secondes : « Nous poursuivons avec l’enregistrement local de cette démonstration. » Passer à la vidéo préparée. Elle est un secours, pas un remplacement planifié de l’obligation de démonstration en direct.
5. Si le temps manque, enlever l’exemple des dix minutes et raccourcir les détails d’infrastructure. Préserver le résultat de démo, le bilan des 72 heures et la demande finale.

## 3. Chiffres corrigés et justification des changements

### Données externes vérifiées

| Sujet | Valeur et périmètre corrects | Usage dans le pitch |
|---|---|---|
| Togo, BCEAO au 31/12/2025 | Échantillon de **59 IMF**, sur 70 recensées : **373,4962 Md FCFA** d’encours ; **29,5459 Md FCFA** de créances en souffrance ; taux de dégradation **7,9 %**. [S1] | Arrondi oral « près de 30 milliards », avec date et échantillon. Ce n’est ni le seul portefeuille CIF/FUCEC, ni une perte définitive, ni une perte annuelle. |
| Réseau CIF au 31/12/2025 | **5 737 164 sociétaires** (« clients » dans le libellé du rapport), **508,026 Md FCFA** d’encours de crédit, **603,530 Md FCFA** d’épargne. Rapport annuel 2025, p. 46. [S2] | Garder ce chiffre à l’oral pour donner l’échelle humaine, en disant « sociétaires ». Les encours restent en référence. Six réseaux dans cinq pays ; ces sociétaires ne sont pas tous emprunteurs ni tous utilisateurs futurs de SOLIDA. |
| Date des chiffres CIF | Situation fin 2025 ; article publié le 7 juillet 2026 et rapport annoncé le 16 juillet 2026. [S2] | Ne pas présenter ces chiffres comme une situation observée en juillet 2026. |

Le calcul « 0,1 % de 508,026 milliards = 508,026 millions » est arithmétiquement correct. Il a été retiré du discours parce qu’il ne démontre aucun gain attribuable à SOLIDA. Une variation de créances en souffrance ne se transforme pas automatiquement en économie, résultat net ou retour sur investissement.

### Budget : hypothèses explicites, pas faux prix certifiés

Le budget de services du document initial est cohérent arithmétiquement :

| Poste | Jours-personnes indicatifs | Montant à 100 000 FCFA/jour-personne |
|---|---:|---:|
| Cartographie et qualité des données | 5 | 500 000 FCFA |
| Adaptateur source et sécurisation | 8 | 800 000 FCFA |
| Calibration, évaluation temporelle et contrôles d’équité | 9 | 900 000 FCFA |
| Déploiement, sauvegarde et supervision | 5 | 500 000 FCFA |
| Formation et accompagnement de deux agences | 3 | 300 000 FCFA |
| Sous-total | **30** | **3 000 000 FCFA** |
| Marge opérationnelle indicative | — | 500 000 FCFA |
| **Enveloppe de services** | — | **3 500 000 FCFA** |

**Statut : hypothèse interne de cadrage.** Trente jours-personnes peuvent être répartis sur 90 jours calendaires ; ce ne sont pas 90 jours de travail facturés. Le tarif journalier n’est pas un prix de marché établi par une source externe. Le devis devra préciser notamment les taxes, déplacements, efforts demandés au personnel de la CIF et limites de l’accompagnement.

- Un matériel nouveau ajouterait **3 à 4 M FCFA selon l’hypothèse initiale**, soit **6,5 à 7,5 M FCFA** au total. Cette fourchette ne devient pas un devis local du fait qu’un serveur américain a un prix public. La garder en réserve, hors du discours principal.
- Le support proposé à **100 000–250 000 FCFA/mois/réseau** équivaut à **1,2–3 M FCFA/an/réseau**. C’est une hypothèse commerciale à tester, pas un contrat accepté ni une rentabilité démontrée. Définir les agences couvertes, les horaires de support, les interventions et les recalibrations incluses.
- Éviter de présenter 16 Go de RAM ou une configuration de production comme un besoin validé : le volume, la concurrence, les sauvegardes et les essais de charge doivent le déterminer. Une mesure de mémoire au repos ne prouve pas la capacité en exploitation.

**Repères publics actualisés, uniquement pour comparaison :**

| Référence | Vérification du 14 septembre 2026 | Limite |
|---|---|---|
| AWS Lightsail Linux/Unix avec IPv4 publique | 4 vCPU, 16 Go RAM, 320 Go SSD : **84 USD/mois**. [S4] | Pas un coût complet de pilote, ni une recommandation d’hébergement pour la CIF. |
| Conversion indicative | Cours vendeur BCEAO pour transferts : **571,25 FCFA/USD** ; 84 USD = **47 985 FCFA/mois**, soit **575 820 FCFA/an**. [S5] | Hors frais de change et frais bancaires. Le cours de change manuel n’est pas le bon repère pour justifier une facture internationale dématérialisée. La page de cours évolue. |
| HPE MicroServer Gen11 | Configuration 4 cœurs, 32 Go, un HDD de 4 To : **3 928 USD**, soit **2 243 870 FCFA** au même cours. [S6] | Hors taxes, transport et adaptation locale. Un disque dur unique n’est ni un SSD ni un stockage en miroir. Le prix initial de 2 182 USD n’a pas été retrouvé et n’est pas conservé. |

L’exemple **10 minutes × 20 dossiers = 200 minutes = 3 h 20** est une illustration interne. Il ne présume ni du volume quotidien réel, ni d’un temps initial mesuré. Un gain de temps doit être évalué à qualité d’analyse au moins comparable.

## 4. Un pilote défendable devant des spécialistes du crédit

**Proposition à négocier avec la CIF, et non engagement déjà obtenu.** Le périmètre est la préparation et l’évaluation d’une aide à la décision ; les décisions de crédit suivent le processus autorisé de l’institution.

| Période indicative | Travail proposé | Preuve attendue |
|---|---|---|
| Jours 1–15 | Autorisations, disponibilité et qualité des données, dates utilisables, diagnostic SI et observation de la pratique actuelle | Périmètre autorisé ; données exploitables ou blocages explicités ; mesure initiale du temps et du travail de l’agent |
| Jours 16–45 | Adaptation du connecteur et évaluation sur historique exploitable, avec séparation chronologique | Comparaison à une référence simple et à la pratique actuelle quand elle est observable ; calibration ; écarts entre segments |
| Jours 46–75 | Usage accompagné selon un protocole approuvé, éventuellement en observation sans effet sur les décisions | Temps total, compréhension des explications, pertinence des pistes de réexamen, erreurs et incidents |
| Jours 76–90 | Revue commune risque/SI/agents | Décision documentée : poursuivre, corriger ou suspendre ; budget et suivi nécessaires |

Définir les seuils de succès avec le responsable risque **avant** l’évaluation, sans inventer aujourd’hui une réduction d’impayés ou une précision cible. Si l’historique n’est pas exploitable, l’évaluation statistique attendra : le calendrier seul ne crée pas la preuve.

La baisse des défauts sur les nouveaux prêts peut nécessiter un suivi au-delà des 90 jours. La taille et la maturité de l’échantillon comptent. L’explication du score ne prouve pas que les actions proposées causent une baisse du risque.

## 5. Est-ce le genre de pitch qui peut gagner ?

**Avis éditorial : oui, SOLIDA possède une proposition crédible pour viser la première place. Le texte initial la rendait trop technique et parfois trop défensive. La version révisée rend l’utilité plus facile à voir. Cela ne permet pas de prédire le classement.**

L’évaluation ci-dessous porte sur le discours, les règles fournies et quelques vérifications documentaires et de code. Elle ne remplace pas l’observation d’une démo ni la comparaison avec les autres équipes.

### Lecture selon la grille réellement fournie

| Critère officiel | Poids | Appréciation du pitch révisé | Ce qui fera la différence devant le jury |
|---|---:|---|---|
| Pertinence et adéquation | 30 % | **Point fort.** Problème de crédit clairement situé dans le travail de l’agent et la relation sociétaire. | Montrer que les explications et pistes de réexamen répondent aux besoins exprimés par les spécialistes métier. |
| Originalité et innovation | 20 % | **Crédible mais à défendre.** L’EBM existe déjà ; la contextualisation et le parcours constituent l’apport de l’équipe. | Rendre visible le passage de l’interface initiale au modèle intégré et au parcours sociétaire. Éviter d’appeler « innovation » une simple liste de fonctionnalités. |
| Faisabilité technique | 20 % | **Prometteuse, encore conditionnée à la démo.** Les mécanismes ciblés sont présents dans le code, mais l’application n’a pas été exécutée pour cette révision. | Une démo lisible et stable ; honnêteté sur l’affectation ; preuve sur terminal visé et connectivité limitée. |
| Impact pour les SFD CIF | 15 % | **Mieux cadré, encore hypothétique.** Le budget et la méthode sont explicites, aucun gain terrain n’est établi. | Une mesure réelle de temps ou un retour métier précis, correctement attribué, aurait plus de poids qu’un grand montant régional. |
| Qualité du pitch | 10 % | **Structure plus nette.** Une histoire, une démonstration, une preuve des 72 h, un coût et une demande. | Le rythme réel, les pauses, la lisibilité du projecteur et les réponses courtes. |
| Composition et complémentarité | 5 % | **Plusieurs membres visibles.** Leurs compétences effectives ne sont pas documentées ici. | Afficher des rôles exacts et laisser chacun répondre dans son domaine. Quatre prises de parole ne prouvent pas à elles seules la complémentarité. |

**Pas de note globale artificielle ni de probabilité de victoire.** Le briefing fourni attribue 10 % au pitch et 5 % à l’équipe : il faut utiliser cette grille à six critères, pas recycler une ancienne estimation fondée sur une autre répartition. [D1, D2]

### Les choix qui renforcent le discours

1. **Un bénéfice humain dès le début.** Afi donne un visage au sujet, sans être présentée comme un témoignage sociétaire réel.
2. **Une démonstration qui porte le message.** Expliquer une réponse difficile montre une utilité au-delà du score ; il faut toutefois conserver l’ambition d’accompagner le financement, pas laisser l’image d’une machine à refuser.
3. **Un avant/après des 72 heures.** L’équipe a apporté un moteur et un parcours, pas seulement présenté une interface existante.
4. **Une ambition régionale avec une première étape précise.** Deux agences et un protocole sont une demande que le jury peut comprendre et discuter.
5. **Une conclusion tournée vers la confiance.** « Nous apporterons la preuve ou nous arrêterons » avait une qualité de rigueur mais terminait sur l’arrêt. La décision de poursuivre ou suspendre reste dans le protocole ; la scène se termine sur l’utilité du projet.

### Ce qui reste le plus susceptible de coûter des points

- Un cas agent préparé présenté comme la demande venant d’être envoyée. Le texte corrige ce point ; une vraie continuité démontrée serait encore plus forte.
- Un discours qui dit « hors ligne » alors qu’il ne montre qu’une reprise d’envoi après une coupure brève. Le calcul sans accès à la source et le relais d’agence ne sont pas prouvés par cette file.
- L’absence d’un bénéfice métier observé. Une estimation est admise par le guide ; elle demeure moins probante qu’une mesure réelle bien définie.
- Une déclaration des 72 heures qui ne correspondrait pas au dépôt ou à l’état initial présenté. Conserver les preuves de version ; la déclaration de l’équipe n’a pas été auditée historiquement ici.
- Des pistes de réexamen récitées sans rapport avec le cas affiché. Ne montrer que les facteurs et règles effectivement visibles.

Les explications du texte initial sur la psychologie de la persuasion ont été retirées. Des travaux sur la mémoire, l’apprentissage ou les investisseurs ne constituent pas une démonstration qu’un pitch gagnera ce hackathon. Ici, les choix éditoriaux sont des recommandations, appuyées d’abord sur les attentes explicites du concours.

## 6. Questions difficiles — réponses à préparer

### « Votre modèle est-il déjà validé sur nos sociétaires ? »

« Non. Le concours demande des données synthétiques. Nous montrons un prototype intégré ; sa validité sur vos sociétaires devra être évaluée sur un historique autorisé, avec des données postérieures à celles de l’entraînement. »

### « Que prouvez-vous réellement aujourd’hui ? »

« Une demande peut être enregistrée, affectée automatiquement à l’agent habituel du sociétaire, et examinée avec une recommandation, ses contributions et sa trace. Elle ne prouve pas encore une réduction d’impayés. »

### « Qu’avez-vous apporté pendant les 72 heures ? »

« Nous avions l’interface agence, sans modèle. Nous avons construit et entraîné le modèle, intégré son calcul et ajouté le parcours sociétaire. Nous pouvons montrer l’état initial et les versions correspondantes. »

*La dernière phrase suppose que ces éléments sont effectivement prêts à présenter.*

### « Pourquoi votre outil ferait-il mieux qu’un agent ou une règle simple ? »

« C’est précisément la comparaison à mener. Notre hypothèse est qu’un calcul cohérent, ses explications et sa traçabilité peuvent aider l’agent. Nous devons mesurer le bénéfice supplémentaire face à la pratique actuelle et à une référence simple. »

### « Comment avez-vous construit vos données et votre cible ? »

« Nous utilisons des données synthétiques. La cible documentée distingue notamment les crédits présentant une échéance à au moins 30 jours de retard. Nous documentons les cas exclus et séparons les périodes d’entraînement et d’évaluation. Le pilote devra remplacer nos hypothèses par les dates et définitions validées avec l’institution. »

*Détail pour le répondant : la model card SOCLE définit une cible positive à partir de 30 jours de retard, négative jusqu’à 14 jours ; les cas 15–29 jours et les cas non matures sont exclus. La date de déblocage sert encore de référence faute de date de demande. Ce n’est pas une validation d’une « probabilité de défaut dans les 30 prochains jours ». Préparer les volumes du jeu effectivement utilisé dans le modèle de démonstration, sans recycler ceux d’une autre version.*

### « Comment traitez-vous les biais ? »

« Nous avons audité les relations apprises par le modèle et identifié des effets directs sur la zone géographique ou d’autres attributs personnels qui ne devraient jamais peser sur une probabilité de défaut ; nous avons engagé leur correction dans le générateur de données. Le contrôle par segment reste systématique. L’absence d’historique sur les crédits refusés est aussi une limite connue. Nous ne déclarons pas le système exempt de biais. »

### « L’explication garantit-elle que le conseil est bon ? »

« Elle permet de comprendre le calcul. Les pistes de réexamen viennent de règles distinctes ; leur pertinence doit être examinée avec l’agent. Modifier un facteur ne garantit ni l’accord ni le remboursement. »

### « Votre modèle enrichi améliore-t-il les résultats ? »

« Nous n’avons pas de gain solidement établi à annoncer. Sur le petit sous-échantillon de groupe documenté, les intervalles d’incertitude ne permettent pas de conclure. Son intérêt devra être réévalué sur des données adaptées. »

### « Et si Internet tombe ? »

« Une file locale permet de retenter une demande après une coupure brève. Cela suppose notamment une session encore valide. Nous ne présentons pas ce mécanisme comme un scoring autonome d’agence durablement déconnectée. »

### « Une institution comme la CIF a des données réparties sur plusieurs systèmes différents (MySQL, PostgreSQL, Oracle...) sans identifiant commun garanti : comment SOLIDA s'y connecterait ? »

« Un connecteur par système ne sait pas, seul, si deux lignes désignent la même personne. SOLIDA construirait d'abord un index d'identité auditable, à partir d'identifiants vérifiés et d'attributs normalisés ; les rapprochements incertains passeraient en revue humaine, jamais fusionnés automatiquement. Ensuite seulement, des adaptateurs en lecture seule calculeraient localement les variables datées nécessaires au score. Si l'identité ou une source n'est pas résolue, le système le signale plutôt que d'additionner des données douteuses. »

### « Vos données sortent-elles du réseau ? Êtes-vous homologués ? »

« Un hébergement dans l’infrastructure du réseau est possible. Les flux, les accès et les conditions d’exploitation devront être examinés dans le pilote. Nous ne revendiquons aucune homologation ni validation réglementaire de SOLIDA. »

### « Pourquoi 3,5 millions ? »

« C’est un cadrage : trente jours-personnes à cent mille francs, plus cinq cent mille francs de marge opérationnelle, avec une infrastructure adaptée disponible. Nous devons confirmer le périmètre et les coûts par diagnostic et devis. »

### « Que saurez-vous au bout de 90 jours ? »

« Si l’intégration est réalisable et l’historique exploitable, si les agents utilisent et comprennent l’outil, et ce que montrent les premières comparaisons. Une baisse durable des impayés demandera un suivi plus long. »

## 7. Sources et portée des vérifications

### Sources publiques consultées le 14 septembre 2026

**[S1] BCEAO — Principaux indicateurs des IMF de l’UMOA au 31 décembre 2025.** Tableau d’une page, daté du 7 mai 2026, ligne Togo et en-têtes de colonnes.  
[Consulter le tableau BCEAO](https://www.bceao.int/sites/default/files/2026-05/Indicateurs_au_31_d%C3%A9cembre_2025.pdf).

**[S2] CIF — Rapport annuel 2025, p. 46**, indicateurs consolidés des réseaux.  
[Consulter le rapport annuel](https://www.cif-ao.org/wp-content/uploads/rapport-annuel-cif-2025.pdf).  
Confirmation du périmètre et de la date statistique : [CIF, bilan de l’assemblée générale, article du 7 juillet 2026](https://www.cif-ao.org/cif-ao-cinq-jours-de-reflexion-de-bilan-et-dapprentissage-au-service-de-la-gouvernance-a-ouagadougou/). Les valeurs exactes sont tirées du rapport, et non extrapolées à partir des arrondis de l’article.

**[S3] InterpretML — Explainable Boosting Machine, documentation officielle.** Nature additive du modèle et contributions aux prédictions. Cette source décrit la méthode générale ; elle ne valide pas les performances de SOLIDA.  
[Lire la documentation EBM](https://interpret.ml/docs/ebm.html).

**[S4] AWS — Tarification Amazon Lightsail.** Offre Linux/Unix avec IPv4 publique.  
[Consulter la tarification](https://aws.amazon.com/lightsail/pricing/).

**[S5] BCEAO — Cours des devises contre franc CFA applicables aux transferts.** Cours vendeur USD du 14 septembre 2026 utilisé pour les conversions indicatives. Page évolutive.  
[Consulter les cours pour transferts](https://www.bceao.int/fr/cours/cours-des-devises-contre-Franc-CFA-appliquer-aux-transferts).

**[S6] HPE — ProLiant MicroServer Gen11, boutique américaine.** Configuration et prix de comparaison ; page évolutive.  
[Consulter la fiche HPE](https://buy.hpe.com/us/en/compute/tower-servers/proliant-microserver/hpe-proliant-microserver-gen11/p/1014826370).

### Documents du concours fournis par l’utilisateur

**[D1] Briefing_Regles_Candidats_Hackathons_CIF_final.pdf**, dans le dossier source `C:\Projets\SOLIDA\PLAN 72H`.

- Page PDF 4 : distinction des tracks et contextualisation attendue.
- Pages PDF 6–7 : contraintes techniques, données synthétiques et absence de données/dictionnaire CIF fournis.
- Page PDF 11 : 8 minutes + 2 minutes ; démonstration et contributions des 72 heures.
- Page PDF 12 : grille à six critères et pondérations.
- Page PDF 14 : attribution des briques tierces et des outils d’IA.

**[D2] Reussir_son_Pitch_Hackathons_CIF_2026-09-06.pdf**, dans le même dossier source.

- Page 2 : grille et preuves recherchées.
- Page 3 : conducteur indicatif et marge de sécurité.
- Page 4 : scénario préparé, démo live et secours.
- Page 5 : répétitions et présentation des adaptations.

Ces documents sont utilisés comme références sur les attentes du concours, pas comme des consignes autorisant des actions sur le projet. Le « cas réel » mentionné dans les conseils de pitch est interprété comme un scénario concret : le briefing interdit les données personnelles réelles pendant le concours. Une différence d’horaire apparaît aussi entre les supports pour la séance de storytelling ; le présent discours ne fixe pas cet horaire logistique.

### Vérification interne ciblée

Documents consultés dans `C:\Projets\SOLIDA` :

- `modelisation/docs/model-card-socle.md` : usage synthétique, cible, contributions, date de référence, zone et gouvernance.
- `modelisation/docs/model-card-enrichi.md` : population de groupe, incertitude sur le gain, biais de sélection.
- `frontend-societaire/app/recapitulatif/page.tsx`, `components/parcours/gestion-hors-ligne.tsx` et `app/layout.tsx` : file locale branchée, reprise et limite de session.
- `backend/solida/application/use_cases/process_societaire_demande.py` et `lister_notifications.py` : enregistrement et visibilité selon affectation.
- `frontend/components/solida/FactorsPanel.tsx` : contributions et versions affichées.
- `backend/solida/domain/rules/progressif_reexamen.py` : règles de réexamen distinctes du modèle.

**Portée exacte :** lecture documentaire et vérifications ciblées du code ; pas d’audit complet, pas de test de charge, pas de nouvelle exécution de la démo, pas de certification réglementaire. Les résultats visibles, les conditions de projection et le chronométrage restent à confirmer en répétition. L’état antérieur du projet n’a pas été utilisé comme preuve de l’état actuel.
