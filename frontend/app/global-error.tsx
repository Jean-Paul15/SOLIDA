"use client";

// Explicite plutôt que de laisser Next.js générer son propre fallback interne : ce dernier
// tente d'utiliser le contexte du layout racine (TooltipProvider, PreviewProvider),
// indisponible lors du rendu d'une erreur globale, ce qui fait échouer le pré-rendu en
// production (bug Next.js 16 documenté : vercel/next.js#84994, #86178). Ce composant ne doit
// donc dépendre d'aucun provider — il remplace entièrement le layout racine, pas seulement
// son contenu.
export default function GlobalError({ reset }: { error: Error; reset: () => void }) {
  return (
    <html lang="fr">
      <body style={{ fontFamily: "sans-serif", padding: "2rem" }}>
        <h1>Une erreur inattendue est survenue</h1>
        <p>Veuillez réessayer ou recharger la page.</p>
        <button onClick={() => reset()}>Réessayer</button>
      </body>
    </html>
  );
}
