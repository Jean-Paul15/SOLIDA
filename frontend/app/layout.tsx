import type { Metadata } from "next";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ibmPlexMono, ibmPlexSans, sourceSerif4 } from "./fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "SOLIDA — Scoring d'octroi",
  description:
    "Scoring d'octroi de microcrédit fondé sur la trajectoire d'épargne et le comportement de remboursement des sociétaires.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr">
      <body
        className={`${ibmPlexSans.variable} ${ibmPlexMono.variable} ${sourceSerif4.variable} font-sans antialiased`}
      >
        <TooltipProvider>{children}</TooltipProvider>
        <Toaster />
      </body>
    </html>
  );
}
