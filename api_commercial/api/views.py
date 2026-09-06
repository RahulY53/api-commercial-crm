from __future__ import annotations

from collections import Counter

import frappe
from frappe.utils import getdate, nowdate

from api_commercial.services.customers import get_descendant_customers

PAGE_LENGTH = 500
OPEN_OPPORTUNITY_STATUSES = ("Active", "On Hold")
PRICE_ROLES = {"Commercial/Pricing", "Leadership", "CRM Admin", "System Manager"}


@frappe.whitelist()
def get_my_accounts() -> list[dict]:
	accounts = frappe.get_list(
		"CRM Organization",
		fields=[
			"name",
			"organization_name as customer_name",
			"custom_region as region",
			"custom_parent_customer as parent_customer",
			"custom_is_key_account as is_key_account",
		],
		order_by="organization_name asc",
		limit_page_length=PAGE_LENGTH,
	)
	if not accounts:
		return []

	names = [account.name for account in accounts]
	primary_managers = _current_assignment_map(names, "Primary Account Manager")
	opportunities = frappe.get_all(
		"Product Opportunity",
		filters={"customer": ("in", names), "status": ("in", OPEN_OPPORTUNITY_STATUSES)},
		fields=["customer", "next_action_due_date"],
	)
	counts = Counter(row.customer for row in opportunities)
	next_due = _earliest_dates(opportunities, "customer", "next_action_due_date")

	for account in accounts:
		account.primary_account_manager = primary_managers.get(account.name)
		account.primary_account_manager_name = _display_user(account.primary_account_manager)
		account.open_opportunity_count = counts.get(account.name, 0)
		account.next_action_due = next_due.get(account.name)
	return accounts


@frappe.whitelist()
def get_my_opportunities() -> list[dict]:
	opportunities = frappe.get_list(
		"Product Opportunity",
		fields=[
			"name",
			"opportunity_name",
			"customer",
			"product",
			"region",
			"current_stage",
			"probability",
			"next_action",
			"next_action_due_date",
			"opportunity_owner",
		],
		order_by="next_action_due_date asc, modified desc",
		limit_page_length=PAGE_LENGTH,
	)
	_apply_product_names(opportunities)
	_apply_market_summary(opportunities)
	_apply_stage_names(opportunities)
	_apply_user_names(opportunities, ("opportunity_owner",))
	return opportunities


@frappe.whitelist()
def get_customer_360(customer: str) -> dict:
	doc = frappe.get_doc("CRM Organization", customer)
	doc.check_permission("read")

	visible_family = _visible_customer_family(doc.name)
	opportunities = frappe.get_list(
		"Product Opportunity",
		filters={"customer": ("in", visible_family)},
		fields=[
			"name",
			"opportunity_name",
			"customer",
			"product",
			"current_stage",
			"probability",
			"opportunity_owner",
			"next_action",
			"next_action_due_date",
			"status",
		],
		order_by="modified desc",
		limit_page_length=PAGE_LENGTH,
	)
	_apply_product_names(opportunities)
	_apply_stage_names(opportunities)
	_apply_user_names(opportunities, ("opportunity_owner",))
	estimated_potential = _estimated_potential(opportunities)

	sites = frappe.get_list(
		"Manufacturing Site",
		filters={"customer": ("in", visible_family)},
		fields=["name", "site_name", "customer", "site_type", "city", "country", "active"],
		order_by="customer asc, site_name asc",
		limit_page_length=PAGE_LENGTH,
	)
	affiliations = frappe.get_list(
		"Contact Affiliation",
		filters={"customer": ("in", visible_family), "active": 1},
		fields=[
			"name",
			"contact",
			"customer",
			"affiliation_type",
			"manufacturing_site",
			"designation",
			"department",
			"role",
		],
		order_by="customer asc, contact asc",
		limit_page_length=PAGE_LENGTH,
	)
	_apply_contact_names(affiliations)

	primary_manager = _current_assignment_map([doc.name], "Primary Account Manager").get(doc.name)
	global_manager = _global_account_manager(doc.name)
	region_head = _region_head(doc.custom_region)
	today = getdate(nowdate())

	return {
		"customer": {
			"name": doc.name,
			"customer_name": doc.organization_name,
			"region": doc.custom_region,
			"parent_customer": doc.custom_parent_customer,
			"primary_account_manager": _display_user(primary_manager),
			"global_account_manager": _display_user(global_manager),
			"region_head": _display_user(region_head),
			"status": doc.custom_customer_status,
			"is_key_account": doc.custom_is_key_account,
		},
		"summary": {
			"open_opportunities": sum(
				1 for opportunity in opportunities if opportunity.status in OPEN_OPPORTUNITY_STATUSES
			),
			"manufacturing_sites": len(sites),
			"contacts": len({affiliation.contact for affiliation in affiliations}),
			"next_actions_due": sum(
				1
				for opportunity in opportunities
				if opportunity.next_action_due_date
				and getdate(opportunity.next_action_due_date) <= today
				and opportunity.status in OPEN_OPPORTUNITY_STATUSES
			),
			"estimated_potential": estimated_potential,
		},
		"hierarchy": _customer_hierarchy_rows(doc.name, visible_family),
		"opportunities": opportunities,
		"affiliations": affiliations,
		"sites": sites,
	}


