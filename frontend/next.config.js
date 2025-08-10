/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/index.html',
        permanent: false,
      },
    ];
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  experimental: {
    serverActions: true,
  },
  optimizeFonts: false,
  env: {
    // Load environment variables from the root .env file
    ...require('dotenv').config({ path: path.resolve(__dirname, '../.env') }).parsed,
  },
};

module.exports = nextConfig;
