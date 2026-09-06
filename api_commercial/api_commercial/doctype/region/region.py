import frappe
from frappe.utils.nestedset import NestedSet


class Region(NestedSet):
	nsm_parent_field = "parent_region"

	def validate(self):
		self.region_code = self.region_code.strip().upper()
		if self.parent_region and not frappe.db.get_value("Region", self.parent_region, "active"):
			frappe.throw("Parent Region must be active.")
