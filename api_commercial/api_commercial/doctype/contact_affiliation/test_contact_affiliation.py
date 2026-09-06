import frappe
from frappe.tests.utils import FrappeTestCase


class TestContactAffiliation(FrappeTestCase):
	def setUp(self):
		self.customer = self.make_customer()
		self.other_customer = self.make_customer()
		self.site = frappe.get_doc(
			{
				"doctype": "Manufacturing Site",
				"site_name": f"Affiliation Site {frappe.generate_hash(length=8)}",
				"customer": self.customer.name,
				"site_type": "R&D",
			}
		).insert()
		self.contact = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": f"Contact {frappe.generate_hash(length=8)}",
			}
		).insert()

	def test_contact_can_have_customer_and_site_affiliations(self):
		customer_affiliation = self.make_affiliation("Customer", customer=self.customer.name)
		site_affiliation = self.make_affiliation("Manufacturing Site", site=self.site.name)

		self.assertEqual(customer_affiliation.customer, self.customer.name)
		self.assertEqual(site_affiliation.customer, self.customer.name)

	def test_site_affiliation_rejects_mismatched_customer(self):
		with self.assertRaises(frappe.ValidationError):
			self.make_affiliation(
				"Manufacturing Site", customer=self.other_customer.name, site=self.site.name
			)

	def test_duplicate_affiliation_is_rejected(self):
		self.make_affiliation("Customer", customer=self.customer.name, start="2026-01-01")

		with self.assertRaises(frappe.ValidationError):
			self.make_affiliation("Customer", customer=self.customer.name, start="2026-06-01")

	def test_overlapping_primary_affiliation_is_rejected(self):
		self.make_affiliation(
			"Customer", customer=self.customer.name, primary=1, start="2026-01-01"
		)

		with self.assertRaises(frappe.ValidationError):
			self.make_affiliation(
				"Customer", customer=self.other_customer.name, primary=1, start="2026-02-01"
			)

	def make_customer(self):
		return frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Affiliation Customer {frappe.generate_hash(length=10)}",
				"custom_account_type": "Global Parent",
			}
		).insert()

	def make_affiliation(
		self, affiliation_type, customer=None, site=None, primary=0, start=None
	):
		return frappe.get_doc(
			{
				"doctype": "Contact Affiliation",
				"contact": self.contact.name,
				"affiliation_type": affiliation_type,
				"customer": customer,
				"manufacturing_site": site,
				"primary_affiliation": primary,
				"start_date": start,
				"active": 1,
			}
		).insert()
