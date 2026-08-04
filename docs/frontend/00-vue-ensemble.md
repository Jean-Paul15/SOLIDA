# SOLIDA — le crédit qui se justifie, pas qui se subit

SOLIDA transforme la décision d'octroi de microcrédit en un geste simple pour l'agent et une
décision compréhensible pour le sociétaire : un nom tapé, un dossier complet à l'écran, un score
entier accompagné de ses raisons — jamais une boîte noire. La trajectoire d'épargne du sociétaire,
construite mois après mois depuis son adhésion, devient le signal central, disponible pour
l'ensemble du portefeuille dès la première demande — pas seulement pour ceux qui ont déjà emprunté.

Ce socle frontend démontre le parcours complet — connexion, recherche, dossier à 360°, demande,
résultat de scoring — sur des données factices, avant que le modèle et l'API réels n'existent. Le
même contrat d'interface qui alimente ces écrans aujourd'hui alimentera plus tard le vrai backend,
sans qu'un seul composant n'ait à changer.

## État de cette passe

Construit : parcours P0 (connexion → recherche → dossier → demande → résultat), design system
complet, contrats et implémentations factices, conteneurisation Docker de bout en bout.

Volontairement hors périmètre à ce stade : modèle de scoring réel, backend FastAPI, bases
PostgreSQL, MinIO — voir `03-perimetre-hackathon.md` dans `SOLIDA-FOUNDATION` pour l'ordre de
priorité complet.
