import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial.api_commercial.doctype.product_opportunity.test_product_opportunity import OpportunityTestData


class TestOpportunityMarket(OpportunityTestData, FrappeTestCase):
	def test_target_market_is_unique_per_opportunity(self):
		opportunity = self.make_opportunity()
		market = frappe.get_doc(
			{
				"doctype": "Target Market",
				"market_name": f"Market {frappe.generate_hash(length=10)}",
				"active": 1,
			}
		).insert()
		self.make_market(opportunity.name, market.name)

		with self.assertRaises(frappe.ValidationError):
			self.make_market(opportunity.name, market.name)

	def test_probability_override_is_bounded(self):
		opportunity = self.make_opportunity()
		market = frappe.get_doc(
			{
				"doctype": "Target Market",
				"market_name": f"Market {frappe.generate_hash(length=10)}",
				"active": 1,
			}
		).insert()
		with self.assertRaises(frappe.ValidationError):
			self.make_market(opportunity.name, market.name, probability_override=101)

	def make_market(self, opportunity, market, **overrides):
		values = {
			"doctype": "Opportunity Market",
			"opportunity": opportunity,
			"target_market": market,
		}
		values.update(overrides)
		return frappe.get_doc(values).insert()
