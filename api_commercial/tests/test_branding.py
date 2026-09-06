import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial.setup import BRAND_FAVICON, BRAND_LOGO, BRAND_NAME, seed_branding


class TestBranding(FrappeTestCase):
	def test_arkenstone_branding_is_applied_to_crm_and_frappe_surfaces(self):
		seed_branding()
		self.assertEqual(frappe.db.get_single_value("FCRM Settings", "brand_name"), BRAND_NAME)
		self.assertEqual(frappe.db.get_single_value("FCRM Settings", "brand_logo"), BRAND_LOGO)
		self.assertEqual(frappe.db.get_single_value("FCRM Settings", "favicon"), BRAND_FAVICON)
		self.assertEqual(frappe.db.get_single_value("System Settings", "app_name"), BRAND_NAME)
		self.assertEqual(frappe.db.get_single_value("Website Settings", "app_logo"), BRAND_LOGO)

	def test_custom_administrator_branding_is_not_overwritten(self):
		frappe.db.set_single_value("FCRM Settings", "brand_name", "Example Customer Brand")
		seed_branding()
		self.assertEqual(
			frappe.db.get_single_value("FCRM Settings", "brand_name"), "Example Customer Brand"
		)
