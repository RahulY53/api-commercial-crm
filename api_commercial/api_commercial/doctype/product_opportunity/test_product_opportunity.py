from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class OpportunityTestData:
	def setUp(self):
		suffix = frappe.generate_hash(length=10)
		self.region = frappe.get_doc(
			{
				"doctype": "Region",
				"region_name": f"Opportunity Region {suffix}",
				"region_code": f"OR{suffix[:6]}",
				"active": 1,
			}
		).insert()
		self.customer = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Opportunity Customer {suffix}",
				"custom_account_type": "Operating Customer",
				"custom_region": self.region.name,
			}
		).insert()
		self.product = frappe.get_doc(
			{
				"doctype": "CRM Product",
				"product_code": f"OPP-{suffix}",
				"product_name": f"Test API {suffix}",
			}
		).insert()
		self.pipeline = frappe.get_doc(
			{
				"doctype": "Pipeline",
				"pipeline_name": f"Opportunity Pipeline {suffix}",
				"active": 1,
			}
		).insert()
		self.stage = self.make_stage("Discovery", 1, 25)
		self.next_stage = self.make_stage("Evaluation", 2, 55)

	def make_stage(self, stage_name, sequence, probability):
		return frappe.get_doc(
			{
				"doctype": "Pipeline Stage",
				"pipeline": self.pipeline.name,
				"stage_name": stage_name,
				"sequence": sequence,
				"default_probability": probability,
				"active": 1,
			}
		).insert()

	def make_opportunity(self, **overrides):
		values = {
			"doctype": "Product Opportunity",
			"customer": self.customer.name,
			"product": self.product.name,
			"opportunity_owner": "Administrator",
			"pipeline": self.pipeline.name,
			"current_stage": self.stage.name,
			"status": "Active",
		}
		values.update(overrides)
		return frappe.get_doc(values).insert()


class TestProductOpportunity(OpportunityTestData, FrappeTestCase):
	def test_region_name_and_stage_values_are_server_derived(self):
		opportunity = self.make_opportunity(region=None, probability=99)

		self.assertEqual(opportunity.region, self.region.name)
		self.assertEqual(
			opportunity.opportunity_name,
			f"{self.customer.organization_name} - {self.product.product_name}",
		)
		self.assertEqual(opportunity.stage_entered_date, today())
		self.assertEqual(opportunity.probability, 25)

	def test_stage_must_belong_to_pipeline(self):
		other_pipeline = frappe.get_doc(
			{
				"doctype": "Pipeline",
				"pipeline_name": f"Other Pipeline {frappe.generate_hash(length=10)}",
				"active": 1,
			}
		).insert()
		other_stage = frappe.get_doc(
			{
				"doctype": "Pipeline Stage",
				"pipeline": other_pipeline.name,
				"stage_name": "Discovery",
				"sequence": 1,
				"default_probability": 10,
				"active": 1,
			}
		).insert()

		with self.assertRaises(frappe.ValidationError):
			self.make_opportunity(current_stage=other_stage.name)

	def test_duplicate_requires_documented_admin_override(self):
		self.make_opportunity()
		with self.assertRaises(frappe.ValidationError):
			self.make_opportunity()

		override = self.make_opportunity(
			duplicate_override=1,
			duplicate_override_reason="Separate validated business stream",
		)
		self.assertTrue(override.name)

	def test_duplicate_override_requires_authorized_role(self):
		self.make_opportunity()
		with (
			patch("frappe.get_roles", return_value=["Account Manager"]),
			self.assertRaises(frappe.ValidationError),
		):
			self.make_opportunity(
				duplicate_override=1,
				duplicate_override_reason="Separate validated business stream",
			)

	def test_stage_entered_date_only_changes_with_stage(self):
		opportunity = self.make_opportunity()
		frappe.db.set_value("Product Opportunity", opportunity.name, "stage_entered_date", "2025-01-01")
		opportunity.reload()
		opportunity.stage_entered_date = "2025-02-01"
		opportunity.save()
		self.assertEqual(str(opportunity.stage_entered_date), "2025-01-01")

		opportunity.current_stage = self.next_stage.name
		opportunity.save()
		self.assertEqual(opportunity.stage_entered_date, today())
		self.assertEqual(opportunity.probability, 55)
