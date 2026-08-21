interface SectionProps {
  title: string;
  description: string;
}

export function Section({ title, description }: SectionProps) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] font-medium tracking-wide text-neutre-500 uppercase">
        {title}
      </span>
      <p className="text-xs text-neutre-500">{description}</p>
    </div>
  );
}
