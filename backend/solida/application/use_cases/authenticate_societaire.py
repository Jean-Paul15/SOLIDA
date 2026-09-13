from dataclasses import dataclass
from datetime import date

from solida.domain.entities.societaire import Societaire
from solida.domain.errors import IdentiteSocietaireInvalide
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.rules.jeton_societaire import generer_jeton

HISTORIQUE_MOUVEMENTS_JOURS = 730


@dataclass(frozen=True)
class ResultatAuthentification:
    jeton_session: str
    prenom: str


@dataclass(frozen=True)
class AuthenticateSocietaire:
    core_sim_reader: CoreSimReader
    secret: str

    def execute(self, numero_membre: str, montant_dernier_depot: int) -> ResultatAuthentification:
        societaire = self.core_sim_reader.charger_societaire_par_numero_membre(numero_membre)
        if societaire is None:
            raise IdentiteSocietaireInvalide("Numéro de compte ou montant incorrect.")

        depuis = date.today().replace(year=date.today().year - 2)
        mouvements = self.core_sim_reader.charger_mouvements_epargne(
            societaire.societaire_id, depuis
        )
        # Uniquement les dépôts que le sociétaire a lui-même effectués : un
        # transfert_nantie/restitution_nantie porte aussi sens=depot mais est un
        # mouvement technique lié à un crédit, pas une action volontaire connue du
        # sociétaire — l'utiliser comme secret d'authentification serait trompeur.
        depots = [m for m in mouvements if m.type_operation == "depot"]
        dernier_depot = depots[-1] if depots else None

        if dernier_depot is None or dernier_depot.montant != montant_dernier_depot:
            raise IdentiteSocietaireInvalide("Numéro de compte ou montant incorrect.")

        jeton = generer_jeton(self.secret, societaire.societaire_id)
        return ResultatAuthentification(jeton_session=jeton, prenom=_prenom(societaire))


def _prenom(societaire: Societaire) -> str:
    return societaire.nom_complet.split(" ")[0]
