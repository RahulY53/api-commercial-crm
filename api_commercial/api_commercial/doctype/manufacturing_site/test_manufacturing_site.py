import frappe
from frappe.tests.utils import FrappeTestCase


class TestManufacturingSite(FrappeTestCase):
	def setUp(self):
		self.customer = self.make_customer()

	def test_site_name_is_unique_within_customer(self):
		self.make_site("Plant One")

		with self.assertRaises(frappe.ValidationError):
			self.make_site(" Plant One ")

	def test_same_site_name_is_allowed_for_different_customers(self):
		self.make_site("R&D Centre")
		other_customer = self.make_customer()
		other_site = self.make_site("R&D Centre", customer=other_customer.name)

		self.assertTrue(other_site.name)

	def make_customer(self):
		return frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Site Customer {frappe.generate_hash(length=10)}",
				"custom_account_type": "Global Parent",
			}
		).insert()

	def make_site(self, site_name, customer=None):
		return frappe.get_doc(
			{
				"doctype": "Manufacturing Site",
				"site_name": site_name,
				"customer": customer or self.customer.name,
				"site_type": "API Manufacturing",
			}
		).insert()
