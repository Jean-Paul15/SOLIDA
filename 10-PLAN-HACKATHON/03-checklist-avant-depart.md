# Checklist avant le hackathon

À boucler avant le 10 septembre au soir.

## Administratif — avant le 23 août

- [ ] Équipe constituée (3 à 5 membres, tous résidant au Togo)
- [ ] Fiche de présentation de l'équipe rédigée
- [ ] Note de présentation finalisée (5 pages)
- [ ] CV synthétiques de chaque membre
- [ ] Pièce d'identité du chef d'équipe
- [ ] Thématique 02 indiquée explicitement
- [ ] Pays / ville : Togo / Lomé
- [ ] Dossier envoyé à `digicoop-wa@cif-ao.org` **avant le 23 août 23h59 GMT+0**
- [ ] Accusé de réception obtenu ou relance effectuée
- [ ] Questions de clarification envoyées avant le 9 août
- [ ] Réponses de la CIF du 12 août consultées et intégrées

## Validation métier

- [ ] Schéma de données soumis à un praticien de microfinance
- [ ] Retour obtenu et intégré au YAML du générateur
- [ ] Seuil de défaut confirmé (90 jours ou autre)
- [ ] Part réelle de primo-emprunteurs confirmée
- [ ] Existence d'une note qualitative d'agent vérifiée

## Technique — environnement

- [ ] Chaque membre a Docker fonctionnel
- [ ] Chaque membre lance la pile complète en local
- [ ] Chaque membre a accès aux quatre dépôts
- [ ] Hooks Git installés chez tous
- [ ] `.env` partagé sur un canal privé
- [ ] CI verte sur `main`
- [ ] `make demo` testé sur au moins deux machines différentes

## Technique — préparé en amont

- [ ] Générateur CORE-SIM complet et paramétré
- [ ] Contrôles de cohérence passants
- [ ] Squelettes des quatre dépôts
- [ ] Contrats d'interface implémentés avec doublures
- [ ] Règles métier pures écrites et testées à 100 %
- [ ] Design system et primitives front
- [ ] Écran de recherche fonctionnel avec données factices
- [ ] Compose complet
- [ ] Migrations initiales

## Matériel

- [ ] Ordinateur portable par personne, batterie testée
- [ ] Chargeurs
- [ ] Multiprise (les prises manquent toujours)
- [ ] Adaptateur HDMI et VGA pour la projection
- [ ] Partage de connexion mobile en secours
- [ ] Clé USB avec l'environnement complet et les images Docker exportées
- [ ] Disque externe pour les sauvegardes
- [ ] Souris (trois jours au pavé tactile est une mauvaise idée)

**La clé USB avec les images Docker est le point le plus important de cette liste.** Si le Wi-Fi de
l'événement est saturé le matin du jour 1, télécharger les images et les dépendances prendra deux
heures que personne n'a. `docker save` la veille du départ.

## Contenu

- [ ] Jeu de cas de démonstration préparé, incluant : dossier excellent, dossier limite,
      primo-emprunteur, dossier avec groupe dégradé, dossier à données incomplètes
- [ ] Trame du pitch écrite
- [ ] Slides préparées (10 maximum)
- [ ] Réponses préparées aux questions attendues (voir `04-plan-de-demo-et-pitch.md`)

## Logistique

- [ ] Lieu et horaires confirmés
- [ ] Trajet de chacun organisé pour 08h00, trois jours de suite
- [ ] Numéros de téléphone échangés
- [ ] Groupe de discussion créé
- [ ] Personne référente désignée en cas d'imprévu

## La veille

- [ ] `git pull` sur tous les dépôts, CI verte
- [ ] `make demo` rejoué de zéro sur une machine propre
- [ ] Sauvegarde complète sur disque externe
- [ ] Images Docker exportées sur la clé USB
- [ ] Batteries chargées
- [ ] Nuit correcte — trois jours à 12 heures commencent par une nuit de sommeil
