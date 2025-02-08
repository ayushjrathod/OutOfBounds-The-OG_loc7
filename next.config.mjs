/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["res.cloudinary.com", "assets.aceternity.com"],
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
