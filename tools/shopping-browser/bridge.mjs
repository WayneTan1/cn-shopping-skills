/**
 * Local shopping browser bridge: start Playwright MCP, call its tools, or normalize
 * observed offers through Price Pilot. Inputs are CLI arguments and JSON files;
 * outputs are JSON on stdout. Starts a loopback-only process and an independent
 * persistent Edge profile; never imports another browser's cookies.
 * Usage: node bridge.mjs start | tools | call browser_snapshot | compare offers.json
 * Errors exit nonzero. Browser mutations are never retried by this bridge.
 * Updated: 2026-11-03.
 * Copyright: Zhenyu Guo, zhenyu.guo.cn@outlook.com
 * School of Electronic and Communication Engineering, Guangzhou University
 */
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { spawn, execFile } from 'node:child_process';
import { openSync, closeSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import os from 'node:os';
import { promisify } from 'node:util';

const PROJECT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ENDPOINT = 'http://127.0.0.1:8931/mcp';
const RUNTIME_DIR = path.join(PROJECT_DIR, 'runtime');
const PROFILE_DIR = path.join(os.homedir(), '.codex', 'shopping-browser-profile');
const runFile = promisify(execFile);

/**
 * Call the persistent local session host. Inputs: route, optional JSON payload.
 * Output: parsed response. Side effects: loopback HTTP and requested browser work.
 * Non-success HTTP status throws without retry. Example: await sessionRequest('/tools');
 */
export async function sessionRequest(route, payload) {
  const response = await fetch('http://127.0.0.1:8932' + route, {
    method: payload ? 'POST' : 'GET',
    headers: payload ? { 'Content-Type': 'application/json' } : {},
    body: payload ? JSON.stringify(payload) : undefined,
    signal: AbortSignal.timeout(100000)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(result));
  return result;
}

/**
 * Ensure the persistent session host is running after the official server starts.
 * Input: none. Output: identity. Side effects: launches a hidden local Node host.
 * A foreign service on the port or failed startup throws. Example: await startSessionHost();
 */
export async function startSessionHost() {
  try {
    const health = await sessionRequest('/health');
    if (health.name !== 'shopping-session-host') throw new Error('Port 8932 has a different service');
    return health;
  } catch (error) {
    if (String(error.message).includes('different service')) throw error;
  }
  await mkdir(RUNTIME_DIR, { recursive: true });
  const logFd = openSync(path.join(RUNTIME_DIR, 'session-host.log'), 'a');
  const child = spawn(process.execPath, [path.join(PROJECT_DIR, 'session-host.mjs')], {
    cwd: PROJECT_DIR, detached: true, windowsHide: true, stdio: ['ignore', logFd, logFd]
  });
  closeSync(logFd);
  child.unref();
  await writeFile(path.join(RUNTIME_DIR, 'session-host.json'), JSON.stringify({ pid: child.pid }));
  for (let attempt = 0; attempt < 20; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 300));
    try { return await sessionRequest('/health'); } catch {}
  }
  throw new Error('Session host failed; inspect runtime/session-host.log');
}

/**
 * Connect to the local official Playwright MCP server and verify its identity.
 * Input: none. Output: initialized Client. Side effects: loopback HTTP only.
 * Throws on unreachable or unexpected server; caller must close the client.
 * Example: const client = await connectClient();
 */
export async function connectClient() {
  const client = new Client({ name: 'shopping-browser-bridge', version: '1.0.0' });
  try {
    await client.connect(new StreamableHTTPClientTransport(new URL(ENDPOINT)), { timeout: 4000 });
    if (!/playwright/i.test(client.getServerVersion()?.name ?? '')) {
      throw new Error('Port 8931 is occupied by a different MCP server.');
    }
    return client;
  } catch (error) {
    await client.close().catch(() => {});
    throw error;
  }
}

/**
 * Start or reuse the official server, bound to loopback with a dedicated profile.
 * Input: none. Output: server identity and paths. Side effects: creates local
 * runtime/profile directories and a detached Node process. Does not open a page.
 * Fails if a different service owns the endpoint or startup does not complete.
 * Example: await startServer();
 */
