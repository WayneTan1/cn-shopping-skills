# Save the selected product

Read this after a target has been chosen and the user has authorized cart additions or favorites. A request to add/implement this capability for future use alone does not authorize live account mutations. An explicit request to test it on the current shopping target does. Reuse session authorization for the same scope.

## Choose the action

- Taobao/Tmall or JD: add the verified SKU to the cart.
- Pinduoduo: favorite the verified product. Do not substitute 发起拼单、去拼单、单独购买 or a purchase dialog's 确定 for a save action. Prefer a separate SKU/规格 entry for inspection. If the only control may initiate a purchase, do not click it merely to reveal specifications.
- Honor an explicit alternative chosen by the user. Saving one selected winner does not imply saving every compared listing; test multiple candidates only when the session authorizes them.

Before changing state, confirm the product ID, seller, selected variant, intended quantity and current price basis from fresh page evidence. Use the user's delivery region and existing budget. If delivery is unresolved, keep it unresolved in the receipt; saving a candidate does not prove it is orderable.

## Taobao/Tmall and JD carts

1. Inspect the cart for the same seller, product and SKU. Follow the observed cart link; it may open another tab or redirect to another official cart domain. Select the newly observed tab and verify its actual contents and login state before continuing.
2. For a desired total quantity, if that quantity is already present, report `already_present` and keep it. If fewer are present, add only the missing quantity. A request for an additional quantity has different semantics: record it and calculate the intended total from the observed starting quantity. If quantity intent is unclear or existing quantity exceeds the target, preserve it and report the mismatch; do not silently remove items. Do not remove and re-add an item to manufacture a test result.
3. On the product page, verify the selected SKU, quantity, stock and current price again. Click the observed **加入购物车** control once. Avoid membership trials and optional paid services unless authorized. Preserve unrelated cart rows and selection states.
4. Open the cart and verify product ID, seller, exact variant and resulting quantity. A toast alone is provisional. If a cart coupon entry is visible for this target, inspect it using [offers-and-access.md](offers-and-access.md) and recheck the price; do not select unrelated items to meet its threshold or enter checkout.
5. If the click times out, inspect the cart before retrying. Retry only after evidence establishes that the intended mutation did not occur; otherwise record `unknown`. Never click 立即购买、结算、提交订单 or payment controls under save-only authorization.

## Pinduoduo favorites

1. Confirm product ID and seller. Inspect the intended SKU and price through a safe visible specification entry when available; retain them separately because favorites usually save only a product.
2. Inspect the current control. **已收藏 / 取消收藏** indicates an existing favorite: report `already_present` without clicking. Do not mistake 收藏店铺 or 关注店铺 for the product favorite.
3. If the product is not saved, click the observed **收藏** control once. Look for **已收藏**, a filled icon with an accessible saved label, or another explicit saved state. A toast alone is provisional.
4. Verify persistence using the observed product-favorites list and matching product ID, or reopen the same canonical product and confirm it still says **已收藏**. A dated 我收藏了此商品 activity on that product is supporting evidence; do not confuse its activity dialog with the favorites list.
5. If a click times out, reopen/read the current state before any retry. Do not click 已收藏 again: it can undo the action. If verification requires login or an app, leave the achieved state alone and report `unknown` plus the missing verification.

A product favorite does not reserve a price, SKU, stock or quantity. Report the intended SKU/quantity separately with `savedScope: product`. Do not claim that a specific pack was put into a PDD cart.

## Evidence and receipt

Use focused snapshots of the coupon panel, target cart row and favorite control; a whole account/cart dump is unnecessary. Canonicalize URLs to product/SKU identifiers and strip account IDs, session tokens and tracking parameters. Store prices as observed numbers plus currency and basis; unknown delivered totals stay null.

A reusable receipt contains:

- `observedAt` with timezone; `platform`; canonical `productUrl`; `productId`; `seller`; `intendedVariant`; `observedSkuId` (null if unavailable); `requestedQuantity`; `quantityIntent` (`desired_total` or `additional`).
- `delivery`: requested region and separate verification status; `price`: currency, displayed amount, price basis, verified delivered total or null.
- `couponDiscovery`: surfaces actually inspected and per-surface status (`inspected`, `no_visible_entry`, `blocked`, `app_only` or `not_inspected`). A blocked panel is not evidence that no coupons exist.
- `coupons`: label, type, face value, threshold and its basis, scope, validity, account requirements; `claimStatus` (`available`, `claimed_now`, `already_available`, `unavailable`, `unknown`); `eligibility` (`eligible`, `ineligible`, `unknown`) with reason; `applicationStatus` (`applied`, `not_applied`, `unknown`); `verifiedDiscount` (null if unknown); before/after labels and evidence. A 去使用 label observed before clicking supports `already_available`, not `claimed_now`.
- `save`: `action` (`cart` or `favorite`); `savedScope` (`sku` or `product`); before/after quantity or favorite state; mutation count; `status` (`verified`, `already_present`, `failed`, `unknown` or `not_attempted`); `verificationMethod`; evidence paths and any limitations. `verified` requires both a necessary mutation and persisted result. `already_present` is a successful final state without a new mutation.
- `coverage`: distinguish live successes, ineligible promotions, inaccessible stages and untested stages. Report claim/application as untested when no relevant claimable/applicable coupon was encountered. Do not infer new-add success from an already populated cart.

The shopping_compare tool accepts offers only. Keep this receipt separate rather than adding unsupported coupon/favorite fields to that tool's arguments.
