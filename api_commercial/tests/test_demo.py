from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial import demo


class TestDemoData(FrappeTestCase):
	def test_seed_is_idempotent_and_sends_no_welcome_email(self):
		with patch(
			"frappe.core.doctype.user.user.User.send_welcome_mail_to_user"
		) as send_welcome_mail:
			first = demo.seed()
			second = demo.seed()

		send_welcome_mail.assert_not_called()
		self.assertEqual(first["users"], second["users"])
		self.assertEqual(first["opportunities"], second["opportunities"])
		self.assertEqual(len(second["users"]), 6)
		self.assertEqual(len(second["customers"]), 7)
		self.assertEqual(len(second["products"]), 3)
		self.assertEqual(len(second["opportunities"]), 5)

		india_am = frappe.get_doc("User", demo.PERSONAS["india_am"][0])
		self.assertFalse(india_am.send_welcome_email)
		self.assertIn("Sales User", {row.role for row in india_am.roles})
		self.assertIn("Account Manager", {row.role for row in india_am.roles})
