import frappe
from frappe.tests.utils import FrappeTestCase


class TestAccountAssignment(FrappeTestCase):
	def setUp(self):
		self.customer = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Assignment Customer {frappe.generate_hash(length=8)}",
			}
		).insert()

	def test_overlapping_assignment_is_rejected(self):
		self.make_assignment("2026-01-01", "2026-06-30")

		with self.assertRaises(frappe.ValidationError):
			self.make_assignment("2026-06-30", "2026-12-31")

	def make_assignment(self, start_date, end_date):
		return frappe.get_doc(
			{
				"doctype": "Account Assignment",
				"customer": self.customer.name,
				"user": "Administrator",
				"assignment_type": "Primary Account Manager",
				"primary": 1,
				"start_date": start_date,
				"end_date": end_date,
				"active": 1,
			}
		).insert()
