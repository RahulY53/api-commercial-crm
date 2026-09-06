import frappe
from frappe.tests.utils import FrappeTestCase

from api_commercial.api_commercial.doctype.product_opportunity.test_product_opportunity import OpportunityTestData


class TestOpportunityStakeholder(OpportunityTestData, FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.role = frappe.get_doc(
			{
				"doctype": "Opportunity Stakeholder Role",
				"role_name": f"Evaluator {frappe.generate_hash(length=10)}",
				"active": 1,
			}
		).insert()

	def test_affiliation_must_belong_to_opportunity_customer(self):
		opportunity = self.make_opportunity()
		other_customer = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Other Customer {frappe.generate_hash(length=10)}",
			}
		).insert()
		affiliation = self.make_affiliation(other_customer.name)

		with self.assertRaises(frappe.ValidationError):
			self.make_stakeholder(opportunity.name, affiliation.name)

	def test_only_one_primary_contact_is_allowed(self):
		opportunity = self.make_opportunity()
		first = self.make_affiliation(self.customer.name)
		second = self.make_affiliation(self.customer.name)
		self.make_stakeholder(opportunity.name, first.name, primary_contact=1)

		with self.assertRaises(frappe.ValidationError):
			self.make_stakeholder(opportunity.name, second.name, primary_contact=1)

	def test_parent_customer_affiliation_is_allowed_for_subsidiary_opportunity(self):
		parent = frappe.get_doc(
			{
				"doctype": "CRM Organization",
				"organization_name": f"Global Customer {frappe.generate_hash(length=10)}",
			}
		).insert()
		self.customer.custom_parent_customer = parent.name
		self.customer.save()
		opportunity = self.make_opportunity()
		affiliation = self.make_affiliation(parent.name)

		stakeholder = self.make_stakeholder(opportunity.name, affiliation.name)
		self.assertTrue(stakeholder.name)

	def make_affiliation(self, customer):
		contact = frappe.get_doc(
			{
				"doctype": "Contact",
				"first_name": f"Stakeholder {frappe.generate_hash(length=10)}",
			}
		).insert()
		return frappe.get_doc(
			{
				"doctype": "Contact Affiliation",
				"contact": contact.name,
				"affiliation_type": "Customer",
				"customer": customer,
				"active": 1,
			}
		).insert()

	def make_stakeholder(self, opportunity, affiliation, **overrides):
		values = {
			"doctype": "Opportunity Stakeholder",
			"opportunity": opportunity,
			"contact_affiliation": affiliation,
			"opportunity_role": self.role.name,
		}
		values.update(overrides)
		return frappe.get_doc(values).insert()
