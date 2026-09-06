from datetime import date

import frappe
from frappe.utils import getdate


def validate_date_range(start_date: date | str | None, end_date: date | str | None):
	if start_date and end_date and getdate(start_date) > getdate(end_date):
		frappe.throw("End Date cannot be before Start Date.")


def find_overlapping_record(
	doctype: str,
	filters: dict,
	start_date: date | str | None,
	end_date: date | str | None,
	exclude_name: str | None = None,
) -> str | None:
	query_filters = {**filters, "active": 1}
	if exclude_name:
		query_filters["name"] = ("!=", exclude_name)

	for record in frappe.get_all(
		doctype,
		filters=query_filters,
		fields=["name", "start_date", "end_date"],
	):
		if date_ranges_overlap(start_date, end_date, record.start_date, record.end_date):
			return record.name

	return None


def date_ranges_overlap(
	first_start: date | str | None,
	first_end: date | str | None,
	second_start: date | str | None,
	second_end: date | str | None,
) -> bool:
	first_start = getdate(first_start) if first_start else date.min
	first_end = getdate(first_end) if first_end else date.max
	second_start = getdate(second_start) if second_start else date.min
	second_end = getdate(second_end) if second_end else date.max
	return first_start <= second_end and second_start <= first_end
