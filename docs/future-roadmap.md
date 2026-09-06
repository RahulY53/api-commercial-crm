# Future extension roadmap

This document records extension points that Phase 1 must preserve. It does not
authorize or implement any Phase 2 capability. The current system remains a
modular Frappe application and a complete CRM system of record without external
integrations or AI.

## Commercial transaction chain

Later phases may extend the locked Phase 1 grain as follows:

```text
Customer
  -> Product Opportunity
    -> Opportunity Market
      -> RFQ Line
        -> Quote Line
```

An RFQ will be a transaction header with multiple lines and may therefore span
multiple Products and Product Opportunities. A Quote will describe the response
offered to the customer. Issued Quote versions must eventually be immutable and
historically preserved. Phase 1 contains no RFQ, quotation, price approval, or
quote-version implementation.

## Forecasting

Forecasting will primarily attach to `Product Opportunity -> Opportunity
Market`, where target-market assumptions already belong. A later design may add
Base, Upside, and Downside scenarios, monthly phasing, ramp profiles, prices,
forecast cycles, and immutable snapshots. Roll-ups may be required by Customer,
Region, Account Manager, global account, Product, Product Manager, and Target
Market.

Opportunity Market remains detail data and future totals should be calculated
from it. Phase 1 must not introduce manually maintained duplicate totals or a
forecast engine.

## Activities and Microsoft 365

Customer 360 and Product Opportunity 360 reserve clear surfaces for future
emails, meetings, calls, notes, tasks, and a unified activity timeline. Outlook,
Calendar, and Teams synchronization will use a Microsoft Graph adapter at the
integration boundary. Microsoft-specific state must not be embedded throughout
Customer or Opportunity controllers.

Phase 1 contains no mailbox, calendar, meeting, or activity synchronization and
no full task engine.

## SAP boundary

SAP remains the enterprise ERP and the source for later order, shipment,
invoice, and actual-revenue integration. Customer and Product identifiers may
support entity matching, but Phase 1 does not reproduce ERP transactions or
business logic.

Future SAP exchange must be implemented behind explicit adapters and domain
services, with reconciliation, audit, retry, and authorization behaviour made
visible. It must not be scattered across DocType controllers.

## Reporting and intelligence

Advanced dashboards and external market or regulatory intelligence belong to
later phases. Reports must consume the same authoritative domain records and
permission scopes used by lists and direct document access.

AI may later summarize, recommend, draft, detect risk, assist forecasting, or
prepare management briefings. It remains optional, is never the system of
record, and must use the same server-side services and permissions as a human
user. Human ownership and approval remain explicit.

## Review gates for a later phase

Before beginning any future capability:

1. Confirm Phase 1 data and permission invariants remain intact.
2. Document the source of truth and ownership of every new fact.
3. Keep external-system code behind an integration boundary.
4. Define audit, immutability, and failure behaviour before rollout.
5. Add persona, API, and direct-access security tests.
6. Upgrade pinned Frappe or CRM versions only as a separate reviewed change.
