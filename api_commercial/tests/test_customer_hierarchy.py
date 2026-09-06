import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial.services.customers import get_descendant_customers


class TestCustomerHierarchy(FrappeTestCase):
	def setUp(self):
		suffix = frappe.generate_hash(length=8)
		self.region = frappe.get_doc(
			{
				"doctype": "Region",
				"region_name": f"Customer Region {suffix}",
				"region_code": f"C{suffix[:7]}",
			}
		).insert()

	def test_operating_customer_requires_region(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_customer("Operating Customer")

	def test_customer_hierarchy_rejects_cycle(self):
		parent = self.make_customer("Global Parent")
		child = self.make_customer("Operating Customer", parent=parent.name, region=self.region.name)

		parent.custom_parent_customer = child.name
		with self.assertRaises(frappe.ValidationError):
			parent.save()

	def test_descendant_resolution_includes_all_levels(self):
		parent = self.make_customer("Global Parent")
		child = self.make_customer("Operating Customer", parent=parent.name, region=self.region.name)
		grandchild = self.make_customer(
			"Operating Customer", parent=child.name, region=self.region.name
		)

		self.assertEqual(
			set(get_descendant_customers(parent.name, include_self=True)),
			{parent.name, child.name, grandchild.name},
		)

	def make_customer(self, account_type, parent=None, region=None):
		return frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Customer {frappe.generate_hash(length=10)}",
				"custom_account_type": account_type,
				"custom_parent_customer": parent,
				"custom_region": region,
			}
		).insert()
