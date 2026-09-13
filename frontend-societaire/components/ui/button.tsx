import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";

import { cn } from "@/lib/utils";

// Un seul gabarit de taille : "xl", pleine largeur, hauteur généreuse (section 5 de
// SOLIDA_Flux_Societaire.md — "zones de contact larges"). Pas de variante compacte :
// ce parcours n'affiche jamais plus d'une action principale par écran.
const buttonVariants = cva(
  "group/button inline-flex w-full shrink-0 cursor-pointer items-center justify-center gap-2 rounded-lg border border-transparent text-lg font-medium whitespace-nowrap transition-colors outline-none select-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-4 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:size-5 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-solida-teal-700",
        outline:
          "border-border bg-background text-foreground hover:bg-muted active:bg-neutre-200",
        ghost: "text-foreground hover:bg-muted active:bg-neutre-200",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Button({
  className,
  variant = "default",
  asChild = false,
  loading = false,
  onClick,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
    /** État transitoire (envoi en cours) : le bouton reste focusable, le clic est
     * intercepté en JS plutôt que bloqué par `disabled` — évite un saut de focus. */
    loading?: boolean;
  }) {
  const Comp = asChild ? Slot.Root : "button";

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      aria-disabled={loading || props.disabled || undefined}
      onClick={(event: React.MouseEvent<HTMLButtonElement>) => {
        if (loading) {
          event.preventDefault();
          return;
        }
        onClick?.(event);
      }}
      className={cn(
        buttonVariants({ variant, className }),
        "min-h-14 px-6 py-3",
        loading && "cursor-not-allowed opacity-60"
      )}
      {...props}
    />
  );
}

export { Button, buttonVariants };
