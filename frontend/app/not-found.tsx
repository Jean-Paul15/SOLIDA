import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <h1 className="font-serif-title text-xl font-semibold text-neutre-950">Page introuvable</h1>
      <p className="text-sm text-neutre-500">Cette ressource n&rsquo;existe pas ou plus.</p>
      <Link href="/" className="text-sm text-solida-teal-900 underline">
        Retour à la recherche
      </Link>
    </div>
  );
}
