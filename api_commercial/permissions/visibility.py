"""Additive, server-side record visibility for Phase 1 commercial records.

Frappe role permissions remain the action boundary. These hooks only narrow a
user's record set; a ``True`` result cannot grant an action missing from the
DocType's role permissions.
"""

from __future__ import annotations

import frappe
from frappe.contacts.address_and_contact import has_permission as frappe_contact_has_permission
from frappe.utils import getdate, nowdate

ADMIN_ROLES = frozenset({"System Manager", "CRM Admin"})
LEADERSHIP_ROLE = "Leadership"
READ_PERMISSION_TYPES = frozenset({"read", "select", "email", "print", "export", "report"})

ACCOUNT_MANAGER_ROLE = "Account Manager"
REGION_HEAD_ROLE = "Region Head"
GLOBAL_ACCOUNT_MANAGER_ROLE = "Global Account Manager"
PRODUCT_MANAGER_ROLE = "Product Manager"
BUSINESS_DEVELOPMENT_ROLE = "Business Development"

_TABLE_BY_DOCTYPE = {
	"CRM Organization": "`tabCRM Organization`",
	"Manufacturing Site": "`tabManufacturing Site`",
	"Contact Affiliation": "`tabContact Affiliation`",
	"Contact": "`tabContact`",
	"Product Opportunity": "`tabProduct Opportunity`",
	"Opportunity Market": "`tabOpportunity Market`",
	"Opportunity Stakeholder": "`tabOpportunity Stakeholder`",
}


def _user(user: str | None) -> str:
	return user or frappe.session.user


def _roles(user: str) -> frozenset[str]:
	return frozenset(frappe.get_roles(user))


def _is_administrator(user: str, roles: frozenset[str]) -> bool:
	return user == "Administrator" or bool(ADMIN_ROLES & roles)


def _literal(value: object) -> str:
	"""Quote a hook value with the active database driver's escaping rules.

	Frappe v15 permission query hooks return a SQL fragment and provide no
	separate values channel. Keeping every value behind this helper is the safe
	supported pattern for those fragments. Normal record checks still bind the
	document name as a query parameter.
	"""

	return frappe.db.escape(str(value), percent=False)


def _active_window(alias: str, on_date: str) -> str:
	date_literal = _literal(getdate(on_date).isoformat())
	return (
		f"{alias}.`active` = 1"
		f" AND ({alias}.`start_date` IS NULL OR {alias}.`start_date` <= {date_literal})"
		f" AND ({alias}.`end_date` IS NULL OR {alias}.`end_date` >= {date_literal})"
	)


def _in_literals(values: list[str]) -> str:
	return ", ".join(_literal(value) for value in values)


def _gam_customer_names(user: str, on_date: str) -> list[str]:
	"""Resolve cascading account assignments through the Customer adjacency tree.

	Customer hierarchy is intentionally stored on CRM Organization rather than
	as a nested set. Resolution is iterative and cycle-safe; each database call
	uses Frappe filters or bound parameters.
	"""

	today = getdate(on_date).isoformat()
	roots = frappe.db.sql(
		"""
		SELECT DISTINCT assignment.`customer`
		FROM `tabAccount Assignment` assignment
		INNER JOIN `tabAccount Assignment Type` assignment_type
			ON assignment_type.`name` = assignment.`assignment_type`
		WHERE assignment.`user` = %s
			AND assignment.`active` = 1
			AND (assignment.`start_date` IS NULL OR assignment.`start_date` <= %s)
			AND (assignment.`end_date` IS NULL OR assignment.`end_date` >= %s)
			AND assignment_type.`active` = 1
			AND assignment_type.`cascade_to_descendants` = 1
		""",
		(user, today, today),
		pluck=True,
	)

	seen = set(roots)
	frontier = list(roots)
	while frontier:
		children = frappe.get_all(
			"CRM Organization",
			filters={"custom_parent_customer": ("in", frontier)},
			pluck="name",
		)
		frontier = [name for name in children if name not in seen]
		seen.update(frontier)

	return sorted(seen)


