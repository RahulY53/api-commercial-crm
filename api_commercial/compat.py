"""Narrow compatibility adapters for the pinned Frappe/Frappe CRM stack."""

import frappe
from frappe.utils.telemetry.pulse.client import is_enabled

from api_commercial.branding import brand_crm_boot


@frappe.whitelist()
def pulse_boot_config() -> dict[str, bool]:
	"""Return the bootstrap shape expected by Frappe CRM v1.83.

	Frappe v15.120 provides the underlying telemetry decision through
	``is_enabled`` but does not yet expose CRM's ``boot_config`` endpoint.
	"""

	return {"enabled": bool(is_enabled())}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def crm_dev_boot_config():
	"""Preserve Arkenstone copy when CRM refreshes boot in developer mode."""
	from crm.www.crm import get_context_for_dev

	return brand_crm_boot(get_context_for_dev())
