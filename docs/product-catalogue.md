# API Product catalogue

Phase 1 reuses Frappe CRM's `CRM Product` as the authoritative API catalogue
record. The app adds API-specific metadata through supported, migrate-synchronised
custom fields and does not modify Frappe CRM core.

## Field mapping

| Commercial concept | Stored field |
| --- | --- |
| API/Product name | `CRM Product.product_name` |
| Internal product code | `CRM Product.product_code` |
| Notes/description | `CRM Product.description` |
| Molecule | `CRM Product.custom_molecule` |
| Category | `CRM Product.custom_product_category` |
| Therapeutic area | `CRM Product.custom_therapeutic_area` |
| Commercial status | `CRM Product.custom_commercial_status` |
| Standard UOM | `CRM Product.custom_standard_uom` |
| Standard pack size | `CRM Product.custom_standard_pack_size` |
| Product owner | Primary effective `Product Responsibility` |

Category, therapeutic area, and commercial status are explicit configurable
masters. Standard UOM remains text because the installed Frappe and Frappe CRM
baseline has no UOM master and ERPNext is intentionally not installed. The
optional internal manufacturing site field is deferred because Phase 1 only has
customer-owned Manufacturing Sites; linking those would misrepresent the brief.

## Responsibility and audit rules

`Product Responsibility` links a CRM Product to a responsible User with start
and end dates, an active flag, and an optional Primary Product Owner flag.
Overlapping active assignments for the same Product and User are rejected.
Only one primary owner may overlap for a Product. Active responsibilities also
require an enabled Product and enabled User. Frappe change tracking preserves
the assignment history.

Product Manager opportunity visibility will resolve effective Product
Responsibilities in the central permission layer. This increment does not add
an independent owner value to CRM Product, preventing ownership drift.

All normal CRM business roles receive read-only catalogue permissions. Product
master creation and editing is limited to CRM Admin and System Manager. The
dedicated Product Catalogue screen and joined primary-owner column belong to the
Phase 1 user-experience milestone.
