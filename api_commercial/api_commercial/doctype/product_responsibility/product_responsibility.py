import frappe
from frappe.model.document import Document

from api_commercial.services.assignments import find_overlapping_record, validate_date_range


class ProductResponsibility(Document):
	def validate(self):
		validate_date_range(self.start_date, self.end_date)
		self.validate_active_links()
		self.validate_duplicate_responsibility()
		self.validate_primary_responsibility()

	def validate_active_links(self):
		if not self.active:
			return

		if frappe.db.get_value("CRM Product", self.product, "disabled"):
			frappe.throw("An active responsibility requires an enabled Product.")

		if not frappe.db.get_value("User", self.user, "enabled"):
			frappe.throw("An active responsibility requires an enabled User.")

	def validate_duplicate_responsibility(self):
		if not self.active:
			return

		duplicate = find_overlapping_record(
			self.doctype,
			{"product": self.product, "user": self.user},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Product responsibility overlaps with {duplicate}.")

	def validate_primary_responsibility(self):
		if not (self.active and self.primary_responsibility):
			return

		duplicate = find_overlapping_record(
			self.doctype,
			{"product": self.product, "primary_responsibility": 1},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Primary Product Owner responsibility overlaps with {duplicate}.")
