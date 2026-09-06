import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class OpportunityStakeholder(Document):
	def validate(self):
		self.validate_affiliation()
		self.validate_role()
		self.validate_duplicate()
		self.validate_primary_contact()

	def validate_affiliation(self):
		opportunity_customer = frappe.db.get_value(
			"Product Opportunity", self.opportunity, "customer"
		)
		affiliation = frappe.db.get_value(
			"Contact Affiliation",
			self.contact_affiliation,
			["customer", "active", "start_date", "end_date"],
			as_dict=True,
		)
		if not affiliation:
			frappe.throw("Select a valid Contact Affiliation.")
		today = getdate(nowdate())
		if (
			not affiliation.active
			or (affiliation.start_date and getdate(affiliation.start_date) > today)
			or (affiliation.end_date and getdate(affiliation.end_date) < today)
		):
			frappe.throw("Contact Affiliation must be active and currently effective.")
		if not self.is_customer_or_ancestor(affiliation.customer, opportunity_customer):
			frappe.throw(
				"Contact Affiliation must belong to the Product Opportunity's Customer "
				"or one of its parent Customers."
			)

	@staticmethod
	def is_customer_or_ancestor(candidate, customer):
		visited = set()
		while customer and customer not in visited:
			if customer == candidate:
				return True
			visited.add(customer)
			customer = frappe.db.get_value("CRM Organization", customer, "custom_parent_customer")
		return False

	def validate_role(self):
		if not frappe.db.get_value("Opportunity Stakeholder Role", self.opportunity_role, "active"):
			frappe.throw("Opportunity Role must be active.")

	def validate_duplicate(self):
		filters = {
			"opportunity": self.opportunity,
			"contact_affiliation": self.contact_affiliation,
			"opportunity_role": self.opportunity_role,
		}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Opportunity Stakeholder", filters):
			frappe.throw("This Contact Affiliation already has that role on the Product Opportunity.")

	def validate_primary_contact(self):
		if not self.primary_contact:
			return
		filters = {"opportunity": self.opportunity, "primary_contact": 1}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Opportunity Stakeholder", filters):
			frappe.throw("The Product Opportunity already has a primary Contact.")
