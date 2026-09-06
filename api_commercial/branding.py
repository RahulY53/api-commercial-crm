"""Supported website-context branding for the upstream CRM frontend."""

import frappe


CRM_MESSAGE_OVERRIDES = {
	"Frappe CRM": "Arkenstone CRM",
	"Welcome to Frappe CRM": "Welcome to Arkenstone CRM",
	"How many people will use Frappe CRM?": "How many people will use Arkenstone CRM?",
	"Frappe CRM mobile": "Arkenstone CRM mobile",
	"You do not have permission to access Frappe CRM": "You do not have permission to access Arkenstone CRM",
	"You do not have enough permissions to access Frappe CRM. Please contact your administrator if you believe this is an error.": (
		"You do not have enough permissions to access Arkenstone CRM. "
		"Please contact your administrator if you believe this is an error."
	),
}


def update_website_context(context):
	"""Inject CRM copy into the route's existing boot payload."""
	path = context.get("path") or getattr(frappe.local, "path", "") or ""
	if not path.lstrip("/").startswith("crm"):
		return

	boot = context.get("boot")
	if not boot:
		return

	brand_crm_boot(boot)


def brand_crm_boot(boot):
	"""Apply product copy to either a rendered or developer-mode CRM boot."""
	boot.setdefault("translated_messages", {}).update(CRM_MESSAGE_OVERRIDES)
	return boot
