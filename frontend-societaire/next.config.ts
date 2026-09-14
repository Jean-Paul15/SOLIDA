import type { NextConfig } from "next";

// Même convention que frontend/next.config.ts : le navigateur appelle toujours
// /api/v1/... en même origine, cette réécriture route vers le backend réel sans que
// le code client n'ait besoin de connaître son adresse.
const BACKEND_INTERNAL_URL = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `${BACKEND_INTERNAL_URL}/api/v1/:path*` }];
  },
};

export default nextConfig;
