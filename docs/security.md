# Phase 1 security contract

## Three layers

1. Frappe Role permissions determine which actions a user may perform.
2. Server-side record scope determines which records the user may access.
3. Field permission levels protect sensitive commercial fields independently.

Ownership is accountability metadata, not the complete permission model.
Client-side filtering is never an access-control boundary.

## Additive visibility

A reusable scope service calculates access as the union of applicable grants:

- Account Manager: explicitly assigned Customers.
- Region Head: Customers in active Regions they lead.
- Global Account Manager: assigned parent Customer plus all descendants.
- Product Manager: read access to Product Opportunities for assigned Products.
- Leadership: broad read access.
- CRM Admin and System Manager: administrative access.

Manufacturing Sites and Contact Affiliations inherit Customer scope. Product
Opportunity inherits Customer scope and additionally accepts Product Manager
read scope. Opportunity Markets and Stakeholders inherit their Opportunity.
Contact visibility is granted when at least one active affiliation is visible.
A GAM or Product Manager does not automatically become Opportunity owner.

Date-bounded grants apply only when active and when the current date is within
their optional start/end dates.

## Enforcement pattern

Every protected DocType receives both:

- `permission_query_conditions` for lists, search, reports, and link queries;
- `has_permission` for direct document reads and writes.

Both call the same scope-building services. SQL is parameter-safe, hierarchy
resolution uses nested-set ranges, and access is evaluated in bounded queries
rather than per-row recursion. Role permission remains required before a
record-level hook can allow an operation.

Standard `Contact` needs special care because Frappe and CRM already provide
permission/class hooks. The implementation preserves those constraints and adds
affiliation access without replacing CRM's class override. Tests cover both
direct document access and list visibility.

## Functional roles

- Account Manager
- Region Head
- Global Account Manager
- Product Manager
- Business Development
- Customer Service
- Commercial/Pricing
- Leadership
- CRM Admin
- System Manager (standard)

A user may hold multiple roles; record grants are additive. Write privileges do
not automatically expand when read scopes are combined.

## Sensitive fields and audit

Market target price, expected selling price, expected revenue, and future
commercially sensitive fields use permission level 1 and are limited to
Commercial/Pricing, Leadership, and administrators unless an explicit later
policy says otherwise.

Domain records enable change tracking. Assignments, stage transitions, derived
Region changes, ownership changes, and duplicate overrides remain explainable.
Access paths are represented by dated Account Assignments, Region Memberships,
Product Responsibilities, explicit ownership, or broad read roles, so an
administrator can inspect why a user has access without relying on UI state.

## Required tests

The matrix covers positive and negative list/read/write cases for Account
Manager, Region Head, GAM, Product Manager, Business Development, Customer
Service, Commercial/Pricing, Leadership, CRM Admin, and System Manager. It also
covers expired assignments, unrelated Regions/Customers/Products, hierarchy
cascades, multi-role union, field-level sensitivity, and direct URL/API access.
