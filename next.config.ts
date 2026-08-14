import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["node-telegram-bot-api"],
  experimental: {
    serverActions: {
      bodySizeLimit: "50mb",
    },
  },
};

export default nextConfig;
