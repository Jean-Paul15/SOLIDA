# Questionnaire suivi — modèle enrichi et moteur de décision

Ces décisions ne sont pas bloquantes pour le SOCLE, mais elles sont indispensables avant de coder le modèle enrichi ou les règles de décision qui les utilisent.

1. **GIE daté** — quelle est la date d'entrée, de sortie et de changement de rôle de chaque membre ? Une appartenance doit-elle être active à la demande ou historique ?
2. **Crédit de groupe** — quel événement définit un incident de groupe, et à quelle date est-il visible pour une nouvelle demande individuelle ?
3. **Caution solidaire** — quelles données représentent l'engagement, son montant, son plafond et son éventuel appel ? À quelle date l'information devient-elle connue ?
4. **Garantie/nantissement** — quel montant réellement libre peut être observé avant décision ; faut-il distinguer type de garantie, valeur estimée et appel ?
5. **Signaux sectoriels** — source, granularité géographique, date de publication et retard de disponibilité. Sans date d'observation, le signal est exclu.
6. **Objet divisible/indivisible** — fournir une table de référence, versionnée par le métier, associant chaque objet existant à `divisible` ou `indivisible`, et la règle opérationnelle attendue. Aucun classement ne sera inféré depuis le libellé.
7. **Décision** — définir les coûts relatifs d'un défaut, d'un bon refusé et d'une revue manuelle, les seuils à considérer, et l'autorité qui les valide.
8. **Dérive et réentraînement** — fréquence d'arrivée des retours, période d'observation de 90 jours, seuils d'alerte et responsable de la validation d'une nouvelle version.