def _customer_scope_condition(
	customer_expression: str,
	user: str,
	roles: frozenset[str],
	on_date: str,
) -> str:
	clauses: list[str] = []
	user_literal = _literal(user)

	# A direct assignment is an additive access route. Role permissions still
	# decide which operations the user may perform on the target DocType.
	clauses.append(
		"EXISTS ("
		"SELECT 1 FROM `tabAccount Assignment` am_assignment "
		"INNER JOIN `tabAccount Assignment Type` am_assignment_type "
			"ON am_assignment_type.`name` = am_assignment.`assignment_type` "
		f"WHERE am_assignment.`customer` = {customer_expression} "
		f"AND am_assignment.`user` = {user_literal} "
		"AND am_assignment_type.`active` = 1 "
		f"AND {_active_window('am_assignment', on_date)}"
		")"
	)

	if REGION_HEAD_ROLE in roles:
		clauses.append(
			"EXISTS ("
			"SELECT 1 FROM `tabRegion Membership` region_membership "
			"INNER JOIN `tabRegion Membership Role` membership_role "
				"ON membership_role.`name` = region_membership.`membership_role` "
			"INNER JOIN `tabRegion` managed_region "
				"ON managed_region.`name` = region_membership.`region` "
			"INNER JOIN `tabCRM Organization` region_customer "
				f"ON region_customer.`name` = {customer_expression} "
			"INNER JOIN `tabRegion` customer_region "
				"ON customer_region.`name` = region_customer.`custom_region` "
			f"WHERE region_membership.`user` = {user_literal} "
			f"AND region_membership.`membership_role` = {_literal(REGION_HEAD_ROLE)} "
			"AND membership_role.`active` = 1 "
			f"AND {_active_window('region_membership', on_date)} "
			"AND managed_region.`active` = 1 "
			"AND customer_region.`active` = 1 "
			"AND customer_region.`lft` >= managed_region.`lft` "
			"AND customer_region.`rgt` <= managed_region.`rgt`"
			")"
		)

	if GLOBAL_ACCOUNT_MANAGER_ROLE in roles:
		customers = _gam_customer_names(user, on_date)
		if customers:
			clauses.append(f"{customer_expression} IN ({_in_literals(customers)})")

	return "(" + " OR ".join(clauses) + ")" if clauses else "(1 = 0)"


def _organization_condition(
	customer_expression: str, user: str, roles: frozenset[str], on_date: str
) -> str:
	clauses = [_customer_scope_condition(customer_expression, user, roles, on_date)]
	if BUSINESS_DEVELOPMENT_ROLE in roles:
		customer_alias = customer_expression.removesuffix(".`name`")
		clauses.append(
			f"({customer_alias}.`owner` = {_literal(user)} "
			f"AND {customer_alias}.`custom_account_type` = 'Prospect')"
		)
	return "(" + " OR ".join(clauses) + ")"


def _affiliation_scope_condition(
	affiliation_alias: str, user: str, roles: frozenset[str], on_date: str
) -> str:
	"""Allow customer-scoped affiliations and affiliations used on visible opportunities."""

	return (
		"("
		f"{_customer_scope_condition(f'{affiliation_alias}.`customer`', user, roles, on_date)} "
		"OR EXISTS ("
		"SELECT 1 FROM `tabOpportunity Stakeholder` scoped_stakeholder "
		"INNER JOIN `tabProduct Opportunity` stakeholder_opportunity "
			"ON stakeholder_opportunity.`name` = scoped_stakeholder.`opportunity` "
		f"WHERE scoped_stakeholder.`contact_affiliation` = {affiliation_alias}.`name` "
		f"AND {_opportunity_scope_condition('stakeholder_opportunity', user, roles, on_date, True)}"
		")"
		")"
	)


