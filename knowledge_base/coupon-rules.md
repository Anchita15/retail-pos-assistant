# Coupon & Loyalty Rules (Original Notes)

This guide describes common practices for applying coupons and loyalty in a retail POS.

## General Rules
- **Order of operations**: Base price → promotions/coupons → tax.
- **Eligibility**: Check product/brand, store, date/time window, channel, and minimum spend.
- **Stacking**: Allow limited stacking; when conflicts arise, apply the **customer-best** discount.
- **Expiration & one-time use**: Enforce end dates and tokenization for single-use offers.
- **Transparency**: Show clear messages when a coupon is rejected (e.g., “item not eligible”).
- **Returns**: Reverse loyalty points proportionally; recalculate discounts when items are returned.
- **Fraud controls**: Track redemption per account/device; rate-limit suspicious attempts.

## Loyalty Considerations
- **Accrual**: Points typically accrue on pre-tax totals after discounts.
- **Redemption**: Treat points as a tender; verify balance and apply partial redemption if needed.
- **Edge cases**: Mixed baskets, BOGO promotions, and partial refunds should have deterministic rules.

## Data & Observability
- Log the **original price**, discount breakdown, coupon IDs, and final price.
- Publish an event (e.g., `promotion.applied`) for downstream analytics and auditability.
