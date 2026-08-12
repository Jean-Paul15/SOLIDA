import Link from "next/link";

export default function AccesRefuse() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <h1 className="font-serif-title text-xl font-semibold text-neutre-950">Accès refusé</h1>
      <p className="max-w-md text-sm text-neutre-500">
        Vous n&rsquo;avez pas les droits nécessaires pour accéder à cette page. Si vous pensez
        qu&rsquo;il s&rsquo;agit d&rsquo;une erreur, contactez votre superviseur.
      </p>
      <Link href="/" className="text-sm text-solida-teal-900 underline">
        Retour à la recherche
      </Link>
    </div>
  );
}
