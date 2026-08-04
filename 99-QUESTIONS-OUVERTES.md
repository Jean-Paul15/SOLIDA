# Questions ouvertes

**À lire en premier.** Ce dossier contient beaucoup de décisions prises par défaut, faute de
réponses. Chacune peut être remise en cause. Les questions ci-dessous sont classées par impact
décroissant : les premières changent l'architecture, les dernières changent un détail.

Les décisions par défaut sont appliquées dans le reste du dossier tant qu'une réponse n'arrive pas.

---

## Bloquantes — répondre avant d'écrire une ligne de code

### Q1. Combien êtes-vous et qui fait quoi ?
Toute la répartition de `10-PLAN-HACKATHON/02` en dépend, et le périmètre P1 change selon
l'effectif. À trois, il faut abandonner des choses dès maintenant.
**Décision par défaut :** cinq personnes, un rôle chacun.

### Q2. Quelles compétences réelles dans l'équipe ?
Précisément : qui écrit du Python en production, qui connaît React et TypeScript, qui a déjà
entraîné un modèle, qui a déjà écrit une API, qui connaît PostgreSQL. La stack proposée suppose ces
compétences réparties.
**Décision par défaut :** la stack est retenue telle quelle. Si personne n'est à l'aise en
TypeScript, il faut le dire maintenant, pas le jour 2.

### Q3. Confirmez-vous la Thématique 02 ?
Tout ce dossier est écrit pour le scoring microcrédit. Un basculement vers la Thématique 01 rendrait
caduque une grande partie du contenu.
**Décision par défaut :** Thématique 02, définitive.

### Q4. Avez-vous réellement accès à un praticien de microfinance ?
Le schéma de données attend une validation. Sans elle, on génère sur des hypothèses, ce qui reste
faisable mais fragilise la défense devant le jury.
**Décision par défaut :** on génère sur nos hypothèses et on le dit franchement au jury.

### Q5. Le nom SOLIDA est-il retenu ?
Il apparaît partout. Le changer plus tard coûte peu si on le fait maintenant, beaucoup si on le
fait le jour 2.
**Décision par défaut :** SOLIDA.

---

## Structurantes — répondre avant le hackathon

### Q6. Un ou plusieurs dépôts ? — Tranché (ADR-018)
Monorepo unique (`SOLIDA`), pas quatre dépôts séparés. Voir
`00-CONTEXTE/04-journal-de-decisions.md`.

### Q7. Le dossier de principes non versionné, vraiment ? — Tranché (ADR-018)
`SOLIDA-FOUNDATION` (les dossiers numérotés) est versionné dans le monorepo, avec le code. Voir
`00-CONTEXTE/04-journal-de-decisions.md`.

### Q8. Quelle profondeur d'historique dans CORE-SIM ?
Cinq ans est proposé. Trois ans suffiraient et allégeraient la génération ; sept ans donneraient
plus de cycles par sociétaire.
**Décision par défaut :** cinq ans, 25 000 sociétaires.

### Q9. Faut-il vraiment l'authentification en P0 ?
Elle coûte une journée. On pourrait s'en passer pour la démonstration et la mentionner. Mais un
jury financier pose souvent la question du contrôle d'accès, et « on ne l'a pas faite » est une
mauvaise réponse.
**Décision par défaut :** authentification en P0, version minimale, sans limitation de débit.

### Q10. L'écran du groupe de caution est-il prioritaire ?
C'est une liste simple (pas une visualisation de réseau, voir ADR-016), donc plus rapide à
produire qu'avant. Reste P1 : elle ne sert que le segment GIE, minoritaire.
**Décision par défaut :** P1, développé le jour 2 après-midi, abandonné en cas de retard.

### Q11. MLflow dès le jour 1 ou pas du tout ?
Installer MLflow coûte une heure et fait gagner du temps dès que trois personnes entraînent en
parallèle. Ne pas l'installer, c'est retrouver le jour 2 au soir quatorze modèles sans savoir
lequel est lequel.
**Décision par défaut :** installé avant le hackathon, utilisé dès le premier entraînement.

---

## Métier — à poser au praticien

### Q12. Quel seuil définit la créance en souffrance chez vous ?
90 jours retenu par défaut. Différent pour l'agricole ?

### Q13. Les demandes refusées sont-elles conservées dans le système ?
Change la stratégie de modélisation et la mesure du délai d'instruction.

### Q14. Existe-t-il une note qualitative de l'agent après visite terrain ?
Si oui, sous quel format ? C'est probablement la variable la plus prédictive existante, et elle
n'est pas dans notre schéma.

### Q15. Les cautions individuelles hors groupe sont-elles enregistrées de façon structurée ?
Si elles ne vivent que sur le dossier papier, la couche solidaire se limite au segment de groupe (GIE).

### Q16. Trace-t-on qu'une garantie a été appelée, ou qu'un remboursement a été payé par le garant ?
C'est la variable la plus parlante de toute la couche solidaire (« déjà secouru »). Si elle
n'existe pas, il faut la reconstruire indirectement, avec une fiabilité moindre.

### Q17. Quelle est la part réelle de primo-emprunteurs, et la part de crédit de groupe vs individuel ?
45 % de primo et ~25 % de sociétaires emprunteurs retenus par défaut (bilan social FUCEC-TOGO).
Ces deux chiffres déterminent respectivement l'importance du mode socle et la taille de la couche
solidaire — c'est la question la plus structurante de toutes celles à poser au praticien.

### Q18. Un sociétaire peut-il appartenir à plusieurs groupes simultanément ?
Le générateur l'interdit par défaut. À confirmer.

### Q19. Existe-t-il une centrale des risques accessible aux SFD togolais ?
Écartée par défaut. Si elle existe et est accessible, c'est une source de données majeure.

---

## Techniques — arbitrables plus tard

### Q20. Le score doit-il être borné à 300–850 ?
Convention empruntée au scoring anglo-saxon. Une échelle 0–1000 serait plus intuitive pour un
public francophone.
**Décision par défaut :** 300–850, convention bancaire reconnaissable.

### Q21. Les points chiffrés doivent-ils figurer sur la fiche remise au sociétaire ?
Écartés par défaut, jugés plus utiles à l'agent qu'au demandeur. Deux variantes de fiche prévues.

### Q22. La police à empattement sur les titres est-elle activée ?
`Source Serif 4` proposée en option. Elle donne un caractère institutionnel, mais ajoute une
famille à charger.
**Décision par défaut :** désactivée. IBM Plex Sans partout.

### Q23. Mode sombre ?
Écarté. Les agences sont éclairées, l'interface est dense.
**Décision par défaut :** clair uniquement.

### Q24. Faut-il une page publique de présentation du projet ?
Ce serait le seul endroit où Aceternity UI aurait un sens. Coûte une demi-journée.
**Décision par défaut :** non.

---

## Ce que je recommande de trancher dès maintenant

Par ordre : **Q1, Q2, Q3, Q5, Q7**. Les cinq tiennent en dix minutes de discussion d'équipe et
débloquent tout le reste.

Q4 et Q12 à Q19 dépendent du praticien : envoyez-lui le fichier
`02-DONNEES/00-schema-a-valider-par-praticien.md` sans attendre, sa section 11 est faite pour ça.
