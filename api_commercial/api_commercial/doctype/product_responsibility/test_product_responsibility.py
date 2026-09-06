import frappe
from frappe.tests.utils import FrappeTestCase


class TestProductResponsibility(FrappeTestCase):
	def setUp(self):
		self.product = frappe.get_doc(
			{
				"doctype": "CRM Product",
				"product_code": f"TEST-{frappe.generate_hash(length=10)}",
				"product_name": "Test API Product",
			}
		).insert()

	def test_overlapping_responsibility_is_rejected(self):
		self.make_responsibility("2026-01-01", "2026-06-30")

		with self.assertRaises(frappe.ValidationError):
			self.make_responsibility("2026-06-01", "2026-12-31")

	def test_adjacent_responsibility_is_allowed(self):
		self.make_responsibility("2026-01-01", "2026-06-30")
		responsibility = self.make_responsibility("2026-07-01", "2026-12-31")

		self.assertTrue(responsibility.name)

	def test_overlapping_primary_owner_is_rejected(self):
		self.make_responsibility("2026-01-01", None, primary=1)
		other_user = self.make_user()

		with self.assertRaises(frappe.ValidationError):
			self.make_responsibility("2026-02-01", None, user=other_user.name, primary=1)

	def test_active_responsibility_rejects_disabled_product(self):
		self.product.disabled = 1
		self.product.save()

		with self.assertRaises(frappe.ValidationError):
			self.make_responsibility()

	def make_user(self):
		return frappe.get_doc(
			{
				"doctype": "User",
				"email": f"product-manager-{frappe.generate_hash(length=10)}@example.test",
				"first_name": "Product Manager",
				"send_welcome_email": 0,
			}
		).insert()

	def make_responsibility(
		self, start_date=None, end_date=None, user="Administrator", primary=0
	):
		return frappe.get_doc(
			{
				"doctype": "Product Responsibility",
				"product": self.product.name,
				"user": user,
				"primary_responsibility": primary,
				"start_date": start_date,
				"end_date": end_date,
				"active": 1,
			}
		).insert()