@frappe.whitelist()
def get_product_opportunity_360(opportunity: str) -> dict:
	doc = frappe.get_doc("Product Opportunity", opportunity)
	doc.check_permission("read")

	market_fields = [
		"name",
		"target_market",
		"estimated_annual_volume",
		"volume_uom",
		"probability_override as probability",
		"expected_launch_date",
	]
	if PRICE_ROLES.intersection(frappe.get_roles()):
		market_fields.extend(["expected_selling_price", "expected_revenue"])

	markets = frappe.get_list(
		"Opportunity Market",
		filters={"opportunity": doc.name},
		fields=market_fields,
		order_by="target_market asc",
		limit_page_length=PAGE_LENGTH,
	)
	for market in markets:
		market.setdefault("expected_selling_price", None)
		market.setdefault("expected_revenue", None)
		market.probability = market.probability if market.probability is not None else doc.probability

	stakeholders = frappe.get_list(
		"Opportunity Stakeholder",
		filters={"opportunity": doc.name},
		fields=[
			"name",
			"contact_affiliation as affiliation",
			"opportunity_role",
			"influence",
			"sentiment",
			"decision_power",
			"primary_contact",
		],
		order_by="primary_contact desc, modified desc",
		limit_page_length=PAGE_LENGTH,
	)
	_apply_stakeholder_details(stakeholders)

	product = frappe.db.get_value(
		"CRM Product", doc.product, ["product_name", "custom_molecule"], as_dict=True
	) or frappe._dict()
	product_owner = _current_product_owner(doc.product)
	stage_name = frappe.db.get_value("Pipeline Stage", doc.current_stage, "stage_name")

	return {
		"opportunity": {
			"name": doc.name,
			"opportunity_name": doc.opportunity_name,
			"customer": doc.customer,
			"product": doc.product,
			"product_name": product.product_name or doc.product,
			"molecule": product.custom_molecule,
			"current_stage": doc.current_stage,
			"current_stage_name": stage_name or doc.current_stage,
			"probability": doc.probability,
			"region": doc.region,
			"opportunity_owner": _display_user(doc.opportunity_owner),
			"product_owner": _display_user(product_owner),
			"global_account_manager": _display_user(_global_account_manager(doc.customer)),
			"manufacturing_site": doc.manufacturing_site,
			"next_action": doc.next_action,
			"next_action_due_date": doc.next_action_due_date,
			"notes": doc.notes,
		},
		"markets": markets,
		"stakeholders": stakeholders,
	}


def _visible_customer_family(customer: str) -> list[str]:
	potential = set(get_descendant_customers(customer, include_self=True))
	current = frappe.db.get_value("CRM Organization", customer, "custom_parent_customer")
	while current and current not in potential:
		potential.add(current)
		current = frappe.db.get_value("CRM Organization", current, "custom_parent_customer")

	# Ancestors are returned as limited hierarchy context. Every child query is
	# still intersected with its own server-side permission condition.
	return sorted(potential)


