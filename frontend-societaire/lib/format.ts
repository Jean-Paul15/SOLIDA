export function formaterFcfa(valeur: number): string {
  return `${new Intl.NumberFormat("fr-FR").format(valeur)} FCFA`;
}
