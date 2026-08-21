/**
 * Garantit un temps d'affichage minimal pour un état de chargement, succès comme
 * échec : sans ça, une action qui finit avant `minMs` produit un flash trop bref,
 * perçu comme un glitch plutôt qu'un retour visuel utile.
 */
export async function withMinDuration<T>(promise: Promise<T>, minMs = 400): Promise<T> {
  const start = Date.now();
  const settle = async (): Promise<void> => {
    const elapsed = Date.now() - start;
    if (elapsed < minMs) {
      await new Promise((resolve) => setTimeout(resolve, minMs - elapsed));
    }
  };
  try {
    const result = await promise;
    await settle();
    return result;
  } catch (error) {
    await settle();
    throw error;
  }
}
