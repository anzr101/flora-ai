/** @type {import('next').NextConfig} */
const GATEWAY = process.env.GATEWAY_ORIGIN || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  // Proxy API calls to the FastAPI gateway so the browser stays same-origin
  // (no CORS in prod) while we develop against the live backend.
  async rewrites() {
    return [
      { source: "/gw/:path*", destination: `${GATEWAY}/:path*` },
    ];
  },
};

export default nextConfig;