def _opportunity_scope_condition(
	opportunity_alias: str,
	user: str,
	roles: frozenset[str],
	on_date: str,
	include_product_scope: bool,
) -> str:
	clauses = [_customer_scope_condition(f"{opportunity_alias}.`customer`", user, roles, on_date)]
	clauses.append(f"{opportunity_alias}.`opportunity_owner` = {_literal(user)}")
	if include_product_scope and PRODUCT_MANAGER_ROLE in roles:
		clauses.append(
			"EXISTS ("
			"SELECT 1 FROM `tabProduct Responsibility` product_responsibility "
			f"WHERE product_responsibility.`product` = {opportunity_alias}.`product` "
			f"AND product_responsibility.`user` = {_literal(user)} "
			f"AND {_active_window('product_responsibility', on_date)}"
			")"
		)
	return "(" + " OR ".join(clauses) + ")"


def _scope_context(user: str | None) -> tuple[str, frozenset[str], str]:
	resolved_user = _user(user)
	return resolved_user, _roles(resolved_user), nowdate()


def _broad_query_access(user: str, roles: frozenset[str]) -> bool:
	return _is_administrator(user, roles) or LEADERSHIP_ROLE in roles


def get_crm_organization_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return _organization_condition("`tabCRM Organization`.`name`", user, roles, today)


def get_manufacturing_site_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return _customer_scope_condition("`tabManufacturing Site`.`customer`", user, roles, today)


def get_contact_affiliation_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return _affiliation_scope_condition("`tabContact Affiliation`", user, roles, today)


def get_contact_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return (
		"EXISTS ("
		"SELECT 1 FROM `tabContact Affiliation` visible_affiliation "
		"WHERE visible_affiliation.`contact` = `tabContact`.`name` "
		f"AND {_active_window('visible_affiliation', today)} "
		f"AND {_affiliation_scope_condition('visible_affiliation', user, roles, today)}"
		")"
	)


def get_product_opportunity_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return _opportunity_scope_condition(
		"`tabProduct Opportunity`", user, roles, today, include_product_scope=True
	)


def _opportunity_child_condition(table: str, user: str, roles: frozenset[str], today: str) -> str:
	return (
		"EXISTS ("
		"SELECT 1 FROM `tabProduct Opportunity` inherited_opportunity "
		f"WHERE inherited_opportunity.`name` = {table}.`opportunity` "
		f"AND {_opportunity_scope_condition('inherited_opportunity', user, roles, today, True)}"
		")"
	)


def get_opportunity_market_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return _opportunity_child_condition("`tabOpportunity Market`", user, roles, today)


def get_opportunity_stakeholder_permission_query_conditions(user=None, doctype=None) -> str:
	user, roles, today = _scope_context(user)
	if _broad_query_access(user, roles):
		return ""
	return _opportunity_child_condition("`tabOpportunity Stakeholder`", user, roles, today)


def _record_scope_condition(
	doctype: str, user: str, roles: frozenset[str], today: str, include_product_scope: bool
) -> str:
	"""Build the same policy against the ``scoped_record`` query alias."""

	if doctype == "CRM Organization":
		return _organization_condition("scoped_record.`name`", user, roles, today)
	if doctype == "Manufacturing Site":
		return _customer_scope_condition("scoped_record.`customer`", user, roles, today)
	if doctype == "Contact Affiliation":
		return _affiliation_scope_condition("scoped_record", user, roles, today)
	if doctype == "Contact":
		return (
			"EXISTS (SELECT 1 FROM `tabContact Affiliation` visible_affiliation "
			"WHERE visible_affiliation.`contact` = scoped_record.`name` "
			f"AND {_active_window('visible_affiliation', today)} "
			f"AND {_affiliation_scope_condition('visible_affiliation', user, roles, today)})"
		)
	if doctype == "Product Opportunity":
		return _opportunity_scope_condition(
			"scoped_record", user, roles, today, include_product_scope=include_product_scope
		)
	if doctype in {"Opportunity Market", "Opportunity Stakeholder"}:
		return (
			"EXISTS (SELECT 1 FROM `tabProduct Opportunity` inherited_opportunity "
			"WHERE inherited_opportunity.`name` = scoped_record.`opportunity` "
			f"AND {_opportunity_scope_condition('inherited_opportunity', user, roles, today, include_product_scope)})"
		)
	return "(1 = 0)"


