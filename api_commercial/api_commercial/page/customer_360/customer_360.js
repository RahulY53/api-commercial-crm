frappe.pages["customer-360"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({ parent: wrapper, title: __("Customer 360"), single_column: true });
};

frappe.pages["customer-360"].on_page_show = function (wrapper) {
	const customer = frappe.get_route()[1];
	const ui = window.apiCommercialUI;
	if (!customer) {
		wrapper.page?.set_title(__("Customer 360"));
		ui.message(wrapper, __("Select a Customer to open Customer 360."));
		return;
	}
	return ui.load(wrapper, "api_commercial.api.views.get_customer_360", { customer }, (data) => {
		wrapper.page?.set_title(data.customer.customer_name);
		return [
			ui.details([
				{ label: __("Region"), value: data.customer.region },
				{ label: __("Parent Account"), value: data.customer.parent_customer },
				{ label: __("Primary AM"), value: data.customer.primary_account_manager },
				{
					label: __("Global Account Manager"),
					value: data.customer.global_account_manager,
				},
				{ label: __("Region Head"), value: data.customer.region_head },
				{ label: __("Status"), html: ui.pill(data.customer.status) },
			]),
			ui.metrics([
				{ label: __("Open Opportunities"), value: data.summary.open_opportunities },
				{ label: __("Manufacturing Sites"), value: data.summary.manufacturing_sites },
				{ label: __("Contacts"), value: data.summary.contacts },
				{ label: __("Next Actions Due"), value: data.summary.next_actions_due },
				...(data.summary.estimated_potential == null
					? []
					: [
							{
								label: __("Estimated Potential"),
								value: data.summary.estimated_potential,
							},
						]),
			]),
			`<section><h2 class="api-commercial-section-title">${ui.escape(
				__("Account hierarchy")
			)}</h2>${ui.table(
				[
					{ label: __("Customer"), key: "customer_name" },
					{ label: __("Region"), key: "region" },
					{ label: __("Level"), key: "level" },
				],
				data.hierarchy,
				__("Account hierarchy")
			)}</section>`,
			`<section><h2 class="api-commercial-section-title">${ui.escape(
				__("Product Opportunities")
			)}</h2>${ui.table(
				[
					{
						label: __("Opportunity"),
						render: (row) =>
							ui.link(
								row.opportunity_name,
								`/app/product-opportunity-360/${encodeURIComponent(row.name)}`
							),
					},
					{ label: __("Product"), key: "product_name" },
					{ label: __("Stage"), key: "current_stage" },
					{ label: __("Probability"), key: "probability" },
					{ label: __("Owner"), key: "opportunity_owner" },
					{ label: __("Next Action"), key: "next_action" },
					{ label: __("Due"), key: "next_action_due_date" },
				],
				data.opportunities,
				__("Product Opportunities")
			)}</section>`,
			`<section><h2 class="api-commercial-section-title">${ui.escape(
				__("Contacts & Affiliations")
			)}</h2>${ui.table(
				[
					{ label: __("Contact"), key: "contact_name" },
					{ label: __("Affiliation"), key: "affiliation_type" },
					{ label: __("Site"), key: "manufacturing_site" },
					{ label: __("Designation"), key: "designation" },
					{ label: __("Role"), key: "role" },
				],
				data.affiliations,
				__("Contacts & Affiliations")
			)}</section>`,
			`<section><h2 class="api-commercial-section-title">${ui.escape(
				__("Manufacturing Sites")
			)}</h2>${ui.table(
				[
					{ label: __("Site"), key: "site_name" },
					{ label: __("Type"), key: "site_type" },
					{ label: __("City"), key: "city" },
					{ label: __("Country"), key: "country" },
				],
				data.sites,
				__("Manufacturing Sites")
			)}</section>`,
		].join("");
	});
};
