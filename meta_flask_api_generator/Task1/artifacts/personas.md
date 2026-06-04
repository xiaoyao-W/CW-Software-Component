Personas: Core users include shoppers placing a single mixed-stall order, merchants fulfilling their portion, and admins ensuring the split-and-sync workflow runs reliably.

1. **Customer**
   - **Responsibilities:** Browse stalls, add items to cart, checkout once, track overall order status.
   - **Needs:** One cart across stalls, clear totals and fees, consolidated tracking with per-stall updates.

2. **Merchant**
   - **Responsibilities:** Manage stall catalog and inventory, view assigned sub-orders, update fulfillment and pickup/delivery status.
   - **Needs:** Real-time sub-order feed, simple status updates, accurate item and payment breakdown per stall.

3. **Administrator**
   - **Responsibilities:** Configure stalls and integrations, monitor order-splitting jobs, resolve exceptions and disputes.
   - **Needs:** Audit logs per split, retry/rollback tools, dashboards for stuck or failed sub-orders.

4. **Developer**
   - **Responsibilities:** Build and maintain APIs, implement cross-database cart/checkout, generate flowcharts from the split logic.
   - **Needs:** Clear contract between platform and stall DBs, idempotent order-splitting workflow, automatic flowchart export tied to releases.