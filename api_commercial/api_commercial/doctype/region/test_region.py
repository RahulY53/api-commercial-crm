import frappe
from frappe.tests.utils import FrappeTestCase


class TestRegion(FrappeTestCase):
	def test_region_code_is_normalized(self):
		region = frappe.get_doc(
			{
				"doctype": "Region",
				"region_name": f"Test Region {frappe.generate_hash(length=8)}",
				"region_code": f" t{frappe.generate_hash(length=6)} ",
			}
		).insert()

		self.assertEqual(region.region_code, region.region_code.strip().upper())
