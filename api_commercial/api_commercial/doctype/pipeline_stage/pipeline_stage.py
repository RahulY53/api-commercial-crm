import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt


class PipelineStage(Document):
	def validate(self):
		self.stage_name = (self.stage_name or "").strip()
		if cint(self.sequence) < 1:
			frappe.throw("Sequence must be greater than zero.")
		if not 0 <= flt(self.default_probability) <= 100:
			frappe.throw("Default Probability must be between 0 and 100.")
		if self.recommended_max_days is not None and cint(self.recommended_max_days) < 0:
			frappe.throw("Recommended Maximum Days cannot be negative.")
		if self.is_won_stage and self.is_lost_stage:
			frappe.throw("A Pipeline Stage cannot be both won and lost.")
		if self.active and not frappe.db.get_value("Pipeline", self.pipeline, "active"):
			frappe.throw("Pipeline must be active.")

		filters = {"pipeline": self.pipeline, "stage_name": self.stage_name}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Pipeline Stage", filters):
			frappe.throw("Stage Name must be unique within the Pipeline.")

		sequence_filters = {"pipeline": self.pipeline, "sequence": self.sequence}
		if self.name:
			sequence_filters["name"] = ["!=", self.name]
		if frappe.db.exists("Pipeline Stage", sequence_filters):
			frappe.throw("Sequence must be unique within the Pipeline.")
