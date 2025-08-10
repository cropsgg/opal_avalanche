/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    SERVER_API_URL: process.env.SERVER_API_URL || 'http://localhost:8001',
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
}

module.exports = nextConfig
