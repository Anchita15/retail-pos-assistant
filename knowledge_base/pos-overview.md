# POS Overview (Original Notes)

This note summarizes a typical retail Point-of-Sale (POS) system without referencing any vendor-specific product.

## Core Components
- **POS client**: UI for scanning items, applying discounts, collecting tenders, printing/emailing receipts.
- **Pricing & tax services**: Determine base price, promotions, taxes; must be idempotent and traceable.
- **Promotions & loyalty**: Coupon validation, points accrual/redemption, eligibility checks.
- **Inventory**: Real-time availability, reservations, post-sale decrements, reconciliation jobs.
- **Payments**: External gateway calls with timeouts, retries, and error handling for reversals/voids.
- **Data stores**: Transaction log, product catalog, configuration, user/role permissions.
- **Integration**: REST/JSON for synchronous flows; message bus (MoM) for events such as `transaction.completed`.

## Typical Flow
1. **Scan items** → POS calls pricing service; promotions engine evaluates best offers.
2. **Totals** → display subtotals, taxes, savings, and loyalty status.
3. **Tender** → call payment gateway; handle pending timeouts and duplicate authorizations safely.
4. **Finalize** → persist transaction, publish an event, update inventory, and issue receipt.
5. **After-sale** → reconciliation jobs, analytics, and loyalty point posting.

## Architecture Notes
- Use **idempotent** endpoints and **correlation IDs** for cross-service tracing.
- Apply **retry with exponential backoff** on network failures; avoid double-charges with safe rollback.
- Prefer **event-driven** side effects (inventory updates, analytics) so the POS flow stays fast.
