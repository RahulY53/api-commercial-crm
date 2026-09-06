import frappe
from frappe.model.document import Document


class Pipeline(Document):
	def validate(self):
		self.pipeline_name = (self.pipeline_name or "").strip()
		if self.is_default and not self.active:
			frappe.throw("The default Pipeline must be active.")
		if self.is_default:
			filters = {"is_default": 1}
			if self.name:
				filters["name"] = ["!=", self.name]
			if frappe.db.exists("Pipeline", filters):
				frappe.throw("Only one Pipeline can be the default.")
