---
name: cn-shopping-compare
description: Compare products on JD, Taobao/Tmall, Pinduoduo, Xianyu and Zhuanzhuan by exact specifications, current prices, eligible coupons, delivery costs and seller evidence. Use for shopping research, lowest delivered price or best-value recommendations, including normal recovery from browser access errors. Supports new and used goods; does not authorize checkout or payment.
metadata:
  trigger_examples:
    - shopping: 比价/购物/电商/怎么买/最值/性价比/推荐/购买建议/询价
    - marketplaces: 京东/jd/淘宝/taobao/tmall/天猫/拼多多/pinduoduo/pdd/闲鱼/xianyu/goofish/转转/zhuanzhuan
  openclaw:
    homepage: https://github.com/wby1121/price-pilot
---

# CN Shopping Compare

## Overview

Use this skill to turn a shopping request into a structured, cross-platform recommendation. Integrate available listing evidence, normalize the data, score the options, and explain why the top choice wins.

## System Modules

Treat the workflow as four independent modules. Do not let an inquiry failure invalidate discovery, scoring, or decision output.

### 1. 商品发现

- Search platform listings or accept direct listing URLs.
- Extract title, price, condition, region, seller reputation, and publish time.
- Produce a comparable candidate list even if follow-up inquiry is unavailable.

### 2. 候选评分

- Score value for money.
- Score risk separately.
- Generate recommendation reasons from evidence, not only from price.

### 3. 询价助手

- Draft inquiry text first.
- Require human confirmation before sending.
- Track seller replies and structure quoted prices.

### 4. 汇总决策

- Merge discovery candidates and inquiry replies.
- Output ranked products, recommendation reasons, and direct product links.

## Workflow

### 1. Clarify the target

Extract the decision constraints before searching:

- product name and generation
- model or configuration
- new or used preference
- budget cap or target price band
- platform preference or exclusions
- risk tolerance
- must-have details such as color, storage, edition, invoice, warranty, shipping origin

Ask a follow-up only when the missing detail would materially change the recommendation. Otherwise proceed with reasonable defaults and state them.

### 2. Route each platform to the best data source

Use current data for all time-sensitive facts. Do not rely on stale memory for prices, ratings, or availability.

Prefer deterministic evidence over blind browsing:

1. direct listing links or screenshots supplied by the user
2. configured marketplace MCP servers
3. the installed persistent shopping browser with the user's existing session
4. public search pages
5. only then, broad browsing as a weak fallback

If direct browsing is blocked, use an available marketplace MCP or the installed shopping browser. Classify the failure before retrying: slow rendering, login, verification, a partial access error, and a product being unavailable require different responses. Use the recovery procedure in [offers-and-access.md](../cn-shopping-cart/references/offers-and-access.md). Ask the user to log in when required while continuing independent comparisons; user-provided links or screenshots are another source when available. Do not export cookies, automate verification, or call restricted endpoints to work around the barrier. Explain the remaining limitation instead of pretending the search was complete.

Search these platforms unless the user narrows the scope:

- JD
- Taobao
- Pinduoduo
- Xianyu
- Zhuanzhuan

Read [platform-playbook.md](./references/platform-playbook.md) before searching.

### 3. Normalize candidate listings for 商品发现

For a lowest-price or best-value request, inspect relevant coupons and use [offers-and-access.md](../cn-shopping-cart/references/offers-and-access.md) to collect eligible free coupons and verify their application. Expand the complete product offer panel and record already-held, newly claimed, eligible and applied states separately; do not count future return coupons as current savings. Coupon collection does not authorize cart additions, favorites, checkout, paid membership or messages to sellers. Do not subtract every displayed promotion: thresholds, eligibility and stacking must be supported by the current page.

Use the user's delivery region and exact selected pack size. For groceries record grams per pack, pack count, gift weight separately, cold-chain shipping, delivery availability and thaw protection. Compute price per 500g from verified total net weight and the supported price; clearly label item-only or conditional prices when shipping or coupons remain unverified. A listing title such as “490g × 5” can display the price of its two-pack SKU.

Prefer 2 to 5 strong candidates per platform instead of dumping raw search noise.

Capture these fields whenever available:

- platform
- title
- current price
- landed price including shipping or coupons when visible
- condition
- store or seller type
- rating, review count, sales volume, or transaction count
- return policy and warranty
- authenticity or inspection signals
- advantages
- red flags
- listing URL
- evidence source such as public search, direct link, screenshot, cookie session, or MCP

### 4. Evaluate evidence quality for 候选评分

Treat evidence quality as part of the recommendation:

- prefer complete specs, clear photos, detailed disclosures, and realistic review density
- penalize suspiciously low price, vague descriptions, mismatched specs, or repeated complaints
- for used marketplaces, treat seller credibility and inspection options as first-class inputs

Read [ranking-rubric.md](./references/ranking-rubric.md) before scoring.

### 5. Score and rank

Use `scripts/score_products.py` when the candidate set is large enough to benefit from consistent scoring.

```bash
python3 scripts/score_products.py --input candidates.json
```

Use the result as a structured aid, not as a blind final answer.

### 6. Use 询价助手 when deeper confirmation is needed

When the user wants true transaction-ready pricing instead of rough market comparison:

- draft an inquiry message
- ask for manual confirmation before sending
- track replies as quoted prices rather than replacing the candidate layer

### 7. Return a decision-oriented answer from 汇总决策

Always answer in a way that helps the user buy or reject:

- lead with the best overall option
- return the top 2 to 3 candidates, not only one winner
- call out the best budget option if it differs
- call out the safest option if it differs
- explain why lower-ranked options lost
- mention the biggest risk to check before checkout
- always include direct product links when available
- make it explicit which platforms were covered by deterministic sources and which were only best-effort

When a platform fails, explain the failure in plain language instead of saying only "failed" or "access denied":

- say whether the platform has no stable public search page, a JS shell page, a login wall, or a verification page
- say what fallback was used or should be used next
- if the platform was skipped, say so explicitly

Preferred answer structure:

1. Best overall recommendation
2. Top candidates with platform, price, score, and direct product link
3. Platform coverage and why any platform was skipped or degraded
4. Biggest risk checks before buying

## Save an authorized target after comparison

When this session already authorizes saving the selected product, continue into [cn-shopping-cart](../cn-shopping-cart/SKILL.md) and its [save-target.md](../cn-shopping-cart/references/save-target.md): Taobao/Tmall and JD use the cart; Pinduoduo uses product favorites. Preserve the user's chosen product, intended SKU, quantity and delivery region. Save only the selected target(s) within that authorization; do not save every ranked alternative or ask again for permission already given. A comparison-only request remains read-only except the free coupon workflow above.

Inspect existing cart/favorite state, perform only the necessary mutation, and verify the saved result. Return the action receipt alongside the recommendation. An existing cart row is `already_present`, not a new add; a PDD favorite saves the product and does not lock its intended SKU or price. Report untested claiming/application and inaccessible stages explicitly.

## References

- Use [platform-playbook.md](./references/platform-playbook.md) for platform-specific heuristics.
- Use [ranking-rubric.md](./references/ranking-rubric.md) for default scoring and tie-break rules.
- Use [offers-and-access.md](../cn-shopping-cart/references/offers-and-access.md) for coupons, delivery checks and bounded browser recovery.
- Use the installed shopping browser's [runtime.md](../cn-shopping-cart/references/runtime.md) when native MCP tools are unavailable.
