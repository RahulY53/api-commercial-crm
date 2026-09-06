frappe.pages["product-opportunity-360"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Product Opportunity 360"),
		single_column: true,
	});
};

frappe.pages["product-opportunity-360"].on_page_show = function (wrapper) {
	const opportunity = frappe.get_route()[1];
	const ui = window.apiCommercialUI;
	if (!opportunity) {
		wrapper.page?.set_title(__("Product Opportunity 360"));
		ui.message(wrapper, __("Select a Product Opportunity to open this view."));
		return;
	}
	return ui.load(
		wrapper,
		"api_commercial.api.views.get_product_opportunity_360",
		{ opportunity },
		(data) => {
			wrapper.page?.set_title(data.opportunity.opportunity_name);
			return [
				ui.details([
					{ label: __("Customer"), value: data.opportunity.customer },
					{ label: __("Product"), value: data.opportunity.product_name },
					{ label: __("Stage"), html: ui.pill(data.opportunity.current_stage) },
					{ label: __("Probability"), value: `${data.opportunity.probability ?? 0}%` },
					{ label: __("Region"), value: data.opportunity.region },
					{ label: __("Owner"), value: data.opportunity.opportunity_owner },
					{ label: __("Product Owner"), value: data.opportunity.product_owner },
					{
						label: __("Global Account Manager"),
						value: data.opportunity.global_account_manager,
					},
					{ label: __("Next Action"), value: data.opportunity.next_action },
					{ label: __("Next Action Due"), value: data.opportunity.next_action_due_date },
				]),
				`<section><h2 class="api-commercial-section-title">${ui.escape(
					__("Markets")
				)}</h2>${ui.table(
					[
						{ label: __("Target Market"), key: "target_market" },
						{ label: __("Annual Volume"), key: "estimated_annual_volume" },
						{ label: __("UOM"), key: "volume_uom" },
						{ label: __("Expected Selling Price"), key: "expected_selling_price" },
						{ label: __("Expected Revenue"), key: "expected_revenue" },
						{ label: __("Probability"), key: "probability" },
						{ label: __("Launch Date"), key: "expected_launch_date" },
					],
					data.markets,
					__("Markets")
				)}</section>`,
				`<section><h2 class="api-commercial-section-title">${ui.escape(
					__("Stakeholders")
				)}</h2>${ui.table(
					[
						{ label: __("Contact"), key: "contact_name" },
						{ label: __("Affiliation"), key: "affiliation" },
						{ label: __("Designation"), key: "designation" },
						{ label: __("Opportunity Role"), key: "opportunity_role" },
						{ label: __("Influence"), key: "influence" },
						{ label: __("Sentiment"), key: "sentiment" },
					],
					data.stakeholders,
					__("Stakeholders")
				)}</section>`,
			].join("");
		}
	);
};
