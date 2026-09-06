import frappe
from frappe.model.document import Document


class ManufacturingSite(Document):
	def validate(self):
		if self.site_name:
			self.site_name = self.site_name.strip()
		self.validate_unique_customer_site()

	def validate_unique_customer_site(self):
		filters = {"customer": self.customer, "site_name": self.site_name}
		if self.name:
			filters["name"] = ("!=", self.name)
		if duplicate := frappe.db.exists(self.doctype, filters):
			frappe.throw(f"Manufacturing Site already exists as {duplicate}.")
