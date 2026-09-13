import type { Metadata, Viewport } from "next";
import { Toaster } from "@/components/ui/sonner";
import { GestionHorsLigne } from "@/components/parcours/gestion-hors-ligne";
import { DemandeProvider } from "@/lib/demande-context";
import { ibmPlexMono, ibmPlexSans, sourceSerif4 } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ma demande — SOLIDA",
  description: "Faire une demande de crédit auprès de votre caisse, en quelques étapes.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr">
      <body
        className={`${ibmPlexSans.variable} ${ibmPlexMono.variable} ${sourceSerif4.variable} min-h-dvh font-sans antialiased`}
      >
        <DemandeProvider>{children}</DemandeProvider>
        <GestionHorsLigne />
        <Toaster />
      </body>
    </html>
  );
}
