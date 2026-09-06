import frappe
from frappe.tests.utils import FrappeTestCase


class TestProductCatalogue(FrappeTestCase):
	def test_api_product_metadata_uses_configurable_masters(self):
		suffix = frappe.generate_hash(length=10)
		category = frappe.get_doc(
			{
				"doctype": "API Product Category",
				"category_name": f"Category {suffix}",
			}
		).insert()
		therapeutic_area = frappe.get_doc(
			{
				"doctype": "Therapeutic Area",
				"therapeutic_area_name": f"Area {suffix}",
			}
		).insert()
		commercial_status = frappe.get_doc(
			{
				"doctype": "Product Commercial Status",
				"status_name": f"Status {suffix}",
			}
		).insert()

		product = frappe.get_doc(
			{
				"doctype": "CRM Product",
				"product_code": f"API-{suffix}",
				"product_name": "Catalogue Test API",
				"custom_molecule": "Test Molecule",
				"custom_product_category": category.name,
				"custom_therapeutic_area": therapeutic_area.name,
				"custom_commercial_status": commercial_status.name,
				"custom_standard_uom": "kg",
				"custom_standard_pack_size": 25,
			}
		).insert()

		saved = frappe.get_doc("CRM Product", product.name)
		self.assertEqual(saved.custom_product_category, category.name)
		self.assertEqual(saved.custom_therapeutic_area, therapeutic_area.name)
		self.assertEqual(saved.custom_commercial_status, commercial_status.name)
		self.assertEqual(saved.custom_standard_uom, "kg")
		self.assertEqual(saved.custom_standard_pack_size, 25)
