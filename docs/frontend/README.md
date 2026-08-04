# Documentation du frontend SOLIDA

Cette documentation décrit ce qui est réellement construit, au fur et à mesure de l'avancement.
Un agent qui reprend ce travail doit pouvoir lire ces fichiers plutôt que parcourir tout le code
pour reconstituer ce qui s'est passé.

Convention : chaque fichier correspond à une étape de construction, numérotée dans l'ordre où elle
a été réalisée.

| Fichier | Contenu |
|---|---|
| `00-vue-ensemble.md` | Ce qu'est SOLIDA, ce que ce socle frontend démontre |
| `01-design-system.md` | Jetons Tailwind v4 implémentés, polices, comment en ajouter un |
| `02-contrats-et-mocks.md` | Types TypeScript, fixtures, routes `/api/v1` factices |
| `03-calcul-echeance.md` | Méthode actuarielle retenue pour l'échéance de crédit, sources |
| `04-ecrans.md` | Écrans livrés, un par un, avec leur route et leur état |
| `05-securite.md` | Session, cookies, en-têtes — mesures appliquées |
| `06-docker-et-dev.md` | Comment lancer, construire, tester — tout sous Docker |
| `07-hooks-et-ci.md` | Hooks Git et pipeline CI mis en place |
