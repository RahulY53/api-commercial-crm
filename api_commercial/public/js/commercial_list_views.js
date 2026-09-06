(() => {
	function enhance(doctype, options) {
		const existing = frappe.listview_settings[doctype] || {};
		if (existing.__apiCommercialEnhanced) return;

		const originalOnload = existing.onload;
		frappe.listview_settings[doctype] = {
			...existing,
			...options,
			onload(listview) {
				originalOnload?.(listview);
				listview.page?.set_title(__(options.pageTitle));
			},
			__apiCommercialEnhanced: true,
		};
	}

	enhance("CRM Organization", {
		pageTitle: "Customers",
		add_fields: [
			"organization_name",
			"custom_account_type",
			"custom_region",
			"custom_customer_status",
			"custom_is_key_account",
		],
		hide_name_column: true,
	});

	enhance("Manufacturing Site", {
		pageTitle: "Manufacturing Sites",
		add_fields: ["site_name", "customer", "site_type", "city", "country", "active"],
		hide_name_column: true,
		get_indicator: (doc) =>
			doc.active ? [__("Active"), "green", "active,=,1"] : [__("Inactive"), "gray", "active,=,0"],
	});

	enhance("Contact Affiliation", {
		pageTitle: "Contact Affiliations",
		add_fields: [
			"contact",
			"affiliation_type",
			"customer",
			"manufacturing_site",
			"designation",
			"active",
		],
		hide_name_column: true,
		get_indicator: (doc) =>
			doc.active ? [__("Active"), "green", "active,=,1"] : [__("Inactive"), "gray", "active,=,0"],
	});

	enhance("CRM Product", {
		pageTitle: "Products",
		add_fields: [
			"product_name",
			"custom_molecule",
			"custom_product_category",
			"custom_therapeutic_area",
			"custom_commercial_status",
			"disabled",
		],
		hide_name_column: true,
	});

	enhance("Product Opportunity", {
		pageTitle: "Product Opportunities",
		add_fields: [
			"opportunity_name",
			"customer",
			"product",
			"current_stage",
			"probability",
			"status",
			"next_action_due_date",
		],
		hide_name_column: true,
		get_indicator(doc) {
			const colors = { Active: "blue", "On Hold": "orange", Won: "green", Lost: "red" };
			return [__(doc.status || "Unknown"), colors[doc.status] || "gray", `status,=,${doc.status}`];
		},
	});
})();
