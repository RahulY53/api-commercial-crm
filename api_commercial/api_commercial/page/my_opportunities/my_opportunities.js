frappe.pages["my-opportunities"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("My Opportunities"),
		single_column: true,
	});
	page.set_primary_action(__("Refresh"), () => loadOpportunities(wrapper), "refresh");
};

frappe.pages["my-opportunities"].on_page_show = loadOpportunities;

function loadOpportunities(wrapper) {
	const ui = window.apiCommercialUI;
	return ui.load(wrapper, "api_commercial.api.views.get_my_opportunities", {}, (rows) =>
		ui.table(
			[
				{
					label: __("Opportunity"),
					render: (row) =>
						ui.link(
							row.opportunity_name,
							`/app/product-opportunity-360/${encodeURIComponent(row.name)}`
						),
				},
				{ label: __("Customer"), key: "customer" },
				{ label: __("Product"), key: "product_name" },
				{ label: __("Target Markets"), key: "target_markets" },
				{ label: __("Estimated Potential"), key: "estimated_potential" },
				{ label: __("Region"), key: "region" },
				{ label: __("Stage"), render: (row) => ui.pill(row.current_stage_name) },
				{
					label: __("Probability"),
					render: (row) => `${ui.escape(row.probability ?? 0)}%`,
				},
				{ label: __("Next Action"), key: "next_action" },
				{ label: __("Due"), key: "next_action_due_date" },
				{ label: __("Owner"), key: "opportunity_owner_name" },
			],
			rows,
			__("My Opportunities")
		)
	);
}
