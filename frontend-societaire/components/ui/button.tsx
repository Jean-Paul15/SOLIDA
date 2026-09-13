import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";

import { cn } from "@/lib/utils";

// Un seul gabarit de taille, pleine largeur (jamais plus d'une action principale par
// écran) : compact plutôt que démesuré, mais toujours au-dessus du minimum tactile
// de 44px (Apple HIG / Material) — ni trop gros ni trop petit.
// "transition" (pas seulement transition-colors) : anime aussi active:scale, pour
// un vrai retour au toucher — pas seulement un survol qui ne veut rien dire sur
// mobile. Neutralisé automatiquement sous prefers-reduced-motion (app/globals.css).
const buttonVariants = cva(
  "group/button inline-flex w-full shrink-0 cursor-pointer items-center justify-center gap-2 rounded-lg border border-transparent text-base font-medium whitespace-nowrap transition outline-none select-none active:scale-[0.98] disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100 aria-invalid:border-destructive aria-invalid:ring-4 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-solida-teal-700 active:bg-solida-teal-800",
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
        "min-h-11 px-5 py-2.5",
        loading && "cursor-not-allowed opacity-60"
      )}
      {...props}
    />
  );
}

export { Button, buttonVariants };
