from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.website.page_renderers.template_page import TemplatePage

from api_commercial.branding import update_website_context
from api_commercial.compat import crm_dev_boot_config, pulse_boot_config


class TestCompatibility(FrappeTestCase):
	def test_pulse_boot_config_matches_crm_contract(self):
		with patch("api_commercial.compat.is_enabled", return_value=False):
			self.assertEqual(pulse_boot_config(), {"enabled": False})

		with patch("api_commercial.compat.is_enabled", return_value=True):
			self.assertEqual(pulse_boot_config(), {"enabled": True})

	def test_crm_branding_is_injected_into_boot_messages(self):
		context = {"boot": {"translated_messages": {}}}
		original_path = getattr(frappe.local, "path", None)
		frappe.local.path = "crm"
		try:
			update_website_context(context)
		finally:
			frappe.local.path = original_path

		self.assertEqual(
			context["boot"]["translated_messages"]["Welcome to Frappe CRM"],
			"Welcome to Arkenstone CRM",
		)

	def test_developer_boot_keeps_branding(self):
		with patch(
			"crm.www.crm.get_context_for_dev",
			return_value={"translated_messages": {}},
		):
			boot = crm_dev_boot_config()

		self.assertEqual(
			boot["translated_messages"]["Welcome to Frappe CRM"],
			"Welcome to Arkenstone CRM",
		)

	def test_rendered_crm_boot_keeps_branding(self):
		frappe.set_user("Administrator")
		html = TemplatePage("crm").get_html()
		self.assertIn('"Welcome to Frappe CRM": "Welcome to Arkenstone CRM"', html)
