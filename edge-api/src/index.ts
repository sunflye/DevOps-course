export default {
    async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
        const url = new URL(request.url);

        // Root endpoint
        if (url.pathname === '/') {
            return new Response('Welcome to the Edge API!', {
                headers: { 'Content-Type': 'text/plain' },
            });
        }

        // Health check endpoint
        if (url.pathname === '/health') {
            return new Response('OK', { status: 200 });
        }

        // Deployment info endpoint
        if (url.pathname === '/info') {
            const deploymentInfo = {
                deploymentId: 'v1.0.0',
                timestamp: new Date().toISOString(),
                region: 'Global Edge',
            };
            return new Response(JSON.stringify(deploymentInfo, null, 2), {
                headers: { 'Content-Type': 'application/json' },
            });
        }

        // 404 Not Found for other paths
        return new Response('Not Found', { status: 404 });
    },
};