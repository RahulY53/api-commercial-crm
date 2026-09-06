import frappe
from frappe.model.document import Document

from api_commercial.services.assignments import find_overlapping_record, validate_date_range


class ContactAffiliation(Document):
	def validate(self):
		validate_date_range(self.start_date, self.end_date)
		self.validate_affiliated_entity()
		self.validate_duplicate_affiliation()
		self.validate_primary_affiliation()

	def validate_affiliated_entity(self):
		if self.affiliation_type == "Customer":
			if not self.customer:
				frappe.throw("Customer is required for a Customer affiliation.")
			if self.manufacturing_site:
				frappe.throw("Manufacturing Site must be empty for a Customer affiliation.")
			return

		if self.affiliation_type != "Manufacturing Site":
			frappe.throw("Select a valid Affiliation Type.")
		if not self.manufacturing_site:
			frappe.throw("Manufacturing Site is required for a site affiliation.")

		site_customer = frappe.db.get_value("Manufacturing Site", self.manufacturing_site, "customer")
		if not site_customer:
			frappe.throw("Manufacturing Site does not have an owning Customer.")
		if self.customer and self.customer != site_customer:
			frappe.throw("Customer must match the Manufacturing Site's owning Customer.")
		self.customer = site_customer

	def validate_duplicate_affiliation(self):
		if not self.active:
			return
		filters = {
			"contact": self.contact,
			"affiliation_type": self.affiliation_type,
			"customer": self.customer,
		}
		if self.manufacturing_site:
			filters["manufacturing_site"] = self.manufacturing_site
		duplicate = find_overlapping_record(
			self.doctype,
			filters,
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Affiliation overlaps with {duplicate}.")

	def validate_primary_affiliation(self):
		if not (self.active and self.primary_affiliation):
			return
		duplicate = find_overlapping_record(
			self.doctype,
			{"contact": self.contact, "primary_affiliation": 1},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Primary affiliation overlaps with {duplicate}.")
