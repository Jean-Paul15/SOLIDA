# Secrets et configuration

## Règle absolue

**Aucun secret dans le dépôt. Jamais. Aucune exception.**

Un secret commité est compromis, même supprimé au commit suivant : l'historique Git le conserve.
La seule réponse correcte est la rotation du secret, pas la suppression du fichier.

## Ce qui est un secret

Mots de passe de base, secret de signature JWT, clés MinIO, clés d'API, certificats, chaînes de
connexion complètes.

## Ce qui n'en est pas

Noms d'hôtes internes, ports, noms de bases, seuils métier, paramètres de scorecard. Ceux-là sont
de la configuration et **doivent** être versionnés, sinon personne ne sait avec quels seuils le
système tourne.

Distinguer les deux évite le travers inverse : chiffrer la configuration jusqu'à ce que plus
personne ne sache comment le système est réglé.

## Mise en œuvre

| Environnement | Moyen |
|---|---|
| Local | Fichier `.env`, non versionné, généré depuis `.env.example` |
| Hackathon | `.env` partagé hors Git, sur un canal privé |
| Production | Variables d'environnement injectées par l'orchestrateur, ou coffre |

`.env.example` est versionné, complet, et contient des valeurs factices explicites :

```
POSTGRES_SOLIDA_PASSWORD=REMPLACER_MOI
JWT_SECRET=REMPLACER_MOI_32_CARACTERES_MINIMUM
```

Il sert de documentation. Une variable ajoutée au code sans être ajoutée à `.env.example` cassera
l'environnement de tous les autres.

## Protection mécanique

Trois barrières successives, conformément au principe de défense en profondeur :

1. `.gitignore` bloque `.env`
2. Un hook `pre-commit` exécute **gitleaks** et refuse le commit
3. La CI exécute la même analyse sur l'historique de la branche

## Validation au démarrage

Configuration validée par Pydantic Settings au démarrage. Une variable manquante ou invalide
**empêche le démarrage**, avec un message nommant la variable.

Aucune valeur par défaut sur un secret. Un `JWT_SECRET` par défaut est la porte d'entrée classique.

## Rotation

| Secret | Fréquence | Procédure |
|---|---|---|
| JWT | Trimestrielle | Rotation avec période de recouvrement |
| Mots de passe base | Semestrielle | Changement + redémarrage |
| Clés MinIO | Semestrielle | Idem |
| En cas de fuite | Immédiate | Rotation puis analyse de l'exposition |

## Si un secret est commité

1. Considérer le secret comme compromis.
2. Le faire tourner immédiatement.
3. Ne pas se contenter de réécrire l'historique : si le dépôt a été poussé ou cloné, c'est trop
   tard.
4. Journaliser l'incident.

L'étape 2 est la seule qui compte réellement.
