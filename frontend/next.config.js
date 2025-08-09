/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  experimental: {
    serverActions: true,
  },
  env: {
    // Load environment variables from the root .env file
    ...require('dotenv').config({ path: path.resolve(__dirname, '../.env') }).parsed,
  },
};

module.exports = nextConfig;
