/**
 * Local end-to-end browser test: choose a SKU, add one item and verify the cart.
 * Uses a separate headless Edge context and a local fixture, never the user's
 * shopping profile. Inputs: installed Playwright MCP. Output: Node test result.
 * Opens an ephemeral loopback server and closes it after testing.
 * Usage: node --test test-browser.mjs
 * Updated: 2026-11-03.
 * Copyright: Zhenyu Guo, zhenyu.guo.cn@outlook.com
 * School of Electronic and Communication Engineering, Guangzhou University
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

/** Serve a fixed local test store; inputs are HTTP request/response, output is
 * HTML. Changes only the fixture DOM when clicked, with no real marketplace I/O. */
function serveFixture(request, response) {
  response.setHeader('Content-Type', 'text/html; charset=utf-8');
  response.end(`<!doctype html><html lang="zh"><title>LOCAL TEST STORE</title>
    <h1>测试音频板</h1><label>规格<select id="sku"><option value="battery">带电池</option><option value="no-battery">无电池</option></select></label>
    <label>数量<input id="qty" value="1" type="number"></label>
    <button id="add">加入购物车</button><p role="status" id="cart">购物车空</p>
    <script>let count=0;document.getElementById('add').onclick=()=>{count+=Number(document.getElementById('qty').value);document.getElementById('cart').textContent='SKU='+document.getElementById('sku').value+';数量='+count;};</script></html>`);
}

/** Combine MCP text blocks. Input: tool result. Output: plain text, no I/O. */
function toolText(result) { return result.content.filter(item => item.type === 'text').map(item => item.text).join('\n'); }

test('real MCP browser selects the intended SKU and verifies exactly one cart addition on a local fixture', async () => {
  const fixture = http.createServer(serveFixture);
  await new Promise(resolve => fixture.listen(0, '127.0.0.1', resolve));
  const client = new Client({ name: 'shopping-browser-e2e', version: '1' });
  try {
    await client.connect(new StdioClientTransport({ command: process.execPath, args: [
      fileURLToPath(new URL('./node_modules/@playwright/mcp/cli.js', import.meta.url)),
      '--browser', 'msedge', '--headless', '--isolated', '--ignore-roots', '--no-webmcp'
    ], stderr: 'pipe' }));
    await client.callTool({ name: 'browser_navigate', arguments: { url: `http://127.0.0.1:${fixture.address().port}/` } });
    let snapshot = toolText(await client.callTool({ name: 'browser_snapshot', arguments: {} }));
    const skuTarget = snapshot.match(/combobox[^\n]*\[ref=([^\]]+)\]/)?.[1];
    assert.ok(skuTarget, snapshot);
    const selection = await client.callTool({ name: 'browser_select_option', arguments: { target: skuTarget, values: ['no-battery'] } });
    assert.ok(!selection.isError, toolText(selection));
    snapshot = toolText(await client.callTool({ name: 'browser_snapshot', arguments: {} }));
    assert.match(snapshot, /无电池.*\[selected\]/);
    const addTarget = snapshot.match(/button "加入购物车"[^\n]*\[ref=([^\]]+)\]/)?.[1];
    assert.ok(addTarget, snapshot);
    const addition = await client.callTool({ name: 'browser_click', arguments: { target: addTarget, element: 'local fixture add button' } });
    assert.ok(!addition.isError, toolText(addition));
    const verification = toolText(await client.callTool({ name: 'browser_snapshot', arguments: {} }));
    assert.match(verification, /SKU=no-battery;数量=1/);
  } finally {
    await client.close();
    await new Promise(resolve => fixture.close(resolve));
  }
});
