/**
 * Exercise SKU grouping, real Price Pilot normalization and the registered MCP
 * protocol. Inputs: installed project dependencies. Output: Node test results.
 * Writes local test evidence; never edits a real shopping cart or reads login data.
 * Usage: node --test test-workflow.mjs
 * Updated: 2026-11-03.
 * Copyright: Zhenyu Guo, zhenyu.guo.cn@outlook.com
 * School of Electronic and Communication Engineering, Guangzhou University
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { groupOffers, normalizeOffers } from './workflow.mjs';

const offer = {
  productKey: 'SER0039', variantKey: '180-degree', title: 'TEST ONLY servo',
  url: 'https://example.com/test-product', price: 28, quantity: 1, currency: 'CNY',
  observedAt: '2026-11-03T00:00:00Z', evidence: 'synthetic test fixture; not a real quote', condition: 'new', skuConfirmed: true
};

test('different SKU, quantity, condition and currency are not price-ranked together', () => {
  const groups = groupOffers([offer, { ...offer, variantKey: 'continuous', price: 5 },
    { ...offer, quantity: 2 }, { ...offer, currency: 'USD' }, { ...offer, condition: 'used' }]);
  assert.equal(groups.length, 5);
  assert.ok(groups.every(group => group.comparisonComplete === false));
});

test('landed price wins only when every same-SKU offer has a verified landed total', () => {
  const result = groupOffers([{ ...offer, price: 20, landedPrice: 35 }, { ...offer, price: 28, landedPrice: 28 }])[0];
  assert.equal(result.offers[0].price, 28);
  assert.equal(result.basis, 'observed_whole_order_landed_price');
  assert.equal(groupOffers([offer, { ...offer, landedPrice: 30 }])[0].basis, 'unit_price_only_shipping_or_discounts_unverified');
});

test('invalid or missing price evidence fails before comparison', () => {
  assert.throws(() => groupOffers([{ ...offer, price: NaN }]));
  assert.throws(() => groupOffers([{ ...offer, evidence: '' }]));
  assert.throws(() => groupOffers([{ ...offer, url: 'file:///private.txt' }]));
});

test('two search-result prices do not count as completed SKU comparison', () => {
  const group = groupOffers([{ ...offer, skuConfirmed: false }, { ...offer, price: 58.4, skuConfirmed: false }])[0];
  assert.equal(group.comparisonComplete, false);
  assert.equal(group.skuVerified, false);
});

test('Price Pilot receives a numeric price under ten and preserves independent SKU evidence', async () => {
  const result = await normalizeOffers({ query: 'synthetic regression', offers: [{ ...offer, price: 2.5 }] });
  assert.equal(result.pricePilot.normalized_candidates[0].price, 2.5);
  assert.equal(result.groups[0].offers[0].variantKey, '180-degree');
});

test('MCP starts, lists browser and comparison tools, and normalizes a real request', async () => {
  const client = new Client({ name: 'shopping-protocol-test', version: '1' });
  const transport = new StdioClientTransport({ command: process.execPath,
    args: [fileURLToPath(new URL('./server.mjs', import.meta.url))], stderr: 'pipe' });
  try {
    await client.connect(transport);
    const tools = (await client.listTools()).tools;
    assert.ok(tools.some(tool => tool.name === 'browser_click'));
    assert.ok(tools.some(tool => tool.name === 'shopping_compare'));
    assert.ok(!tools.some(tool => tool.name === 'browser_network_request'));
    const result = await client.callTool({ name: 'shopping_compare', arguments: { offers: [offer] } });
    assert.ok(!result.isError);
    assert.equal(JSON.parse(result.content[0].text).groups[0].offers[0].price, 28);
  } finally { await client.close(); }
});
