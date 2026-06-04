## Functional Requirements
- Support a multi-stall cart with items grouped by stall.
- Compute totals (items, fees, taxes) per stall and overall in the cart/checkout.
- Provide a unified checkout with one-time payment across multiple stalls.
- Create a single platform “parent” order for the customer at checkout.
- Split the paid parent order into per-stall sub-orders with itemized allocations.
- Sync/write each sub-order into the corresponding stall system via API/connector.
- Handle partial failures during sub-order sync (e.g., some stalls succeed, others fail) with retry behavior.
- Allow merchants to view/list only their own sub-orders (via merchant portal and/or API).
- Allow merchants to update sub-order fulfillment status (e.g., confirm/prepare/ready/shipped).
- Aggregate sub-order statuses into a consolidated customer-visible order status and show per-stall updates.
- Provide admin/developer tools to monitor split jobs, inspect failures, and retry safely.
- Auto-generate and export a versioned flowchart/diagram of the order-splitting logic (e.g., SVG/PNG), tied to deploy/CI.

## Non-Functional Requirements
- Idempotency for checkout and order-splitting to prevent duplicate orders/sub-orders during retries.
- Consistency requirement: customer-visible order state reflects latest sub-order states with bounded lag.
- Security: least-privilege access control so merchants can only access their stall’s data.
- Security: encrypt data in transit.
- Observability: structured logging.
- Observability: metrics collection.
- Observability: tracing/traceability per order and sub-order.
- Auditability: maintain audit trails for actions/events (e.g., status changes, retries, failures).