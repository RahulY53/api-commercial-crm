frappe.pages["my-accounts"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("My Accounts"),
		single_column: true,
	});
	page.set_primary_action(__("Refresh"), () => loadAccounts(wrapper), "refresh");
};

frappe.pages["my-accounts"].on_page_show = loadAccounts;

function loadAccounts(wrapper) {
	const ui = window.apiCommercialUI;
	return ui.load(wrapper, "api_commercial.api.views.get_my_accounts", {}, (rows) =>
		ui.table(
			[
				{
					label: __("Account"),
					render: (row) =>
						ui.link(
							row.customer_name,
							`/app/customer-360/${encodeURIComponent(row.name)}`
						),
				},
				{ label: __("Region"), key: "region" },
				{ label: __("Parent Account"), key: "parent_customer" },
				{ label: __("Primary AM"), key: "primary_account_manager_name" },
				{ label: __("Open Opportunities"), key: "open_opportunity_count" },
				{ label: __("Next Action Due"), key: "next_action_due" },
				{
					label: __("Key Account"),
					render: (row) => ui.pill(row.is_key_account ? __("Yes") : __("No")),
				},
			],
			rows,
			__("My Accounts")
		)
	);
}
