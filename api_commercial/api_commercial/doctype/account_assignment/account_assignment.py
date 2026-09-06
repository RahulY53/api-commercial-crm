import frappe
from frappe.model.document import Document

from api_commercial.services.assignments import find_overlapping_record, validate_date_range


class AccountAssignment(Document):
	def validate(self):
		validate_date_range(self.start_date, self.end_date)
		self.validate_assignment_type()
		self.validate_duplicate_assignment()
		self.validate_primary_assignment()

	def validate_assignment_type(self):
		if self.active and not frappe.db.get_value(
			"Account Assignment Type", self.assignment_type, "active"
		):
			frappe.throw("Assignment Type must be active.")

	def validate_duplicate_assignment(self):
		if not self.active:
			return
		duplicate = find_overlapping_record(
			self.doctype,
			{"customer": self.customer, "user": self.user, "assignment_type": self.assignment_type},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Assignment overlaps with {duplicate}.")

	def validate_primary_assignment(self):
		if not (self.active and self.primary):
			return
		duplicate = find_overlapping_record(
			self.doctype,
			{"customer": self.customer, "assignment_type": self.assignment_type, "primary": 1},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Primary assignment overlaps with {duplicate}.")
