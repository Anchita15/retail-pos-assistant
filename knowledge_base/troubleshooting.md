# Troubleshooting Playbook (Original Notes)

A quick field guide for diagnosing POS issues in stores.

## When the POS Freezes During Payment
1. **Capture context**: transaction ID, last API called, timestamps, and cashier ID.
2. **Network checks**: verify DNS and gateway reachability; retry with backoff if transient.
3. **Payment safety**: if authorization state is unknown, query the gateway before retrying to avoid double charges.
4. **Rollback**: use safe void/reversal APIs; mark the local transaction as pending-review if state cannot be confirmed.
5. **Logging**: include correlation IDs across services to let support trace the request end-to-end.

## Inventory Mismatch
- Reconcile using `transaction.completed` events and a nightly job.
- Flag negative on-hand as an exception; create a ticket automatically with affected SKUs and store.

## Performance Issues
- Cache catalog and tax tables with short TTLs.
- Limit synchronous calls in the checkout path; move non-critical work (analytics, receipts) to async jobs.

## Support Handoff
- Provide a minimal bundle: logs, timestamps, correlation ID, request payloads (with PII masked), and store environment details.
