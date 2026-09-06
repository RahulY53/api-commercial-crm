import frappe
from frappe.model.document import Document

from api_commercial.services.assignments import find_overlapping_record, validate_date_range


class RegionMembership(Document):
	def validate(self):
		validate_date_range(self.start_date, self.end_date)
		self.validate_active_links()
		self.validate_duplicate_membership()
		self.validate_primary_membership()

	def validate_active_links(self):
		if not self.active:
			return
		if not frappe.db.get_value("Region", self.region, "active"):
			frappe.throw("Region must be active.")
		if not frappe.db.get_value("Region Membership Role", self.membership_role, "active"):
			frappe.throw("Membership Role must be active.")

	def validate_duplicate_membership(self):
		if not self.active:
			return
		duplicate = find_overlapping_record(
			self.doctype,
			{"user": self.user, "region": self.region, "membership_role": self.membership_role},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Membership overlaps with {duplicate}.")

	def validate_primary_membership(self):
		if not (self.active and self.primary_region):
			return
		duplicate = find_overlapping_record(
			self.doctype,
			{"user": self.user, "primary_region": 1},
			self.start_date,
			self.end_date,
			self.name,
		)
		if duplicate:
			frappe.throw(f"Primary Region overlaps with {duplicate}.")
