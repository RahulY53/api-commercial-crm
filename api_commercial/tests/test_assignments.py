from datetime import date

from frappe.tests.utils import FrappeTestCase

from api_commercial.services.assignments import date_ranges_overlap


class TestAssignmentServices(FrappeTestCase):
	def test_open_ended_ranges_overlap(self):
		self.assertTrue(date_ranges_overlap(None, None, date(2026, 1, 1), date(2026, 1, 2)))

	def test_separated_ranges_do_not_overlap(self):
		self.assertFalse(
			date_ranges_overlap(
				date(2026, 1, 1), date(2026, 1, 31), date(2026, 2, 1), date(2026, 2, 28)
			)
		)
