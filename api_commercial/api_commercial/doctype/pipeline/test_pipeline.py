import frappe
from frappe.tests.utils import FrappeTestCase


class TestPipeline(FrappeTestCase):
	def test_only_one_default_pipeline_is_allowed(self):
		if not frappe.db.exists("Pipeline", {"is_default": 1}):
			self.make_pipeline(is_default=1)
		with self.assertRaises(frappe.ValidationError):
			self.make_pipeline(is_default=1)

	def test_stage_name_is_unique_within_pipeline(self):
		pipeline = self.make_pipeline()
		self.make_stage(pipeline.name, "Discovery")
		with self.assertRaises(frappe.ValidationError):
			self.make_stage(pipeline.name, "Discovery", sequence=2)

	def test_stage_sequence_is_unique_within_pipeline(self):
		pipeline = self.make_pipeline()
		self.make_stage(pipeline.name, "Discovery", sequence=1)
		with self.assertRaises(frappe.ValidationError):
			self.make_stage(pipeline.name, "Evaluation", sequence=1)

	def make_pipeline(self, is_default=0):
		return frappe.get_doc(
			{
				"doctype": "Pipeline",
				"pipeline_name": f"Test Pipeline {frappe.generate_hash(length=10)}",
				"active": 1,
				"is_default": is_default,
			}
		).insert()

	def make_stage(self, pipeline, stage_name, sequence=1):
		return frappe.get_doc(
			{
				"doctype": "Pipeline Stage",
				"pipeline": pipeline,
				"stage_name": stage_name,
				"sequence": sequence,
				"default_probability": 20,
				"active": 1,
			}
		).insert()
