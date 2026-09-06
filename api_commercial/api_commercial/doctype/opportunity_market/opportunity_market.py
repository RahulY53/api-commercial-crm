import frappe
from frappe.model.document import Document
from frappe.utils import flt


class OpportunityMarket(Document):
	def validate(self):
		self.validate_target_market()
		self.validate_commercial_values()
		self.validate_unique_market()

	def validate_target_market(self):
		if not frappe.db.get_value("Target Market", self.target_market, "active"):
			frappe.throw("Target Market must be active.")

	def validate_commercial_values(self):
		if self.estimated_annual_volume is not None and flt(self.estimated_annual_volume) < 0:
			frappe.throw("Estimated Annual Volume cannot be negative.")
		if self.probability_override is not None and not 0 <= flt(self.probability_override) <= 100:
			frappe.throw("Probability Override must be between 0 and 100.")

	def validate_unique_market(self):
		filters = {"opportunity": self.opportunity, "target_market": self.target_market}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Opportunity Market", filters):
			frappe.throw("Target Market already exists on this Product Opportunity.")
