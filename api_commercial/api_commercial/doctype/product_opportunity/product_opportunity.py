import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, today


OPEN_STATUSES = ("Active", "On Hold")
DUPLICATE_OVERRIDE_ROLES = {"CRM Admin", "System Manager"}


class ProductOpportunity(Document):
	def autoname(self):
		self.name = make_autoname("PO-.#####")
		self.opportunity_id = self.name

	def validate(self):
		self.set_customer_details()
		self.validate_manufacturing_site()
		self.validate_pipeline_stage()
		self.set_stage_values()
		self.set_opportunity_name()
		self.validate_probability()
		self.validate_duplicate_override()
		self.validate_duplicate_opportunity()

	def after_insert(self):
		if self.opportunity_id != self.name:
			frappe.db.set_value(self.doctype, self.name, "opportunity_id", self.name, update_modified=False)

	def set_customer_details(self):
		customer = frappe.db.get_value(
			"CRM Organization", self.customer, ["organization_name", "custom_region"], as_dict=True
		)
		if not customer:
			frappe.throw("Select a valid Customer.")
		self.region = customer.custom_region
		self._customer_name = customer.organization_name

	def validate_manufacturing_site(self):
		if not self.manufacturing_site:
			return
		site_customer = frappe.db.get_value("Manufacturing Site", self.manufacturing_site, "customer")
		if site_customer != self.customer:
			frappe.throw("Manufacturing Site must belong to the selected Customer.")

	def validate_pipeline_stage(self):
		stage = frappe.db.get_value(
			"Pipeline Stage",
			self.current_stage,
			["pipeline", "active", "default_probability"],
			as_dict=True,
		)
		if not stage or not stage.active:
			frappe.throw("Current Stage must be active.")
		if stage.pipeline != self.pipeline:
			frappe.throw("Current Stage must belong to the selected Pipeline.")
		if not frappe.db.get_value("Pipeline", self.pipeline, "active"):
			frappe.throw("Pipeline must be active.")
		self._stage_probability = stage.default_probability

	def set_stage_values(self):
		previous = self.get_doc_before_save()
		stage_changed = not previous or previous.current_stage != self.current_stage
		if stage_changed:
			self.stage_entered_date = today()
			self.probability = self._stage_probability
		elif previous and self.stage_entered_date != previous.stage_entered_date:
			self.stage_entered_date = previous.stage_entered_date

	def set_opportunity_name(self):
		product_name = frappe.db.get_value("CRM Product", self.product, "product_name") or self.product
		self.opportunity_name = f"{self._customer_name} - {product_name}"

	def validate_probability(self):
		if not 0 <= flt(self.probability) <= 100:
			frappe.throw("Probability must be between 0 and 100.")

	def validate_duplicate_override(self):
		if not self.duplicate_override:
			return
		if not (self.duplicate_override_reason or "").strip():
			frappe.throw("Duplicate Override Reason is required.")

		previous = self.get_doc_before_save()
		override_just_enabled = not previous or not previous.duplicate_override
		if override_just_enabled and not DUPLICATE_OVERRIDE_ROLES.intersection(frappe.get_roles()):
			frappe.throw("Only CRM Admin or System Manager can authorize a duplicate opportunity.")

	def validate_duplicate_opportunity(self):
		if self.status not in OPEN_STATUSES:
			return
		filters = {
			"customer": self.customer,
			"product": self.product,
			"status": ["in", OPEN_STATUSES],
		}
		if self.name:
			filters["name"] = ["!=", self.name]
		duplicate = frappe.db.exists("Product Opportunity", filters)
		if duplicate and not self.duplicate_override:
			frappe.throw(
				f"Active Product Opportunity {duplicate} already exists for this Customer and Product. "
				"Ask a CRM Admin to authorize a documented duplicate when the exception is legitimate."
			)
