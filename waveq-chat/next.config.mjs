/** @type {import('next').NextConfig} */
const nextConfig = {
    experimental: {
        serverComponentsExternalPackages: ['nanoid'],
    },
    // Allow serving static files from uploads directory
    async rewrites() {
        return [
            {
                source: '/uploads/:path*',
                destination: '/api/serve/:path*',
            },
        ];
    },
};

export default nextConfig;
