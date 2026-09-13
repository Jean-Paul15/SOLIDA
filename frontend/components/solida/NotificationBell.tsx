"use client";

import { Bell } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchNotifications } from "@/lib/services/notifications";

const INTERVALLE_RAFRAICHISSEMENT_MS = 45_000;

export function NotificationBell() {
  const [total, setTotal] = useState<number | null>(null);

  useEffect(() => {
    let actif = true;
    function rafraichir() {
      fetchNotifications(1)
        .then((page) => {
          if (actif) setTotal(page.total);
        })
        .catch(() => {
          // Silencieux : le prochain intervalle retentera.
        });
    }
    rafraichir();
    const intervalle = setInterval(rafraichir, INTERVALLE_RAFRAICHISSEMENT_MS);
    return () => {
      actif = false;
      clearInterval(intervalle);
    };
  }, []);

  return (
    <Link href="/notifications" className="relative flex size-8 items-center justify-center">
      <Bell className="size-4 text-neutre-700" />
      {total !== null && total > 0 && (
        <span className="absolute top-0 right-0 flex size-4 items-center justify-center rounded-full bg-decision-refus text-[10px] font-medium text-blanc">
          {total > 9 ? "9+" : total}
        </span>
      )}
    </Link>
  );
}
