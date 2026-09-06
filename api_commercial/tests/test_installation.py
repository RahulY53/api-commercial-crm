import frappe
from frappe.tests.utils import FrappeTestCase


class TestInstallation(FrappeTestCase):
	def test_required_apps_are_installed(self):
		installed_apps = frappe.get_installed_apps()

		self.assertIn("frappe", installed_apps)
		self.assertIn("crm", installed_apps)
		self.assertIn("api_commercial", installed_apps)

	def test_crm_contact_override_is_preserved(self):
		overrides = frappe.get_hooks("override_doctype_class")

		self.assertIn("crm.overrides.contact.CustomContact", overrides.get("Contact", []))
