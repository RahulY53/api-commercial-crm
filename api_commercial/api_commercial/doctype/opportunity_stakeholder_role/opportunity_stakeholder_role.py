from frappe.model.document import Document


class OpportunityStakeholderRole(Document):
	def validate(self):
		self.role_name = (self.role_name or "").strip()
