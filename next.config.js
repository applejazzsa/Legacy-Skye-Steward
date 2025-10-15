/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // You can re-enable these once you're ready to enforce them
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },

  // Add image domains here if you load external images
  images: {
    remotePatterns: [
      // { protocol: 'https', hostname: 'example.com' }
    ],
  },
};

module.exports = nextConfig;