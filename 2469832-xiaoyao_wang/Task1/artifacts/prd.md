## Overview
- Single cart/checkout across multiple independently managed stalls (separate databases)
- Platform splits a paid order into per-stall sub-orders for merchant fulfillment
- Merchants view/update only their sub-orders; customer sees consolidated status
- System auto-generates a flowchart documenting the order-splitting process

## Goals
- Enable mixed-stall cart and one-time payment with correct totals/fees/taxes
- Create reliable, idempotent order-splitting and per-stall order sync
- Provide merchant tooling for fast sub-order fulfillment updates
- Auto-produce/export an always-up-to-date order-splitting flowchart

## Non-Goals
- Unifying or migrating stall databases into a single shared database
- Implementing full merchant POS/accounting beyond sub-order views and statuses
- Supporting complex multi-address shipping in v1 (beyond per-stall fulfillment rules)
- Building a general-purpose workflow engine for all business processes

## User Personas (brief)
- Customer: one cart across stalls, clear totals, consolidated tracking with per-stall updates
- Merchant: real-time sub-order feed, accurate breakdown per stall, simple status updates
- Administrator: audit logs, exception handling, retry/rollback tools, reliability dashboards
- Developer: clear API contracts, idempotent split workflow, flowchart generation tied to releases

## Key Features
- Multi-stall cart with item grouping by stall and unified checkout totals
- Order-splitting service that creates per-stall sub-orders and syncs to stall systems
- Merchant portal/API to list sub-orders and update fulfillment status
- Automatic flowchart generation/export from the splitting workflow logic

## User Flows
- Customer: browse stalls → add items → view cart grouped by stall → pay once → track overall + per-stall statuses
- Platform: payment authorized/captured → split by stall → create sub-orders → notify/sync stalls → aggregate statuses
- Merchant: receive sub-order → confirm/prepare → mark ready/shipped → updates reflected in customer’s main order
- Admin/Dev: monitor split jobs → inspect failures → retry safely → export/view flowchart for current version

## Functional Requirements
- Cart must support items from multiple stalls and compute totals (items, fees, taxes) per stall and overall
- Checkout must create a single platform order and then generate sub-orders per stall with itemized allocations
- Sub-order sync must write to each stall system via API/connector and handle partial failures with retries
- Flowchart generator must output a versioned diagram of split logic (e.g., SVG/PNG) on deploy/CI

## Non-Functional Requirements
- Idempotency for checkout and splitting to prevent duplicate sub-orders on retries
- Consistency: customer-visible order state must reflect latest sub-order states with bounded lag
- Security: least-privilege access so merchants can only access their stall’s data; encrypted data in transit
- Observability: structured logs, metrics, and traceability per order/sub-order with audit trails

## Constraints/Assumptions
- Each stall owns its catalog/inventory DB; platform cannot directly query stall DBs without agreed interfaces
- Payment is collected once by the platform and allocated logically to sub-orders (settlement handled separately)
- Stalls expose a stable API/connector for order creation and status updates (or platform provides adapter)
- v1 assumes a finite set of status states and a standard mapping between platform and stall statuses

## Success Metrics
- % of mixed-stall checkouts that successfully split into all required sub-orders on first attempt
- Median time from payment to all sub-orders created/synced to stalls
- Rate of split-job failures requiring admin intervention; retry success rate
- Customer support tickets related to missing/incorrect sub-orders or status mismatches

## Open Questions
- How are taxes, platform fees, discounts, and tips allocated across stalls (proportional, per-item, per-stall rules)?
- What is the settlement model to merchants (netting fees, refunds/chargebacks, partial cancellations)?
- What are the required stall integration methods (push vs pull, webhooks, polling) and SLA expectations?
- What flowchart source-of-truth is preferred (code annotations, workflow definition, traces) and required formats?