from pathlib import Path

import jinja2
import weasyprint

from solida.adapters.http import mappers
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.fiche import EnTeteFiche

_LIBELLE_TRANCHE = {
    "accord": "ACCORD",
    "accord_sous_condition": "ACCORD SOUS CONDITION",
    "comite_de_credit": "COMITÉ DE CRÉDIT",
    "refus": "REFUS",
}

_ENVIRONNEMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).with_name("gabarits")),
    autoescape=True,
)


class WeasyPrintFichePdfGenerator:
    """Implémente `FichePdfGenerator` : rend le même contenu que la fiche JSON/HTML du
    frontend, mis en page pour l'impression via WeasyPrint (HTML/CSS -> PDF, pas de
    navigateur headless — conforme à la contrainte de légèreté du projet)."""

    def generer(self, decision: DecisionEnregistree, entete: EnTeteFiche) -> bytes:
        fiche = mappers.fiche_vers_schema(decision, entete)
        gabarit = _ENVIRONNEMENT.get_template("fiche.html")
        html = gabarit.render(fiche=fiche, libelle_tranche=_LIBELLE_TRANCHE[fiche.resultat.tranche])
        return weasyprint.HTML(string=html).write_pdf()