def _customer_hierarchy_rows(current: str, visible_family: list[str]) -> list[dict]:
	fields = [
		"name",
		"organization_name as customer_name",
		"custom_parent_customer as parent_customer",
		"custom_region as region",
	]

	# Descendants remain subject to normal record permissions. Ancestors are a
	# deliberately limited exception: their basic identity is needed to render
	# the selected customer's lineage, but no ancestor-owned commercial records
	# are loaded by the surrounding Customer 360 queries.
	rows = frappe.get_list(
		"CRM Organization",
		filters={"name": ("in", visible_family)},
		fields=fields,
	)
	ancestor_names = []
	parent = frappe.db.get_value("CRM Organization", current, "custom_parent_customer")
	while parent and parent not in ancestor_names:
		ancestor_names.append(parent)
		parent = frappe.db.get_value("CRM Organization", parent, "custom_parent_customer")
	loaded_names = {row.name for row in rows}
	missing_ancestors = [name for name in ancestor_names if name not in loaded_names]
	if missing_ancestors:
		rows.extend(
			frappe.get_all(
				"CRM Organization",
				filters={"name": ("in", missing_ancestors)},
				fields=fields,
			)
		)
	by_name = {row.name: row for row in rows}
	for row in rows:
		level = 0
		parent = row.parent_customer
		seen = {row.name}
		while parent and parent in by_name and parent not in seen:
			seen.add(parent)
			level += 1
			parent = by_name[parent].parent_customer
		row.level = level
		row.current = row.name == current
	return sorted(rows, key=lambda row: (row.level, row.customer_name))


def _current_assignment_map(customers: list[str], assignment_type: str) -> dict[str, str]:
	if not customers:
		return {}
	rows = frappe.get_all(
		"Account Assignment",
		filters={
			"customer": ("in", customers),
			"assignment_type": assignment_type,
			"active": 1,
		},
		fields=["customer", "user", "primary", "start_date", "end_date"],
		order_by="`primary` desc, modified desc",
	)
	result = {}
	for row in rows:
		if _is_current(row) and row.customer not in result:
			result[row.customer] = row.user
	return result


def _global_account_manager(customer: str) -> str | None:
	lineage = [customer]
	parent = frappe.db.get_value("CRM Organization", customer, "custom_parent_customer")
	while parent and parent not in lineage:
		lineage.append(parent)
		parent = frappe.db.get_value("CRM Organization", parent, "custom_parent_customer")
	assignments = _current_assignment_map(lineage, "Global Account Manager")
	return next((assignments[name] for name in reversed(lineage) if name in assignments), None)


def _region_head(region: str | None) -> str | None:
	if not region:
		return None
	lineage = [region]
	parent = frappe.db.get_value("Region", region, "parent_region")
	while parent and parent not in lineage:
		lineage.append(parent)
		parent = frappe.db.get_value("Region", parent, "parent_region")
	rows = frappe.get_all(
		"Region Membership",
		filters={
			"region": ("in", lineage),
			"membership_role": "Region Head",
			"active": 1,
		},
		fields=["region", "user", "primary_region", "start_date", "end_date"],
		order_by="primary_region desc, modified desc",
	)
	return next((row.user for row in rows if _is_current(row)), None)


def _current_product_owner(product: str) -> str | None:
	rows = frappe.get_all(
		"Product Responsibility",
		filters={"product": product, "active": 1},
		fields=["user", "primary_responsibility", "start_date", "end_date"],
		order_by="primary_responsibility desc, modified desc",
	)
	return next((row.user for row in rows if _is_current(row)), None)


def _is_current(row) -> bool:
	today = getdate(nowdate())
	return (not row.start_date or getdate(row.start_date) <= today) and (
		not row.end_date or getdate(row.end_date) >= today
	)


def _earliest_dates(rows: list, group_field: str, date_field: str) -> dict[str, str]:
	result = {}
	for row in rows:
		value = row.get(date_field)
		group = row.get(group_field)
		if value and (group not in result or getdate(value) < getdate(result[group])):
			result[group] = value
	return result


