interface RubriqueProps {
  titre: string;
  description: string;
}

export function Rubrique({ titre, description }: RubriqueProps) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] font-medium tracking-wide text-neutre-500 uppercase">
        {titre}
      </span>
      <p className="text-xs text-neutre-500">{description}</p>
    </div>
  );
}
