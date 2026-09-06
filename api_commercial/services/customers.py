import frappe


def validate_customer(doc, method=None):
	if doc.custom_account_type == "Operating Customer" and not doc.custom_region:
		frappe.throw("Region is required for an Operating Customer.")

	if doc.custom_region and not frappe.db.get_value("Region", doc.custom_region, "active"):
		frappe.throw("Region must be active.")

	validate_customer_parent(doc)


def validate_customer_parent(doc):
	parent = doc.custom_parent_customer
	if not parent:
		return

	current_name = doc.name or doc.organization_name
	if parent == current_name:
		frappe.throw("A Customer cannot be its own parent.")

	visited = {current_name}
	while parent:
		if parent in visited:
			frappe.throw("Customer hierarchy cannot contain a cycle.")
		visited.add(parent)
		parent = frappe.db.get_value("CRM Organization", parent, "custom_parent_customer")


def get_descendant_customers(customer: str, include_self: bool = False) -> list[str]:
	descendants = []
	frontier = [customer]
	seen = {customer}

	while frontier:
		children = frappe.get_all(
			"CRM Organization",
			filters={"custom_parent_customer": ("in", frontier)},
			pluck="name",
		)
		frontier = [child for child in children if child not in seen]
		seen.update(frontier)
		descendants.extend(frontier)

	return ([customer] if include_self else []) + descendants
