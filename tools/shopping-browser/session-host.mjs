/**
 * Keep one official Playwright MCP session alive and expose a loopback bridge.
 * Input: POST /call with {name,arguments}; GET /tools or /health. Output: JSON.
 * Side effects: the requested browser action, once. Holds the browser session so
 * separate CLI calls retain tabs and login UI. No automatic mutation retries.
 * Usage: node session-host.mjs (normally launched by bridge.mjs start).
 * Updated: 2026-11-03.
 * Copyright: Zhenyu Guo, zhenyu.guo.cn@outlook.com
 * School of Electronic and Communication Engineering, Guangzhou University
 */
import http from 'node:http';
import { connectClient } from './bridge.mjs';

const client = await connectClient();
let isBusy = false;

/**
 * Handle one local bridge request without overlapping browser mutations.
 * Inputs: Node HTTP request/response. Output: JSON response; browser state may
 * change for /call. Limits body size and accepts only the configured loopback host.
 * Errors return 400/500 without retry; a busy session returns 409.
 * Example: POST /call {"name":"browser_snapshot","arguments":{}}
 */
async function handleRequest(request, response) {
  let ownsSession = false;
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (request.headers.host !== '127.0.0.1:8932' || request.headers.origin) {
    response.writeHead(403).end(JSON.stringify({ error: 'Local non-browser clients only' }));
    return;
  }
  try {
    if (request.method === 'GET' && request.url === '/health') {
      response.end(JSON.stringify({ name: 'shopping-session-host', version: '1.0.0', isBusy }));
      return;
    }
    if (isBusy) { response.writeHead(409).end(JSON.stringify({ error: 'Browser is busy; observe before retry' })); return; }
    isBusy = true;
    ownsSession = true;
    if (request.method === 'GET' && request.url === '/tools') {
      response.end(JSON.stringify(await client.listTools()));
      return;
    }
    if (request.method !== 'POST' || request.url !== '/call') {
      response.writeHead(404).end(JSON.stringify({ error: 'Unknown route' })); return;
    }
    let body = '';
    for await (const chunk of request) {
      body += chunk;
      if (Buffer.byteLength(body) > 1024 * 1024) throw new Error('Request exceeds 1 MB');
    }
    const payload = JSON.parse(body);
    if (typeof payload.name !== 'string') throw new Error('Tool name required');
    const result = await client.callTool(payload, undefined, { timeout: 90000 });
    response.end(JSON.stringify(result));
  } catch (error) {
    response.writeHead(500).end(JSON.stringify({ error: error.message }));
  } finally { if (ownsSession) isBusy = false; }
}

const server = http.createServer(handleRequest);
server.listen(8932, '127.0.0.1');
server.on('error', error => { process.stderr.write(error.message + '\n'); process.exitCode = 1; client.close(); });
