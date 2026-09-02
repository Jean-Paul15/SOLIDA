import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Section } from "@/components/solida/Section";
import { scoreDepuisProbabilite } from "@/lib/scorecard";

type PolicyPreset = "prudent" | "equilibre" | "expansion";

interface ThresholdsTabProps {
  preset: PolicyPreset;
  onPresetChange: (value: PolicyPreset) => void;
  margin: number;
  onMarginChange: (value: number) => void;
  lgd: number;
  onLgdChange: (value: number) => void;
  approvalMultiplier: number;
  onApprovalMultiplierChange: (value: number) => void;
  reviewMultiplier: number;
  onReviewMultiplierChange: (value: number) => void;
  threshold: number;
  scorecardParameters: { pdo: number; scoreReference: number; oddsReference: number };
  onSave: () => void;
  isSaving: boolean;
  canEdit: boolean;
}

export function ThresholdsTab({
  preset,
  onPresetChange,
  margin,
  onMarginChange,
  lgd,
  onLgdChange,
  approvalMultiplier,
  onApprovalMultiplierChange,
  reviewMultiplier,
  onReviewMultiplierChange,
  threshold,
  scorecardParameters,
  onSave,
  isSaving,
  canEdit,
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
          ).map(([value, label]) => {
            const isDisabled = value !== "equilibre";
            const button = (
              <Button
                key={value}
                type="button"
                variant={preset === value ? "default" : "outline"}
                size="sm"
                disabled={isDisabled}
                onClick={() => onPresetChange(value)}
              >
                {label}
              </Button>
            );
            if (!isDisabled) return button;
            return (
              <Tooltip key={value}>
                <TooltipTrigger asChild>
                  <span>{button}</span>
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
              <span className="font-mono text-neutre-950">{(margin * 100).toFixed(0)}%</span>
            </div>
            <Slider
              value={[margin]}
              onValueChange={([value]) => onMarginChange(value)}
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
              onValueChange={([value]) => onLgdChange(value)}
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
              <span className="font-mono text-neutre-950">× {approvalMultiplier.toFixed(2)}</span>
            </div>
            <Slider
              value={[approvalMultiplier]}
              onValueChange={([value]) => onApprovalMultiplierChange(value)}
              min={0.3}
              max={0.95}
              step={0.05}
            />
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex justify-between text-sm">
              <Label>Multiplicateur zone d&rsquo;examen</Label>
              <span className="font-mono text-neutre-950">× {reviewMultiplier.toFixed(2)}</span>
            </div>
            <Slider
              value={[reviewMultiplier]}
              onValueChange={([value]) => onReviewMultiplierChange(value)}
              min={1.2}
              max={2.5}
              step={0.05}
            />
          </div>

          <Button
            onClick={onSave}
            loading={isSaving}
            disabled={!canEdit}
            className="self-start gap-1.5"
          >
            {isSaving && <Loader2 className="size-4 animate-spin" />}
            {isSaving ? "Enregistrement…" : "Enregistrer la grille"}
          </Button>
          {!canEdit && (
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
                <div className="font-mono text-neutre-950">{(threshold * 100).toFixed(1)}%</div>
              </div>
              <div>
                <span className="text-neutre-500">Score accord</span>
                <div className="font-mono text-neutre-950">
                  {scoreDepuisProbabilite(threshold * approvalMultiplier, scorecardParameters)}
                </div>
              </div>
              <div>
                <span className="text-neutre-500">Score refus</span>
                <div className="font-mono text-neutre-950">
                  {scoreDepuisProbabilite(threshold * reviewMultiplier, scorecardParameters)}
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
