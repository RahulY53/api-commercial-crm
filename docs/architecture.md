# Phase 1 architecture

Status: accepted baseline, 6 September 2026.

## Scope

`api_commercial` is a separate Frappe application layered on Frappe CRM. It
owns API-commercial domain records and services while using supported Frappe
hooks and APIs. Frappe and Frappe CRM remain unmodified.

The locked commercial hierarchy is:

> Region -> Customer -> Product Opportunity -> Target Market(s)

Region means the geography responsible for the customer relationship. It is
not a target market. Product Opportunity has the grain Customer + Product.

Phase 1 ends at master data, assignments, product opportunities, configurable
stages, target markets, stakeholders, next actions, secure CRUD, 360 views,
tests, and demo data. RFQ, quotation, pricing workflow, forecasting, Microsoft
365, SAP, reporting suites, and AI are explicitly out of scope.

## Installed baseline

| Component | Version | Source revision |
| --- | --- | --- |
| Frappe Framework | v15.120.0 | `755b5cb81fabb431265690fca07f4a8038a5599a` |
| Frappe CRM | v1.83.0 | `52c500d6bdac3cd51553f95cfae9c7a940d99f1a` |
| api_commercial | 0.0.1 | this repository |

Local setup and CI use these tags. Upgrades must be explicit and must rerun the
permission and persona test suites.

## Standard objects reused

- `CRM Organization` is the Customer/Account system of record. Custom fields
  add parent Customer, account classification, country, Region, status, key
  account flag, and the inactive SAP identifier placeholder.
- Frappe `Contact` remains the person system of record. CRM already supplies
  its supported `CustomContact` override; this app will not replace it.
- `Address`, `User`, `Country`, and `Currency` remain standard masters.
- `CRM Product` is the product catalogue base. Custom fields add the required
  API business metadata; Product Responsibility remains a separate relation.

## Objects not reused

- `CRM Deal` permits multiple products and its visibility is based on owner,
  ToDo assignment, and a single sales tree. That conflicts with the locked
  Customer + Product grain and overlapping commercial scopes. Product
  Opportunity is therefore custom.
- `CRM Territory` is a generic territory tree. Region is an explicit stable
  business concept and is modelled as a custom nested-set DocType.
- `CRM Sales Hierarchy` cannot model multi-Region membership, GAM account
  hierarchy access, or cross-Region Product Manager access.
- `CRM Deal Status` is global rather than scoped to configurable pipelines.

## Module boundaries

- `doctype`: persistent domain model and local invariant validation.
- `services`: business operations and reusable scope resolution.
- `permissions`: list-query and document-level permission adapters.
- `api`: narrow whitelisted operations used by the UI and future integrations.
- `fixtures`: custom fields, roles, and workspace configuration owned by this
  app.
- `tests`: unit, integration, permission-matrix, and persona workflow tests.

External-system logic will later live behind adapters. Phase 1 contains no SAP,
Microsoft Graph, or LLM-specific code.

## Delivery milestones

1. Foundation: pinned environment, architecture records, CI, smoke tests.
2. Organisation: Region, membership, account assignment, GAM hierarchy.
3. Customer: Organization extensions, Manufacturing Site, Contact Affiliation.
4. Catalogue: CRM Product extensions and Product Responsibility.
5. Opportunity: Product Opportunity, pipelines, stages, markets, stakeholders.
6. Security: additive server-side visibility and persona tests.
7. Experience: navigation, Customer 360, Product Opportunity 360.
8. Acceptance: deterministic demo data and end-to-end persona verification.
9. Closeout: administrator and upgrade documentation.

## Version-specific constraints

Frappe v15 combines multiple permission query hooks with `AND` and evaluates
document permission hooks in reverse app order until one returns a value.
Permission functions must therefore be paired and tested; they must not rely on
one hook widening another app's result. CRM already overrides `Contact`, so
this app uses events, relations, and permission hooks rather than a second
class override.
