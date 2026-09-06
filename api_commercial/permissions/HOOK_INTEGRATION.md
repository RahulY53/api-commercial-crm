# Permission hook integration

Add these mappings to `api_commercial/hooks.py` after all Phase 1 DocTypes are
available. Frappe v15 combines list conditions from installed apps with `AND`.

```python
permission_query_conditions = {
	"CRM Organization": "api_commercial.permissions.visibility.get_crm_organization_permission_query_conditions",
	"Manufacturing Site": "api_commercial.permissions.visibility.get_manufacturing_site_permission_query_conditions",
	"Contact Affiliation": "api_commercial.permissions.visibility.get_contact_affiliation_permission_query_conditions",
	"Contact": "api_commercial.permissions.visibility.get_contact_permission_query_conditions",
	"Product Opportunity": "api_commercial.permissions.visibility.get_product_opportunity_permission_query_conditions",
	"Opportunity Market": "api_commercial.permissions.visibility.get_opportunity_market_permission_query_conditions",
	"Opportunity Stakeholder": "api_commercial.permissions.visibility.get_opportunity_stakeholder_permission_query_conditions",
}

has_permission = {
	"CRM Organization": "api_commercial.permissions.visibility.has_crm_organization_permission",
	"Manufacturing Site": "api_commercial.permissions.visibility.has_manufacturing_site_permission",
	"Contact Affiliation": "api_commercial.permissions.visibility.has_contact_affiliation_permission",
	"Contact": "api_commercial.permissions.visibility.has_contact_permission",
	"Product Opportunity": "api_commercial.permissions.visibility.has_product_opportunity_permission",
	"Opportunity Market": "api_commercial.permissions.visibility.has_opportunity_market_permission",
	"Opportunity Stakeholder": "api_commercial.permissions.visibility.has_opportunity_stakeholder_permission",
}
```

Do not add or replace an `override_doctype_class` entry for Contact. CRM already
owns that extension through `crm.overrides.contact.CustomContact`.

The Contact query hook is safely additive to Frappe's existing
`frappe.contacts.address_and_contact.get_permission_query_conditions_for_contact`
hook. For document checks, Frappe v15 evaluates hooks in reverse registration
order and stops at the first result that is not `None`. Consequently,
`has_contact_permission` explicitly calls Frappe's existing
`frappe.contacts.address_and_contact.has_permission` rule before evaluating the
affiliation scope. This preserves the core linked-document restriction even
when the API Commercial hook is evaluated first.
