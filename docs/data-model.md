# Phase 1 data model

## Core relationships

```text
Region (tree)
  |-- Region Membership -- User
  `-- CRM Organization (Customer, self hierarchy)
        |-- Account Assignment -- User
        |-- Manufacturing Site
        |-- Contact Affiliation -- Contact
        `-- Product Opportunity -- CRM Product
              |-- Opportunity Market -- Target Market
              `-- Opportunity Stakeholder -- Contact Affiliation

CRM Product -- Product Responsibility -- User
Pipeline -- Pipeline Stage -- Product Opportunity.current_stage
```

## Planned custom DocTypes

| DocType | Purpose and key invariants |
| --- | --- |
| Region | Nested-set Region master with code, parent, active flag, and sort order. |
| Region Membership Role | Configurable semantic roles used by Region Membership. |
| Region Membership | Dated, active User-to-Region membership with role and primary flag. |
| Manufacturing Site | Customer-owned operational site; visibility inherits Customer. |
| Contact Affiliation | Dated Contact relationship to either Customer or Manufacturing Site; only one primary active affiliation per Contact/entity where applicable. |
| Account Assignment | Dated Customer-to-User responsibility and assignment type. GAM assignments may cascade to descendant Customers. |
| Account Assignment Type | Configurable types, including primary AM, secondary AM, GAM, support, and temporary cover. |
| Product Responsibility | Dated CRM Product-to-User responsibility. |
| Product Opportunity | Customer + CRM Product commercial record, derived Region, accountable owner, pipeline/current stage, next action, and status. |
| Pipeline | Configurable active pipeline with one default. |
| Pipeline Stage | Ordered stage belonging to one Pipeline, with probability and won/lost semantics. |
| Target Market | Configurable market master independent of Region and Country. |
| Opportunity Market | Market-level volume, currency, price placeholders, dates, probability override, filing context, and notes. No forecast engine. |
| Opportunity Stakeholder | Opportunity link to a Contact Affiliation, with configurable role and relationship attributes. |
| Opportunity Stakeholder Role | Configurable stakeholder role master. |

## Standard-object extensions

`CRM Organization` gains `parent_customer`, `account_type`, `country`, `region`,
`customer_status`, `is_key_account`, and `sap_customer_id`. Parent links must not
form cycles. Region is required on operating Customers and is never inferred
from Target Market.

These app-owned fields use Frappe's required `custom_` prefix in storage. Contact
Affiliation stores Customer on every record, deriving it from Manufacturing Site
for site affiliations. This explicit, indexed Customer scope avoids a Dynamic
Link permission query and makes inherited access auditable.

`CRM Product` gains molecule, category, therapeutic area, product owner,
commercial status, standard UOM, standard pack size, and notes. All normal CRM
business roles receive read access; edit access is controlled separately.

## Product Opportunity invariants

- Name is generated from Customer + Product and is not authoritative identity.
- Region is derived from Customer and read-only in normal workflows.
- Current Stage must belong to the selected Pipeline.
- Stage entered date changes only when Current Stage changes.
- One active Customer + Product record is the normal rule. A duplicate is
  blocked unless an explicitly permission-controlled override is supplied and
  audited.
- Opportunity Markets are the source for market-level commercial values. Phase
  1 does not implement forecast aggregation or a pricing workflow.
- Active opportunities expose next action, due date, and optional action owner;
  they do not implement a separate task engine.

All assignment and affiliation records are dated and auditable. Historical
records are deactivated or ended rather than overwritten.
