import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial import demo
from api_commercial.api.views import get_customer_360, get_my_opportunities


class TestPhaseOnePersonas(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		demo.seed()

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def visible(self, doctype):
		return set(frappe.get_list(doctype, pluck="name", limit_page_length=500))

	def test_account_manager_sees_only_assigned_customer_and_its_opportunity(self):
		frappe.set_user(demo.PERSONAS["india_am"][0])
		self.assertIn("Teva India", self.visible("CRM Organization"))
		self.assertNotIn("Novartis India", self.visible("CRM Organization"))
		self.assertEqual(
			{row.customer for row in frappe.get_list("Product Opportunity", fields=["customer"])},
			{"Teva India"},
		)
		self.assertFalse(frappe.has_permission("CRM Organization", "read", "Teva Europe"))
		self.assertGreaterEqual(len(self.visible("Opportunity Market")), 1)
		self.assertGreaterEqual(len(self.visible("Opportunity Stakeholder")), 1)

	def test_region_head_sees_customers_and_opportunities_in_their_region(self):
		frappe.set_user(demo.PERSONAS["india_head"][0])
		customers = self.visible("CRM Organization")
		self.assertTrue({"Teva India", "Novartis India"}.issubset(customers))
		self.assertNotIn("Teva Europe", customers)
		self.assertFalse(frappe.has_permission("CRM Organization", "read", "Teva Europe"))
		self.assertEqual(
			{row.customer for row in frappe.get_list("Product Opportunity", fields=["customer"])},
			{"Teva India", "Novartis India"},
		)

	def test_global_account_manager_cascades_across_regions_without_changing_owner(self):
		frappe.set_user(demo.PERSONAS["gam"][0])
		customers = self.visible("CRM Organization")
		self.assertTrue({"Teva Global", "Teva India", "Teva Europe"}.issubset(customers))
		self.assertNotIn("Novartis Global", customers)
		owners = {
			row.customer: row.opportunity_owner
			for row in frappe.get_list(
				"Product Opportunity", fields=["customer", "opportunity_owner"]
			)
		}
		self.assertEqual(owners["Teva India"], demo.PERSONAS["india_am"][0])
		self.assertEqual(owners["Teva Europe"], demo.PERSONAS["europe_am"][0])

	def test_product_manager_sees_responsible_products_across_regions(self):
		frappe.set_user(demo.PERSONAS["product_manager"][0])
		products = {
			row.product for row in frappe.get_list("Product Opportunity", fields=["product"])
		}
		self.assertEqual(products, {"DEMO-SEMAGLUTIDE", "DEMO-TIRZEPATIDE"})
		apixaban_opportunity = frappe.db.get_value(
			"Product Opportunity", {"product": "DEMO-APIXABAN"}, "name"
		)
		self.assertFalse(
			frappe.has_permission("Product Opportunity", "read", apixaban_opportunity)
		)

	def test_leadership_has_broad_read_and_no_write(self):
		frappe.set_user(demo.PERSONAS["leadership"][0])
		self.assertEqual(len(self.visible("Product Opportunity")), 5)
		self.assertTrue(frappe.has_permission("Product Opportunity", "read", "PO-00001"))
		self.assertFalse(frappe.has_permission("Product Opportunity", "write", "PO-00001"))

	def test_sensitive_potential_is_omitted_for_account_manager(self):
		frappe.set_user(demo.PERSONAS["india_am"][0])
		rows = get_my_opportunities()
		self.assertTrue(rows)
		self.assertTrue(all(row.estimated_potential is None for row in rows))
		customer = get_customer_360("Teva India")
		self.assertIsNone(customer["summary"]["estimated_potential"])
		self.assertIn("Teva Global", {row.name for row in customer["hierarchy"]})
