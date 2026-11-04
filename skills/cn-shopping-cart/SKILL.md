---
name: cn-shopping-cart
description: "Use the local shopping_browser MCP for Taobao/Tmall, JD and Pinduoduo price comparison, coupon discovery and verification, free coupon collection, delivery checks, access recovery, and authorized cart additions or Pinduoduo favorites. Integrates observed SKU evidence with Price Pilot; platform login or verification may require the user. Does not authorize checkout or payment."
---

# 电商比价、找券与加购收藏

Use the installed `shopping_browser` MCP and Price Pilot. Browser login stays in the dedicated Edge profile; the Codex in-app browser has separate login state.

## Connect

Prefer the native MCP tools. If they are absent from the current tool list or the service is stopped, read [runtime.md](references/runtime.md) and use its local bridge. Do not repeat the earlier claim that this environment cannot operate a browser without first trying this installed bridge.

Inspect `browser_tabs` and explicitly select the intended product tab. Tabs may include permission prompts or unrelated items. A URL supplied by ambient browser state is a candidate, not proof that the user chose that product.

Recheck the current tab URL before each action; another task or the user may change focus, and permission tabs can change tab indices. Select a freshly observed index and take a fresh snapshot when the page differs. Keep browser operations sequential within the shared session.

If the dedicated window requires login, ask the user to sign in there while completing independent work. Do not request passwords, OTPs, cookie exports or another browser's profile. Do not interact with permission dialogs or bypass verification barriers. A product page becoming readable does not prove the cart is authenticated.

## Coupons, delivery and access recovery

For best-price requests, coupon collection, or access errors, read [offers-and-access.md](references/offers-and-access.md). Expand the full relevant coupon/promotion panel; check observed shop or cart coupon entries when needed. Record discovery, claim, eligibility and application separately. Claim directly relevant free coupons within the authorized shopping workflow, then recheck the exact SKU and requested basket. Recover through normal platform entry points and bounded retries; login and verification barriers require the user.

Use the user's delivery region. A page's default region is not evidence of delivery or free shipping to the user. For frozen food compare net weight, pack count, cold-chain delivery and thaw protection as well as price. Do not infer the selected quantity from the product title or price from a different SKU.

## Collect comparable evidence

Preserve the user's model, variant, quantity, condition, budget and previous authorization. For each candidate, inspect current page content and selected options. A `skuId` query parameter alone does not prove that SKU is selected.

Use fresh snapshots and observed `target` references for actions; version 0.0.84 uses `target`, not the older `ref` input field. Do not invent selectors or reuse a reference after navigation. Use `browser_find` for focused inspection and DOM evaluation only when needed to read visible selected options or prices.

Record product key, canonical variant key, title, seller, product URL, observed SKU, numeric unit price, quantity, currency, observation time and evidence file. Set `skuConfirmed` false for search snippets or an unverified selected variant. `landedPrice` is the observed total for the requested quantity including delivery and discounts; leave it null until verified. Pass observations to `shopping_compare`. The tool calls Price Pilot without `--fetch`, so authenticated cookies never leave the browser. It groups only equal product/variant/quantity/currency/condition combinations and does not call search-only evidence a completed SKU comparison.

Keep coupon status, eligibility, delivery region, price discrepancies and access limitations in a separate evidence record; do not invent unsupported `shopping_compare` fields. Per-kilogram or per-500g calculations across different packs are a separate value comparison, not an identical-SKU match. Do not claim a platform-wide lowest price when other platforms are inaccessible.

Do not mix battery/no-battery kits, positional/continuous-rotation servos, or different board models. A single seller is a price reference, not completed comparison. Unknown shipping means comparison by item price only. Do not fabricate seller reputation, coupons, stock or reviews.

## Save the selected target and verify

For authorized save/add requests, continue after choosing the target: Taobao/Tmall and JD use the cart; Pinduoduo uses product favorites unless the user specifies another supported action. Read [save-target.md](references/save-target.md) before saving. Preserve authorization already given in this session; do not ask again for the same products. A comparison-only request does not authorize saving, and permission to save does not authorize checkout.

Check existing state first, perform at most one necessary mutation, then verify in the cart or through persistent favorite state. Keep the user's intended SKU and quantity in the receipt even when a platform favorite saves only the product. A timeout requires inspection before any retry. Do not add every runner-up, duplicate an existing line, or toggle an existing favorite off.

Return a short receipt with the exact target, price basis, coupon eligibility/application, save action and verification status. Use the structured fields in [save-target.md](references/save-target.md) when saving an audit artifact. Store only focused evidence with canonical product URLs; exclude account identifiers, contact details and credentials. Separate real marketplace results from skill validation or simulated tests, and disclose stages that were not exercised.