export async function startServer() {
  try {
    const client = await connectClient();
    const server = client.getServerVersion();
    await client.close();
    return { status: 'already-running', endpoint: ENDPOINT, server };
  } catch (error) {
    if (String(error.message).includes('different MCP server')) throw error;
  }
  await mkdir(RUNTIME_DIR, { recursive: true });
  await mkdir(PROFILE_DIR, { recursive: true });
  const logFd = openSync(path.join(RUNTIME_DIR, 'server.log'), 'a');
  const args = [path.join(PROJECT_DIR, 'node_modules', '@playwright', 'mcp', 'cli.js'),
    '--browser', 'msedge', '--port', '8931', '--host', '127.0.0.1',
    '--shared-browser-context', '--user-data-dir', PROFILE_DIR,
    '--output-dir', path.join(PROJECT_DIR, 'evidence'), '--ignore-roots',
    '--no-webmcp', '--redact-url-params', 'access_token,token,code,ticket,authCode'];
  const child = spawn(process.execPath, args, {
    cwd: PROJECT_DIR, detached: true, windowsHide: true, stdio: ['ignore', logFd, logFd]
  });
  closeSync(logFd);
  let startError;
  child.once('error', error => { startError = error; });
  child.unref();
  await writeFile(path.join(RUNTIME_DIR, 'server.json'), JSON.stringify({
    pid: child.pid, endpoint: ENDPOINT, profileDir: PROFILE_DIR, startedAt: new Date().toISOString()
  }, null, 2));
  for (let attempt = 0; attempt < 20; attempt++) {
    if (startError) throw startError;
    await new Promise(resolve => setTimeout(resolve, 400));
    try {
      const client = await connectClient();
      const server = client.getServerVersion();
      await client.close();
      return { status: 'started', endpoint: ENDPOINT, server, profileDir: PROFILE_DIR };
    } catch (error) {
      if (String(error.message).includes('different MCP server')) throw error;
    }
  }
  throw new Error(`Playwright MCP failed to start. Inspect ${path.join(RUNTIME_DIR, 'server.log')}`);
}

/**
 * Call one browser tool once, keeping the shared browser alive after disconnect.
 * Inputs: MCP tool name and its JSON arguments. Output: unmodified MCP result.
 * Side effects: those of the selected browser tool, possibly including cart edits.
 * Tool errors throw; an interrupted mutation must be observed before any retry.
 * Example: await callTool('browser_snapshot', {});
 */
export async function callTool(name, args = {}) {
  const result = await sessionRequest('/call', { name, arguments: args });
  if (result.isError) throw new Error(JSON.stringify(result));
  return result;
}

/**
 * Normalize browser-observed product evidence with the installed Price Pilot.
 * Input: path to its discovery JSON input. Output: parsed discovery result.
 * Side effects: a local Python subprocess only; intentionally omits --fetch so
 * authenticated cookies remain in Edge and are never sent by Price Pilot.
 * Errors retain Python's diagnostic. Example: await compareOffers('offers.json');
 */
export async function compareOffers(inputPath) {
  const python = path.resolve(PROJECT_DIR, '..', '.venv-price-pilot', 'Scripts', 'python.exe');
  const { stdout } = await runFile(python, ['-m', 'price_pilot', 'discover', '--input', path.resolve(inputPath)], {
    cwd: PROJECT_DIR, windowsHide: true, env: { ...process.env, PYTHONUTF8: '1' },
    timeout: 30000, maxBuffer: 4 * 1024 * 1024
  });
  return JSON.parse(stdout);
}

/**
 * Dispatch CLI commands and optionally save results with --output FILE.
 * Inputs: process arguments. Output: JSON on stdout. Side effects depend on the
 * command; tool arguments are read from --input FILE, not evaluated as code here.
 * Unknown commands and non-JSON input fail. Example: node bridge.mjs tools
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const inputIndex = args.indexOf('--input');
  const outputIndex = args.indexOf('--output');
  let result;
  if (command === 'start') result = { browser: await startServer(), session: await startSessionHost() };
  else if (command === 'tools') {
    result = await sessionRequest('/tools');
  } else if (command === 'call' && args[1]) {
    const input = inputIndex >= 0 ? JSON.parse(await readFile(args[inputIndex + 1], 'utf8')) : {};
    result = await callTool(args[1], input);
  } else if (command === 'compare' && args[1]) result = await compareOffers(args[1]);
  else throw new Error('Usage: bridge.mjs start | tools | call TOOL [--input JSON] | compare JSON [--output JSON]');
  const output = JSON.stringify(result, null, 2);
  if (outputIndex >= 0) await writeFile(args[outputIndex + 1], output + '\n', 'utf8');
  process.stdout.write(output + '\n');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => { process.stderr.write(error.message + '\n'); process.exitCode = 1; });
}
