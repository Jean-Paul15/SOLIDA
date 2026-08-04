export function formaterMontant(fcfa: number): string {
  const nombre = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(
    Math.round(fcfa)
  );
  return `${nombre} FCFA`;
}
