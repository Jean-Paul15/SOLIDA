/**
 * Habillage desktop d'un parcours pensé mobile. En dessous de `sm` (640px),
 * transparent : le contenu garde exactement le rendu plein écran déjà validé
 * (ancré en haut, compact). À partir de `sm`, le contenu est présenté comme une
 * carte centrée sur un fond neutre — sans ça, une colonne étroite ancrée en haut
 * d'un grand écran ressemble à un rendu cassé plutôt qu'à un parcours téléphone
 * volontairement contraint. Pertinent en particulier parce que la démo tournera
 * probablement sur un ordinateur portable, pas un téléphone réel.
 */
export function CadreMobile({ children }: { children: React.ReactNode }) {
  return (
    <div className="sm:flex sm:min-h-dvh sm:items-center sm:justify-center sm:bg-neutre-100 sm:px-6 sm:py-10">
      <div className="sm:max-h-[85dvh] sm:w-full sm:max-w-md sm:overflow-y-auto sm:rounded-2xl sm:border sm:border-border sm:bg-blanc sm:shadow-2">
        {children}
      </div>
    </div>
  );
}
