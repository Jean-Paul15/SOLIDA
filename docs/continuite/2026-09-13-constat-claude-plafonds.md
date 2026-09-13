# Constat Claude — plafonds par produit

Cette transcription est conservée pour que la reprise sur un autre PC garde le diagnostic qui a motivé la correction. Les montants historiques cités ne sont plus une règle métier actuelle : les décisions terrain postérieures fixent l'absence de plafond par produit et un maximum institutionnel unique de 100 000 000 FCFA.

## Symptôme constaté

La grille active ne contenait que `{"prod-individuel": 2000000}` dans `plafonds_produits`. Les quatre autres produits (`prod-salarie`, `prod-jeune`, `prod-femme-gie`, `prod-agricole`) étaient absents de la map. L'ancien validateur backend échouait donc pour ces produits.

## Historique rapporté par Claude

- Migration `c1f8e5a3d947_plafonds_produits_dans_grille.py` et versions v0.1 à v1.2-production : cinq plafonds, jeune 750 000, salarié 2 000 000, agricole 1 500 000, femme GIE 1 500 000, individuel 2 000 000.
- À partir de `v-repro-1786548660` / `v0.4-doublon-test`, les versions suivantes auraient conservé seulement `prod-individuel`; la version active signalée était `v-doublon-d50d9088-suite`.

## Cause technique lue

1. `PolitiqueCredit.tsx` initialisait `productCaps` à partir des seules clés existantes de la grille.
2. `ProductsTab.tsx` affichait un maximum catalogue pour une clé absente mais ne l'écrivait pas dans l'état sauvegardé.
3. Le POST de grille remplaçait intégralement la map reçue.

Une interface pouvait donc afficher une valeur plausible tout en perpétuant une map incomplète à chaque enregistrement de politique.

## Décision et correction appliquées

- Le scoring ne lit plus `plafonds_produits` et ne dépend plus d'une clé par produit.
- Il vérifie uniquement le maximum institutionnel de 100 M FCFA.
- Le montant demandé est conservé pour l'étude humaine de faisabilité. Il n'est plus réduit par le prêt précédent, un plafond primo-emprunteur ni une projection de cycle.
- Les champs/maps legacy sont conservés pour consulter les décisions anciennes sans migration destructive.
- L'onglet frontend d'édition des plafonds par produit est retiré pour ne plus représenter une règle inexistante.
- Aucune réparation de données ne réinjecte les cinq plafonds historiques : ce serait rétablir une politique remplacée.
