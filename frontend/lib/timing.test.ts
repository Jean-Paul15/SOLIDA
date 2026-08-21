import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { withMinDuration } from "./timing";

describe("withMinDuration", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("attend le minimum si la promesse se résout plus vite", async () => {
    const resultat = withMinDuration(Promise.resolve("ok"), 400);
    await vi.advanceTimersByTimeAsync(399);
    let regle = false;
    resultat.then(() => {
      regle = true;
    });
    await Promise.resolve();
    expect(regle).toBe(false);

    await vi.advanceTimersByTimeAsync(1);
    expect(await resultat).toBe("ok");
  });

  it("n'ajoute pas d'attente si la promesse dépasse déjà le minimum", async () => {
    const promesseLente = new Promise<string>((resolve) => setTimeout(() => resolve("ok"), 500));
    const resultat = withMinDuration(promesseLente, 400);
    await vi.advanceTimersByTimeAsync(500);
    expect(await resultat).toBe("ok");
  });

  it("respecte le minimum même en cas d'échec", async () => {
    const resultat = withMinDuration(Promise.reject(new Error("echec")), 400).catch(
      (e: Error) => e.message
    );
    await vi.advanceTimersByTimeAsync(400);
    expect(await resultat).toBe("echec");
  });
});
