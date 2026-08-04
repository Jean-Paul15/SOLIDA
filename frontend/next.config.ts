import type { NextConfig } from "next";

// Le navigateur appelle toujours /api/v1/... en meme origine : cette reecriture route
// tout ce qui n'est pas deja une route Next.js locale (ex. /api/v1/sante) vers le backend
// reel, sans que le code client n'ait besoin de connaitre son adresse.
const BACKEND_INTERNAL_URL = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/v1/:path*", destination: `${BACKEND_INTERNAL_URL}/api/v1/:path*` }];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
