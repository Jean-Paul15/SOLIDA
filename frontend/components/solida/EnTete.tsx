import Link from "next/link";

interface EnTeteProps {
  agence?: string;
  utilisateur?: string;
}

export function EnTete({ agence, utilisateur }: EnTeteProps) {
  return (
    <header className="flex h-14 items-center justify-between border-b border-neutre-200 bg-blanc px-6">
      <Link href="/" className="font-serif-title text-base font-semibold text-solida-teal-900">
        SOLIDA
      </Link>
      <div className="flex items-center gap-4 text-sm text-neutre-700">
        {agence && <span>{agence}</span>}
        {utilisateur && <span>{utilisateur}</span>}
      </div>
    </header>
  );
}
