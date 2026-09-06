from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial.permissions import visibility


class TestVisibilityConditions(FrappeTestCase):
	def condition_for(self, method, roles, user="scope@example.com"):
		with (
			patch.object(visibility.frappe, "get_roles", return_value=roles),
			patch.object(visibility, "nowdate", return_value="2026-09-06"),
		):
			return method(user)

	def test_account_manager_scope_is_dated_and_explicit(self):
		condition = self.condition_for(
			visibility.get_crm_organization_permission_query_conditions,
			["Account Manager"],
		)
		self.assertIn("tabAccount Assignment", condition)
		self.assertIn("am_assignment.`customer` = `tabCRM Organization`.`name`", condition)
		self.assertIn("am_assignment.`start_date`", condition)
		self.assertIn("am_assignment.`end_date`", condition)

	def test_region_head_scope_uses_region_nested_set(self):
		condition = self.condition_for(
			visibility.get_crm_organization_permission_query_conditions,
			["Region Head"],
		)
		self.assertIn("region_customer.`name` = `tabCRM Organization`.`name`", condition)
		self.assertIn("customer_region.`name` = region_customer.`custom_region`", condition)
		self.assertIn("customer_region.`lft` >= managed_region.`lft`", condition)
		self.assertIn("customer_region.`rgt` <= managed_region.`rgt`", condition)

	def test_multi_role_scope_is_additive(self):
		condition = self.condition_for(
			visibility.get_product_opportunity_permission_query_conditions,
			["Account Manager", "Product Manager"],
		)
		self.assertIn("tabAccount Assignment", condition)
		self.assertIn("tabProduct Responsibility", condition)
		self.assertIn(" OR ", condition)

	def test_leadership_and_administrators_have_unfiltered_lists(self):
		for roles in (["Leadership"], ["System Manager"], ["CRM Admin"]):
			self.assertEqual(
				self.condition_for(
					visibility.get_product_opportunity_permission_query_conditions, roles
				),
				"",
			)

	def test_direct_assignment_is_an_additive_scope_for_business_roles(self):
		condition = self.condition_for(
			visibility.get_manufacturing_site_permission_query_conditions,
			["Business Development"],
		)
		self.assertIn("tabAccount Assignment", condition)
		self.assertIn("am_assignment.`user`", condition)

	def test_children_inherit_opportunity_scope(self):
		condition = self.condition_for(
			visibility.get_opportunity_market_permission_query_conditions,
			["Product Manager"],
		)
		self.assertIn("inherited_opportunity.`name` = `tabOpportunity Market`.`opportunity`", condition)
		self.assertIn("tabProduct Responsibility", condition)

	def test_contact_list_requires_active_visible_affiliation(self):
		condition = self.condition_for(
			visibility.get_contact_permission_query_conditions,
			["Account Manager"],
		)
		self.assertIn("visible_affiliation.`contact` = `tabContact`.`name`", condition)
		self.assertIn("visible_affiliation.`active` = 1", condition)
		self.assertIn("tabAccount Assignment", condition)

	def test_installed_customer_scope_fragments_execute(self):
		cases = (
			("CRM Organization", visibility.get_crm_organization_permission_query_conditions),
			("Manufacturing Site", visibility.get_manufacturing_site_permission_query_conditions),
			("Contact Affiliation", visibility.get_contact_affiliation_permission_query_conditions),
			("Contact", visibility.get_contact_permission_query_conditions),
		)
		with (
			patch.object(visibility.frappe, "get_roles", return_value=["Account Manager", "Region Head"]),
			patch.object(visibility, "nowdate", return_value="2026-09-06"),
		):
			for doctype, method in cases:
				condition = method("scope@example.com")
				frappe.db.sql(
					f"SELECT `tab{doctype}`.`name` FROM `tab{doctype}` "
					f"WHERE {condition} LIMIT 1"
				)

	def test_gam_resolution_is_cycle_safe_and_includes_descendants(self):
		with (
			patch.object(visibility.frappe.db, "sql", return_value=["GLOBAL"]),
			patch.object(
				visibility.frappe,
				"get_all",
				side_effect=[["CHILD"], ["GLOBAL", "GRANDCHILD"], []],
			),
		):
			self.assertEqual(
				visibility._gam_customer_names("gam@example.com", "2026-09-06"),
				["CHILD", "GLOBAL", "GRANDCHILD"],
			)


class TestVisibilityDocumentChecks(FrappeTestCase):
	def test_direct_check_binds_document_name(self):
		doc = frappe._dict(name="MS-00001")
		with (
			patch.object(visibility.frappe, "get_roles", return_value=["Account Manager"]),
			patch.object(visibility, "nowdate", return_value="2026-09-06"),
			patch.object(visibility.frappe.db, "sql", return_value=[("MS-00001",)]) as sql,
		):
			self.assertTrue(visibility.has_manufacturing_site_permission(doc, "read", "am@example.com"))
			self.assertEqual(sql.call_args.args[1], ("MS-00001",))
			self.assertIn("scoped_record.`name` = %s", sql.call_args.args[0])

	def test_product_manager_responsibility_is_read_only(self):
		doc = frappe._dict(name="PO-00001")
		with (
			patch.object(visibility.frappe, "get_roles", return_value=["Product Manager"]),
			patch.object(visibility, "nowdate", return_value="2026-09-06"),
			patch.object(visibility.frappe.db, "sql", return_value=[]) as sql,
		):
			self.assertFalse(visibility.has_product_opportunity_permission(doc, "write", "pm@example.com"))
			self.assertNotIn("tabProduct Responsibility", sql.call_args.args[0])

	def test_contact_hook_executes_core_rule_first(self):
		doc = frappe._dict(name="CONTACT-00001")
		with patch.object(visibility, "frappe_contact_has_permission", return_value=False) as core:
			self.assertFalse(visibility.has_contact_permission(doc, "read", "am@example.com"))
			core.assert_called_once_with(doc, "read", "am@example.com")
