/**
 * Normalize observed offers without exporting browser credentials. Inputs are
 * explicit SKU-level observations; outputs retain evidence and separate groups.
 * Writes local evidence and invokes Price Pilot without network fetching.
 * Usage: await normalizeOffers({query: 'SER0039', offers: [...]});
 * Updated: 2026-11-03.
 * Copyright: Zhenyu Guo, zhenyu.guo.cn@outlook.com
 * School of Electronic and Communication Engineering, Guangzhou University
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { compareOffers } from './bridge.mjs';

const PROJECT_DIR = path.dirname(fileURLToPath(import.meta.url));

/**
 * Validate observed offers and group only matching product/variant/quantity.
 * Inputs: an array with productKey, variantKey, title, URL, price, quantity,
 * currency, observedAt, evidence, skuConfirmed; optional landedPrice (whole requested quantity).
 * Output: validated offers plus groups sorted by comparable whole-order cost.
 * No I/O. Throws on missing evidence, invalid numbers or non-HTTP product URLs.
 * Example: groupOffers([{productKey:'SER0039',variantKey:'180deg', ...}]);
 */
export function groupOffers(offers) {
  if (!Array.isArray(offers) || !offers.length || offers.length > 100) {
    throw new Error('Provide 1–100 observed offers.');
  }
  const groups = new Map();
  for (const offer of offers) {
    for (const field of ['productKey', 'variantKey', 'title', 'url', 'currency', 'observedAt', 'evidence']) {
      if (typeof offer[field] !== 'string' || !offer[field].trim()) throw new Error(`Missing ${field}`);
    }
    if (!/^https?:$/.test(new URL(offer.url).protocol)) throw new Error('Product URL must be HTTP(S)');
    if (!Number.isFinite(Date.parse(offer.observedAt))) throw new Error('Invalid observation timestamp');
    if (!Number.isFinite(offer.price) || offer.price < 0) throw new Error('Invalid unit price');
    if (!Number.isInteger(offer.quantity) || offer.quantity < 1) throw new Error('Invalid quantity');
    if (typeof offer.skuConfirmed !== 'boolean') throw new Error('Declare whether the exact SKU was confirmed');
    if (offer.landedPrice != null && (!Number.isFinite(offer.landedPrice) || offer.landedPrice < 0)) {
      throw new Error('Invalid whole-order landed price');
    }
    const key = JSON.stringify([offer.productKey, offer.variantKey, offer.quantity, offer.currency, offer.condition ?? 'unknown']);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(offer);
  }
  return [...groups.values()].map(group => {
    const hasAllLandedPrices = group.every(offer => offer.landedPrice != null);
    const sorted = [...group].sort((a, b) => hasAllLandedPrices
      ? a.landedPrice - b.landedPrice : a.price - b.price);
    return {
      productKey: group[0].productKey, variantKey: group[0].variantKey,
      quantity: group[0].quantity, currency: group[0].currency,
      basis: hasAllLandedPrices ? 'observed_whole_order_landed_price' : 'unit_price_only_shipping_or_discounts_unverified',
      offers: sorted, skuVerified: group.every(offer => offer.skuConfirmed),
      comparisonComplete: sorted.length >= 2 && group.every(offer => offer.skuConfirmed)
    };
  });
}

/**
 * Save browser observations and pass their prices into Price Pilot normalization.
 * Input: {query, offers}; fields defined by groupOffers. Output: groups, original
 * observations, Price Pilot result and evidence path. Writes only project evidence.
 * No cookies or authenticated HTTP scraping; errors leave input evidence intact.
 * Example: await normalizeOffers({query:'servo', offers:[...]});
 */
export async function normalizeOffers({ query = '', offers }) {
  const groups = groupOffers(offers);
  const evidenceDir = path.join(PROJECT_DIR, 'evidence');
  await mkdir(evidenceDir, { recursive: true });
  const inputPath = path.join(evidenceDir, `offers-${randomUUID()}.json`);
  const payload = {
    query,
    manual_inputs: offers.map(offer => ({
      ...offer, platform: offer.platform ?? 'unknown', price: offer.price,
      landed_price: null, seller_name: offer.sellerName ?? null,
      source_type: 'browser_observation', notes_list: [offer.evidence]
    }))
  };
  await writeFile(inputPath, JSON.stringify(payload, null, 2), 'utf8');
  const pricePilot = await compareOffers(inputPath);
  const result = { capturedAt: new Date().toISOString(), groups, pricePilot, inputPath };
  const reportPath = inputPath.replace(/\.json$/, '-normalized.json');
  await writeFile(reportPath, JSON.stringify(result, null, 2), 'utf8');
  return { ...result, reportPath };
}