def _has_scoped_permission(doc, ptype: str, user: str | None, doctype: str) -> bool | None:
	user = _user(user)
	roles = _roles(user)

	if _is_administrator(user, roles):
		return True
	if ptype == "create" or not doc.get("name"):
		return _has_create_scope(doc, user, roles, doctype)
	if LEADERSHIP_ROLE in roles:
		return ptype in READ_PERMISSION_TYPES

	condition = _record_scope_condition(
		doctype,
		user,
		roles,
		nowdate(),
		include_product_scope=ptype in READ_PERMISSION_TYPES,
	)

	rows = frappe.db.sql(
		f"SELECT scoped_record.`name` FROM {_TABLE_BY_DOCTYPE[doctype]} scoped_record "
		f"WHERE scoped_record.`name` = %s AND ({condition}) LIMIT 1",
		(doc.name,),
	)
	return bool(rows)


def _has_create_scope(
	doc, user: str, roles: frozenset[str], doctype: str
) -> bool | None:
	"""Require new dependent records to have an editable authorized parent."""

	if doctype == "CRM Organization":
		if BUSINESS_DEVELOPMENT_ROLE in roles:
			return doc.get("custom_account_type") == "Prospect"
		return None

	if doctype == "Contact":
		return None

	if doctype in {"Manufacturing Site", "Contact Affiliation", "Product Opportunity"}:
		if not (customer := doc.get("customer")):
			return False
		return frappe.has_permission("CRM Organization", "write", doc=customer, user=user)

	if doctype in {"Opportunity Market", "Opportunity Stakeholder"}:
		if not (opportunity := doc.get("opportunity")):
			return False
		return frappe.has_permission("Product Opportunity", "write", doc=opportunity, user=user)

	return False


def has_crm_organization_permission(doc, ptype="read", user=None, debug=False):
	return _has_scoped_permission(doc, ptype, user, "CRM Organization")


def has_manufacturing_site_permission(doc, ptype="read", user=None, debug=False):
	return _has_scoped_permission(doc, ptype, user, "Manufacturing Site")


def has_contact_affiliation_permission(doc, ptype="read", user=None, debug=False):
	return _has_scoped_permission(doc, ptype, user, "Contact Affiliation")


def has_product_opportunity_permission(doc, ptype="read", user=None, debug=False):
	return _has_scoped_permission(doc, ptype, user, "Product Opportunity")


def has_opportunity_market_permission(doc, ptype="read", user=None, debug=False):
	return _has_scoped_permission(doc, ptype, user, "Opportunity Market")


def has_opportunity_stakeholder_permission(doc, ptype="read", user=None, debug=False):
	return _has_scoped_permission(doc, ptype, user, "Opportunity Stakeholder")


def has_contact_permission(doc, ptype="read", user=None, debug=False):
	"""Preserve Frappe's Contact-link rule, then apply affiliation scope.

	Frappe v15 evaluates document hooks in reverse registration order and stops
	at the first conclusive result. Because this app's hook runs before Frappe's,
	we explicitly execute the core rule instead of accidentally shadowing it.
	CRM's ``CustomContact`` class override is unrelated and remains untouched.
	"""

	core_result = frappe_contact_has_permission(doc, ptype, _user(user))
	if core_result is False:
		return False
	return _has_scoped_permission(doc, ptype, user, "Contact")