def _apply_product_names(rows: list):
	products = {row.product for row in rows if row.product}
	if not products:
		return
	name_map = {
		row.name: row.product_name
		for row in frappe.get_all(
			"CRM Product", filters={"name": ("in", list(products))}, fields=["name", "product_name"]
		)
	}
	for row in rows:
		row.product_name = name_map.get(row.product, row.product)


def _apply_stage_names(rows: list):
	stages = {row.current_stage for row in rows if row.current_stage}
	if not stages:
		return
	name_map = {
		row.name: row.stage_name
		for row in frappe.get_all(
			"Pipeline Stage", filters={"name": ("in", list(stages))}, fields=["name", "stage_name"]
		)
	}
	for row in rows:
		row.current_stage_name = name_map.get(row.current_stage, row.current_stage)


def _apply_user_names(rows: list, fields: tuple[str, ...]):
	users = {row.get(field) for row in rows for field in fields if row.get(field)}
	if not users:
		return
	name_map = {
		row.name: row.full_name
		for row in frappe.get_all(
			"User", filters={"name": ("in", list(users))}, fields=["name", "full_name"]
		)
	}
	for row in rows:
		for field in fields:
			value = row.get(field)
			row[f"{field}_name"] = name_map.get(value, value)


def _display_user(user: str | None) -> str | None:
	if not user:
		return None
	return frappe.db.get_value("User", user, "full_name") or user


def _apply_market_summary(rows: list):
	opportunities = [row.name for row in rows]
	if not opportunities:
		return
	fields = ["opportunity", "target_market"]
	show_potential = bool(PRICE_ROLES.intersection(frappe.get_roles()))
	if show_potential:
		fields.append("expected_revenue")
	markets = frappe.get_list(
		"Opportunity Market",
		filters={"opportunity": ("in", opportunities)},
		fields=fields,
		limit_page_length=PAGE_LENGTH,
	)
	by_opportunity: dict[str, list] = {}
	for market in markets:
		by_opportunity.setdefault(market.opportunity, []).append(market)
	for row in rows:
		market_rows = by_opportunity.get(row.name, [])
		row.target_markets = ", ".join(sorted(market.target_market for market in market_rows))
		row.estimated_potential = (
			sum(float(market.expected_revenue or 0) for market in market_rows)
			if show_potential
			else None
		)


def _estimated_potential(opportunities: list) -> float | None:
	if not PRICE_ROLES.intersection(frappe.get_roles()):
		return None
	names = [row.name for row in opportunities]
	if not names:
		return 0
	markets = frappe.get_list(
		"Opportunity Market",
		filters={"opportunity": ("in", names)},
		fields=["expected_revenue"],
		limit_page_length=PAGE_LENGTH,
	)
	return sum(float(market.expected_revenue or 0) for market in markets)


def _apply_contact_names(rows: list):
	contacts = {row.contact for row in rows if row.contact}
	if not contacts:
		return
	name_map = {
		row.name: row.full_name
		for row in frappe.get_all(
			"Contact", filters={"name": ("in", list(contacts))}, fields=["name", "full_name"]
		)
	}
	for row in rows:
		row.contact_name = name_map.get(row.contact, row.contact)


def _apply_stakeholder_details(rows: list):
	affiliation_names = {row.affiliation for row in rows if row.affiliation}
	if not affiliation_names:
		return
	affiliations = frappe.get_all(
		"Contact Affiliation",
		filters={"name": ("in", list(affiliation_names))},
		fields=["name", "contact", "designation", "customer", "manufacturing_site"],
	)
	by_name = {row.name: row for row in affiliations}
	contacts = {row.contact for row in affiliations if row.contact}
	contact_names = {
		row.name: row.full_name
		for row in frappe.get_all(
			"Contact", filters={"name": ("in", list(contacts))}, fields=["name", "full_name"]
		)
	}
	for row in rows:
		affiliation = by_name.get(row.affiliation, frappe._dict())
		row.contact_name = contact_names.get(affiliation.contact, affiliation.contact)
		row.designation = affiliation.designation
		row.affiliation_customer = affiliation.customer
		row.manufacturing_site = affiliation.manufacturing_site
