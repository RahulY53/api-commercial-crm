import frappe
from frappe.tests.utils import FrappeTestCase


class TestRegionMembership(FrappeTestCase):
	def setUp(self):
		self.region = frappe.get_doc(
			{
				"doctype": "Region",
				"region_name": f"Membership Region {frappe.generate_hash(length=8)}",
				"region_code": f"M{frappe.generate_hash(length=7)}",
			}
		).insert()

	def test_overlapping_membership_is_rejected(self):
		self.make_membership("2026-01-01", "2026-06-30")

		with self.assertRaises(frappe.ValidationError):
			self.make_membership("2026-06-01", "2026-12-31")

	def test_adjacent_membership_is_allowed(self):
		self.make_membership("2026-01-01", "2026-06-30")
		membership = self.make_membership("2026-07-01", "2026-12-31")

		self.assertTrue(membership.name)

	def make_membership(self, start_date, end_date):
		return frappe.get_doc(
			{
				"doctype": "Region Membership",
				"user": "Administrator",
				"region": self.region.name,
				"membership_role": "Account Manager",
				"start_date": start_date,
				"end_date": end_date,
				"active": 1,
			}
		).insert()
