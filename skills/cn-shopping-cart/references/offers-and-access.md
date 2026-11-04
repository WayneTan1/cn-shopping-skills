# Coupons, delivery and access recovery

Use this workflow for Taobao/Tmall, JD and Pinduoduo through the installed shopping browser. It provides browser procedures, not a guarantee that every platform is accessible or that its promotions can be verified without checkout.

## Discover coupons on the exact target

Confirm product, selected SKU, requested quantity and delivery region before pricing. Do not use an advertised minimum price as the selected SKU's price. Inspect the full relevant promotion surface, not just its collapsed summary:

| Platform | Normal visible discovery route | Interpret separately |
| --- | --- | --- |
| Taobao/Tmall | Product 领券 / 优惠 / 优惠券 panel, expand relevant 查看全部; then observed shop 领券中心 or target cart row's coupon entry when present | Store/platform coupons, official markdowns, cross-store thresholds, 88VIP, new-customer offers, coins and subsidies |
| JD | Product 优惠 panel; expand 查看全部(n) even when its summary initially mentions only gifts; then an observed shop/cart coupon entry when relevant | Self-operated/third-party scope, PLUS, store/platform coupons, subsidies, threshold discounts, gifts and post-purchase return coupons |
| Pinduoduo | Product visible 优惠券 / 领券 / 优惠 entry or observed shop coupon entry; read group-price conditions and selected SKU price | Direct price reductions, coupons, new-user benefits, individual/group purchase and multi-person group requirements |

Use only controls actually observed on the current page. Labels and placement can change. For a selected finalist, inspect its full product offer panel and any directly visible relevant shop/cart entry. Stop when the relevant surfaces are read or their access limitation is established; do not search unrelated coupon sites, claim unrelated offers, or open every promotion in the account.

Record surfaces inspected, visible terms and missing/blocked surfaces. If no entry is visible, say **no coupon entry visible on the inspected page**. A collapsed, inaccessible or app-only panel cannot establish **no coupons exist**. A claim that no additional coupon was verified must not be rewritten as no coupon exists.

## Claim and verify separately

Lowest actionable price / best-value shopping includes collecting directly relevant, free, no-obligation coupons. A request only to describe an offer is read-only. Reuse explicit session authorization; do not ask for each eligible coupon.

1. Read face value, threshold, threshold basis (before/after other discounts), product/shop scope, validity, account/new-customer restrictions and stacking rules. Evaluate only the requested basket. Unrelated cart items do not establish its eligibility. Record known ineligible offers without changing the purchase to fit them.
2. Inspect the before state. A label such as 去使用 / 已领取 already present before the action supports **already available**; it does not prove a new claim. Do not click 去使用 just to test claiming: it may navigate into a purchase flow.
3. Claim a relevant eligible free coupon through its observed 领取 / 立即领取 control. Skip a known-ineligible coupon unless the user separately requests collecting it for later. Skip paid coupon packs, membership trials, credit products, points, invitations, social sharing, following shops or other commitments unless separately authorized. Unknown eligibility stays unknown; do not turn it into a verified saving.
4. Confirm the resulting 已领取 / 去使用 state or matching coupon-wallet entry. If a click times out, inspect first; do not repeat a potentially successful claim blindly. Persisted before/after evidence supports **claimed now**; a success toast alone is provisional.
5. Reinspect the same SKU and requested quantity. Verify application using a visible target-specific discounted line/cart amount, or an order preview only if entering checkout was separately authorized. Claiming and eligibility are not proof of application. Do not enter checkout solely to validate a coupon under research/save-only authorization.
6. Recalculate the supported total and ranking if an applied discount changes it. Record discovery, claim, eligibility and application independently, using the receipt fields in [save-target.md](save-target.md).

Do not subtract every displayed offer or sum identically labeled coupons. Unless stacking is explicitly supported, show them as alternatives. An already discounted subsidy price must not have the subsidy deducted again. A 满额返券 / 收货后返券 promotion belongs to a future purchase, not the current order's cash discount. A shipping-service voucher gifted with a product is not a discount on that product. Record expired, app-only, membership-dependent or unresolved offers as conditional, with no verified savings attributed to them.

Do not buy extra products solely to meet a threshold or alter unrelated cart selections. A larger pack may be compared as an alternative with its full spend and weight. A group price stays conditional until its requirements are supported; do not initiate a group purchase to validate it without authorization.
## Delivery and comparable quantities

Select the delivery region in the listing's normal region selector without editing a saved address. Do not copy personal address/contact data into reports. If the user supplies only a city and a district is required, ask or leave delivery unverified; do not invent a district.

For frozen food capture net weight per bag, number of bags, gift weight and cold-chain terms. Keep a gift out of the weight denominator until its type and weight are confirmed. Present comparisons with and without a different-product gift when it materially changes the ranking.

The confirmed delivered total must match the selected SKU, quantity, verified discounts and delivery region. Otherwise leave `landedPrice` null and label the number as item price or conditional estimate. Search cards, general store scores and reviews for a different variant cannot establish product-specific quality or final price.

## Prevent avoidable access problems

- Reuse the dedicated persistent browser. Inspect tabs, select the target and verify its URL immediately before an action. Do not share cookies outside it or operate permission prompts.
- Start from a normal platform search or shop link, then select products through observed controls. Keep one active navigation/action sequence; do not launch parallel product navigations in the same session.
- Allow navigation to finish and look for relevant text with `browser_find`. Take focused snapshots instead of repeatedly reloading or polling full pages. Do not open many duplicate tabs or repeatedly revisit the same blocked URL.
- Keep a per-platform failure note during the task: page, time, failure type, attempted recovery and next allowed action. Repeated failures should reduce requests, not increase them.

## Recover according to the actual failure

| Observed state | Next action | Stopping condition |
| --- | --- | --- |
| Slow render or ordinary network timeout, no challenge | Inspect the current page, then wait up to 15 seconds for relevant content. Retry the read/navigation once if still necessary. | A second failure: move to another candidate/source and report the limitation. |
| Partial “访问异常” page with readable SKU controls | Preserve visible evidence. Treat missing promotions, reviews or inconsistent prices as unverified. Allow a single normal homepage/shop re-entry after a cooldown of at least 30 seconds, using that time for independent work. | If the same anomaly remains, stop retrying this platform for the task unless the user restores access or meaningful new evidence arrives. |
| Login required | Leave the login page open; ask the user to sign in themselves and continue other work. Reinspect after they report completion. | No automated password, OTP, cookie transfer or repeated login attempts. |
| CAPTCHA, slider, risk verification or explicit access denial | Stop actions against the challenge and request user completion through the normal browser. Public information and other platforms remain available. | Do not vary identities, proxies, fingerprints, profiles, headers, hidden APIs or endpoints to evade the restriction. |
| App-only coupon or details | Record the visible condition and ask the user to inspect it in their app if it could change the winner. | Do not report it as claimed, applied or verified without evidence. |
| Product unavailable or unsupported delivery region | Verify it is the intended SKU and region, then select another candidate. | Do not treat stock/delivery restrictions as a browser error to retry. |

Search price and detail price disagreements are evidence discrepancies. Record both and their contexts; prefer a fully verified selected-SKU total. If no such total is available, report a provisional recommendation and the unresolved price rather than choosing the smaller number.

## Report what actually happened

Summarize the best supported candidate, exact option, price basis, delivery region, unit-weight cost, coupon states and the limitation that could change the recommendation. Separate verified platform coverage from login-blocked or search-only coverage. An updated skill or successful browser connection does not prove that a coupon was collected or that a real order can be placed.
