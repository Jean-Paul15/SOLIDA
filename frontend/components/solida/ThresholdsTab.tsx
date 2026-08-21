import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Section } from "@/components/solida/Section";
import { scoreDepuisProbabilite } from "@/lib/scorecard";

type Preregl = "prudent" | "equilibre" | "expansion";

interface ThresholdsTabProps {
  preregl: Preregl;
  onChangePreregl: (valeur: Preregl) => void;
  marge: number;
  onChangeMarge: (valeur: number) => void;
  lgd: number;
  onChangeLgd: (valeur: number) => void;
  multiplicateurAccord: number;
  onChangeMultiplicateurAccord: (valeur: number) => void;
  multiplicateurExamen: number;
  onChangeMultiplicateurExamen: (valeur: number) => void;
  seuil: number;
  parametresScorecard: { pdo: number; scoreReference: number; oddsReference: number };
  enregistrer: () => void;
  enregistrementEnCours: boolean;
  autoriseAModifier: boolean;
}

export function ThresholdsTab({
  preregl,
  onChangePreregl,
  marge,
  onChangeMarge,
  lgd,
  onChangeLgd,
  multiplicateurAccord,
  onChangeMultiplicateurAccord,
  multiplicateurExamen,
  onChangeMultiplicateurExamen,
  seuil,
  parametresScorecard,
  enregistrer,
  enregistrementEnCours,
  autoriseAModifier,
}: ThresholdsTabProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <Section
          title="Préréglage de politique"
          description="Prudent et Expansion contrôlée seront activés après validation par le comité risque."
        />
        <div className="flex gap-2">
          {(
            [
              ["prudent", "Prudent"],
              ["equilibre", "Équilibré"],
              ["expansion", "Expansion contrôlée"],
            ] as const
          ).map(([valeur, libelle]) => {
            const desactive = valeur !== "equilibre";
            const bouton = (
              <Button
                key={valeur}
                type="button"
                variant={preregl === valeur ? "default" : "outline"}
                size="sm"
                disabled={desactive}
                onClick={() => onChangePreregl(valeur)}
              >
                {libelle}
              </Button>
            );
            if (!desactive) return bouton;
            return (
              <Tooltip key={valeur}>
                <TooltipTrigger asChild>
                  <span>{bouton}</span>
                </TooltipTrigger>
                <TooltipContent>
                  Bientôt disponible, après validation par le comité risque.
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-5 flex flex-col gap-5">
          <Section
            title="Matrice de coûts"
            description="Détermine le seuil économique, recalculé en direct à droite."
          />
          <div className="flex flex-col gap-2">
            <div className="flex justify-between text-sm">
              <Label>Marge nette</Label>
              <span className="font-mono text-neutre-950">{(marge * 100).toFixed(0)}%</span>
            </div>
            <Slider
              value={[marge]}
              onValueChange={([v]) => onChangeMarge(v)}
              min={0.05}
              max={0.3}
              step={0.01}
            />
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex justify-between text-sm">
              <Label>Perte en cas de défaut (LGD)</Label>
              <span className="font-mono text-neutre-950">{(lgd * 100).toFixed(0)}%</span>
            </div>
            <Slider
              value={[lgd]}
              onValueChange={([v]) => onChangeLgd(v)}
              min={0.4}
              max={0.9}
              step={0.01}
            />
          </div>

          <Separator />
          <Section
            title="Largeur des zones de la grille"
            description="Écarte accord et refus du seuil économique central."
          />

          <div className="flex flex-col gap-2">
            <div className="flex justify-between text-sm">
              <Label>Multiplicateur zone d&rsquo;accord</Label>
              <span className="font-mono text-neutre-950">× {multiplicateurAccord.toFixed(2)}</span>
            </div>
            <Slider
              value={[multiplicateurAccord]}
              onValueChange={([v]) => onChangeMultiplicateurAccord(v)}
              min={0.3}
              max={0.95}
              step={0.05}
            />
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex justify-between text-sm">
              <Label>Multiplicateur zone d&rsquo;examen</Label>
              <span className="font-mono text-neutre-950">× {multiplicateurExamen.toFixed(2)}</span>
            </div>
            <Slider
              value={[multiplicateurExamen]}
              onValueChange={([v]) => onChangeMultiplicateurExamen(v)}
              min={1.2}
              max={2.5}
              step={0.05}
            />
          </div>

          <Button
            onClick={enregistrer}
            disabled={enregistrementEnCours || !autoriseAModifier}
            className="self-start"
          >
            {enregistrementEnCours ? "Enregistrement…" : "Enregistrer la grille"}
          </Button>
          {!autoriseAModifier && (
            <p className="text-xs text-neutre-500">
              Lecture seule : la modification de la grille est réservée à la supervision. Les
              curseurs simulent l&rsquo;effet d&rsquo;un réglage sans l&rsquo;enregistrer.
            </p>
          )}
        </div>

        <div className="col-span-7 flex flex-col gap-4 rounded-lg bg-solida-teal-50 p-4">
          <Section
            title="Seuils résultants"
            description="Recalculé en direct à partir des réglages de gauche, rien n'est encore enregistré."
          />

          <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 bg-blanc p-4">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-neutre-500">Seuil économique</span>
                <div className="font-mono text-neutre-950">{(seuil * 100).toFixed(1)}%</div>
              </div>
              <div>
                <span className="text-neutre-500">Score accord</span>
                <div className="font-mono text-neutre-950">
                  {scoreDepuisProbabilite(seuil * multiplicateurAccord, parametresScorecard)}
                </div>
              </div>
              <div>
                <span className="text-neutre-500">Score refus</span>
                <div className="font-mono text-neutre-950">
                  {scoreDepuisProbabilite(seuil * multiplicateurExamen, parametresScorecard)}
                </div>
              </div>
            </div>
          </div>

          <p className="mt-auto text-xs text-neutre-500">
            Score accord et score refus sont les mêmes seuils que ceux affichés sous forme de jauge
            colorée sur l&rsquo;écran de résultat d&rsquo;un score.
          </p>
        </div>
      </div>
    </div>
  );
}
