import frappe


BUSINESS_ROLES = (
	"Account Manager",
	"Region Head",
	"Global Account Manager",
	"Product Manager",
	"Business Development",
	"Customer Service",
	"Commercial/Pricing",
	"Leadership",
	"CRM Admin",
)

REGION_MEMBERSHIP_ROLES = (
	"Region Head",
	"Account Manager",
	"Global Account Manager",
	"Business Development",
	"Support",
)

ACCOUNT_ASSIGNMENT_TYPES = (
	("Primary Account Manager", False),
	("Secondary Account Manager", False),
	("Global Account Manager", True),
	("Support", False),
	("Temporary Cover", False),
)

OPPORTUNITY_STAKEHOLDER_ROLES = (
	"Decision Maker",
	"Procurement",
	"Technical Evaluator",
	"Quality",
	"Regulatory",
	"Sponsor",
	"Champion",
	"Influencer",
	"Blocker",
)


def after_install():
	seed_phase_one_masters()


def after_migrate():
	seed_phase_one_masters()


def seed_phase_one_masters():
	for role_name in BUSINESS_ROLES:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(
				ignore_permissions=True
			)

	if not frappe.db.table_exists("Region Membership Role"):
		return

	for role_name in REGION_MEMBERSHIP_ROLES:
		insert_master_if_missing(
			"Region Membership Role", role_name, {"role_name": role_name, "active": 1}
		)

	for assignment_type, cascades in ACCOUNT_ASSIGNMENT_TYPES:
		insert_master_if_missing(
			"Account Assignment Type",
			assignment_type,
			{
				"assignment_type": assignment_type,
				"active": 1,
				"cascade_to_descendants": cascades,
			},
		)

	if frappe.db.table_exists("Opportunity Stakeholder Role"):
		for role_name in OPPORTUNITY_STAKEHOLDER_ROLES:
			insert_master_if_missing(
				"Opportunity Stakeholder Role", role_name, {"role_name": role_name, "active": 1}
			)


def insert_master_if_missing(doctype: str, name: str, values: dict):
	if frappe.db.exists(doctype, name):
		return

	frappe.get_doc({"doctype": doctype, "name": name, **values}).insert(ignore_permissions=True)
