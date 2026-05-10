export interface Env {
    API_VERSION: string;
    API_KEY: string;
    ADMIN_EMAIL: string;
    EDGE_KV: KVNamespace;
}

export default {
    async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
        const url = new URL(request.url);

        // Root endpoint
        if (url.pathname === '/') {
            return new Response('Welcome to the Edge API!', { headers: { 'Content-Type': 'text/plain' } });
        }

        // Health check endpoint
        if (url.pathname === '/health') {
            console.log(`Health check performed at ${new Date().toISOString()}`);
            return new Response('OK', { status: 200 });
        }

        // Deployment info endpoint
        if (url.pathname === '/info') {
            const deploymentInfo = {
                deploymentId: env.API_VERSION,
                timestamp: new Date().toISOString(),
                region: 'Global Edge',
            };
            return new Response(JSON.stringify(deploymentInfo, null, 2), { headers: { 'Content-Type': 'application/json' } });
        }

        // Edge metadata endpoint
        if (url.pathname === '/edge') {
            const edgeMetadata = {
                colo: request.cf?.colo,
                country: request.cf?.country,
                city: request.cf?.city,
                httpProtocol: request.cf?.httpProtocol,
                tlsVersion: request.cf?.tlsVersion,
                asn: request.cf?.asn,
            };
            return new Response(JSON.stringify(edgeMetadata, null, 2), { headers: { 'Content-Type': 'application/json' } });
        }

        // Config and secrets endpoint
        if (url.pathname === '/config') {
            const config = {
                apiVersion: env.API_VERSION,
                adminEmail: env.ADMIN_EMAIL,
                apiKeyLoaded: env.API_KEY ? 'true' : 'false', // Не показываем сам ключ!
            };
            return new Response(JSON.stringify(config, null, 2), { headers: { 'Content-Type': 'application/json' } });
        }

        // KV storage endpoint
        const kvMatch = url.pathname.match(/^\/kv\/([\w-]+)$/);
        if (kvMatch) {
            const key = kvMatch[1];
            if (request.method === 'POST') {
                const value = await request.text();
                await env.EDGE_KV.put(key, value);
                return new Response(`Stored value for key: ${key}`, { status: 201 });
            }
            if (request.method === 'GET') {
                const value = await env.EDGE_KV.get(key);
                if (value === null) {
                    return new Response('Not Found', { status: 404 });
                }
                return new Response(value, { headers: { 'Content-Type': 'text/plain' } });
            }
            return new Response('Method Not Allowed', { status: 405 });
        }

        // 404 Not Found for other paths
        return new Response('Not Found', { status: 404 });
    },
};