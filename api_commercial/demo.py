"""Deterministic, opt-in Phase 1 demonstration data.

Run with::

	bench --site <site> execute api_commercial.demo.seed

The fictional users receive no known password and no welcome email. An
administrator must explicitly set or reset a password before interactive use.
"""

from __future__ import annotations

import frappe
from frappe.utils import cstr

from api_commercial.setup import seed_phase_one_masters

DEMO_DOMAIN = "api-commercial.example"
START_DATE = "2025-01-01"

PERSONAS = {
	"india_am": ("india.am.demo@api-commercial.example", "Ira", "Account Manager", "Account Manager"),
	"india_head": (
		"india.region-head.demo@api-commercial.example",
		"Ravi",
		"Region Head",
		"Region Head",
	),
	"europe_am": (
		"europe.am.demo@api-commercial.example",
		"Elena",
		"Account Manager",
		"Account Manager",
	),
	"gam": (
		"global.account.demo@api-commercial.example",
		"Gabriel",
		"Global Account Manager",
		"Global Account Manager",
	),
	"product_manager": (
		"product.manager.demo@api-commercial.example",
		"Priyanka",
		"Product Manager",
		"Product Manager",
	),
	"leadership": (
		"leadership.demo@api-commercial.example",
		"Leena",
		"Leadership",
		"Leadership",
	),
}


def seed():
	"""Create or reconcile the complete fictional Phase 1 demonstration dataset."""
	seed_phase_one_masters()
	users = _seed_users()
	regions = _seed_regions()
	_seed_region_memberships(users, regions)
	customers = _seed_customers(regions)
	sites = _seed_sites(customers)
	affiliations = _seed_contacts_and_affiliations(customers)
	_seed_account_assignments(users, customers)
	products = _seed_products()
	_seed_product_responsibilities(users, products)
	pipeline, stages = _seed_pipeline()
	markets = _seed_target_markets()
	opportunities = _seed_opportunities(users, customers, sites, products, pipeline, stages)
	_seed_opportunity_markets(opportunities, markets)
	_seed_stakeholders(opportunities, affiliations)

	return {
		"users": sorted(users.values()),
		"regions": sorted(regions.values()),
		"customers": sorted(customers.values()),
		"products": sorted(products.values()),
		"opportunities": sorted(opportunities.values()),
		"message": "Phase 1 demo data seeded. Demo users have no known password and received no email.",
	}


def _seed_users():
	users = {}
	for key, (email, first_name, last_name, business_role) in PERSONAS.items():
		user = _ensure(
			"User",
			{"name": email},
			{
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
				"enabled": 1,
				"user_type": "System User",
				"send_welcome_email": 0,
			},
		)
		for role in ("Sales User", business_role):
			if role not in {row.role for row in user.roles}:
				user.add_roles(role)
		users[key] = user.name
	return users


def _seed_regions():
	regions = {}
	for name, code, sort_order in (
		("India", "IND", 10),
		("Europe", "EUR", 20),
		("North America", "NAM", 30),
	):
		regions[name] = _ensure(
			"Region",
			{"name": name},
			{"region_name": name, "region_code": code, "sort_order": sort_order, "active": 1},
		).name
	return regions


def _seed_region_memberships(users, regions):
	for user, region, role in (
		(users["india_am"], regions["India"], "Account Manager"),
		(users["india_head"], regions["India"], "Region Head"),
		(users["europe_am"], regions["Europe"], "Account Manager"),
	):
		_ensure(
			"Region Membership",
			{"user": user, "region": region, "membership_role": role},
			{"primary_region": 1, "start_date": START_DATE, "active": 1},
		)


def _seed_customers(regions):
	customers = {}
	for name in ("Teva Global", "Novartis Global"):
		customers[name] = _ensure(
			"CRM Organization",
			{"name": name},
			{
				"organization_name": name,
				"custom_account_type": "Global Parent",
				"custom_customer_status": "Active",
				"custom_is_key_account": 1,
			},
		).name

	for name, parent, region, country in (
		("Teva India", "Teva Global", "India", "India"),
		("Teva Europe", "Teva Global", "Europe", "Germany"),
		("Novartis India", "Novartis Global", "India", "India"),
		("Novartis Europe", "Novartis Global", "Europe", "Switzerland"),
		("Novartis US", "Novartis Global", "North America", "United States"),
	):
		customers[name] = _ensure(
			"CRM Organization",
			{"name": name},
			{
				"organization_name": name,
				"custom_parent_customer": customers[parent],
				"custom_account_type": "Operating Customer",
				"custom_country": _existing("Country", country),
				"custom_region": regions[region],
				"custom_customer_status": "Active",
			},
		).name
	return customers


def _seed_sites(customers):
	sites = {}
	for site_name, site_type, city in (
		("Teva Goa Site", "API Manufacturing", "Goa"),
		("Teva Hyderabad R&D Site", "R&D", "Hyderabad"),
	):
		sites[site_name] = _ensure(
			"Manufacturing Site",
			{"customer": customers["Teva India"], "site_name": site_name},
			{
				"site_name": site_name,
				"customer": customers["Teva India"],
				"site_type": site_type,
				"city": city,
				"country": _existing("Country", "India"),
				"active": 1,
			},
		).name
	return sites


def _seed_contacts_and_affiliations(customers):
	affiliations = {}
	for key, first_name, last_name, customer, designation, department in (
		("teva_india", "Asha", "Demo", "Teva India", "Procurement Manager", "Procurement"),
		("teva_global", "Maya", "Demo", "Teva Global", "Global Regulatory Lead", "Regulatory"),
		("teva_europe", "Emil", "Demo", "Teva Europe", "Technical Director", "R&D"),
		("novartis_india", "Arjun", "Demo", "Novartis India", "Quality Director", "Quality"),
		("novartis_europe", "Lena", "Demo", "Novartis Europe", "Sourcing Lead", "Procurement"),
		("novartis_us", "Taylor", "Demo", "Novartis US", "Portfolio Director", "Commercial"),
	):
		email = f"{key.replace('_', '.')}@contacts.{DEMO_DOMAIN}"
		contact = _ensure_contact(email, first_name, last_name)
		affiliations[key] = _ensure(
			"Contact Affiliation",
			{"contact": contact.name, "affiliation_type": "Customer", "customer": customers[customer]},
			{
				"contact": contact.name,
				"affiliation_type": "Customer",
				"customer": customers[customer],
				"designation": designation,
				"department": department,
				"influence_level": "High",
				"relationship_strength": "Developing",
				"primary_affiliation": 1,
				"start_date": START_DATE,
				"active": 1,
			},
		).name
	return affiliations


def _seed_account_assignments(users, customers):
	for customer, user, assignment_type, primary in (
		("Teva India", users["india_am"], "Primary Account Manager", 1),
		("Teva Europe", users["europe_am"], "Primary Account Manager", 1),
		("Teva Global", users["gam"], "Global Account Manager", 1),
	):
		_ensure(
			"Account Assignment",
			{
				"customer": customers[customer],
				"user": user,
				"assignment_type": assignment_type,
			},
			{"primary": primary, "start_date": START_DATE, "active": 1},
		)


def _seed_products():
	for doctype, field, values in (
		("API Product Category", "category_name", ("Peptide API", "Small Molecule API")),
		("Therapeutic Area", "therapeutic_area_name", ("Metabolic", "Cardiovascular")),
	):
		for value in values:
			_ensure(doctype, {"name": value}, {field: value, "active": 1})

	for index, value in enumerate(("Development", "Commercial"), 1):
		_ensure(
			"Product Commercial Status",
			{"name": value},
			{"status_name": value, "active": 1, "sort_order": index * 10},
		)

	products = {}
	for name, code, category, area, status, pack_size in (
		("Semaglutide", "DEMO-SEMAGLUTIDE", "Peptide API", "Metabolic", "Commercial", 1),
		("Tirzepatide", "DEMO-TIRZEPATIDE", "Peptide API", "Metabolic", "Development", 1),
		("Apixaban", "DEMO-APIXABAN", "Small Molecule API", "Cardiovascular", "Commercial", 5),
	):
		products[name] = _ensure(
			"CRM Product",
			{"product_code": code},
			{
				"product_code": code,
				"product_name": name,
				"disabled": 0,
				"custom_molecule": name,
				"custom_product_category": category,
				"custom_therapeutic_area": area,
				"custom_commercial_status": status,
				"custom_standard_uom": "kg",
				"custom_standard_pack_size": pack_size,
			},
		).name
	return products


def _seed_product_responsibilities(users, products):
	for product in (products["Semaglutide"], products["Tirzepatide"]):
		_ensure(
			"Product Responsibility",
			{"product": product, "user": users["product_manager"]},
			{"primary_responsibility": 1, "start_date": START_DATE, "active": 1},
		)


def _seed_pipeline():
	pipeline_name = "API Commercial Pipeline"
	existing_default = frappe.db.get_value("Pipeline", {"is_default": 1}, "name")
	pipeline = _ensure(
		"Pipeline",
		{"name": pipeline_name},
		{
			"pipeline_name": pipeline_name,
			"active": 1,
			"is_default": not existing_default or existing_default == pipeline_name,
			"description": "Configurable Phase 1 demonstration pipeline.",
		},
	)
	stages = {}
	for name, sequence, probability, won, lost, max_days in (
		("Qualification", 10, 10, 0, 0, 30),
		("Technical Evaluation", 20, 35, 0, 0, 90),
		("Commercial Alignment", 30, 65, 0, 0, 60),
		("Won", 40, 100, 1, 0, 0),
		("Lost", 50, 0, 0, 1, 0),
	):
		stages[name] = _ensure(
			"Pipeline Stage",
			{"pipeline": pipeline.name, "stage_name": name},
			{
				"pipeline": pipeline.name,
				"stage_name": name,
				"sequence": sequence,
				"default_probability": probability,
				"recommended_max_days": max_days,
				"is_won_stage": won,
				"is_lost_stage": lost,
				"active": 1,
			},
		).name
	return pipeline.name, stages


def _seed_target_markets():
	markets = {}
	for name, code in (("US", "US"), ("EU", "EU"), ("Canada", "CA")):
		markets[name] = _ensure(
			"Target Market",
			{"name": name},
			{"market_name": name, "market_code": code, "active": 1},
		).name
	return markets


def _seed_opportunities(users, customers, sites, products, pipeline, stages):
	opportunities = {}
	for key, customer, product, owner, stage, site, priority, next_action, due_date in (
		("teva_india_semaglutide", "Teva India", "Semaglutide", "india_am", "Technical Evaluation", "Teva Goa Site", "High", "Confirm technical sample review", "2026-10-15"),
		("teva_europe_semaglutide", "Teva Europe", "Semaglutide", "europe_am", "Commercial Alignment", None, "High", "Align European launch assumptions", "2026-10-30"),
		("novartis_india_apixaban", "Novartis India", "Apixaban", "india_head", "Qualification", None, "Medium", "Confirm India demand scenario", "2026-11-10"),
		("novartis_europe_tirzepatide", "Novartis Europe", "Tirzepatide", "europe_am", "Technical Evaluation", None, "High", "Schedule technical workshop", "2026-11-20"),
		("novartis_us_tirzepatide", "Novartis US", "Tirzepatide", "gam", "Qualification", None, "Medium", "Identify US technical sponsor", "2026-12-01"),
	):
		opportunities[key] = _ensure(
			"Product Opportunity",
			{"customer": customers[customer], "product": products[product]},
			{
				"customer": customers[customer],
				"product": products[product],
				"manufacturing_site": sites.get(site),
				"opportunity_owner": users[owner],
				"pipeline": pipeline,
				"current_stage": stages[stage],
				"strategic_priority": priority,
				"opportunity_type": "New Business",
				"status": "Active",
				"next_action": next_action,
				"next_action_due_date": due_date,
				"action_owner": users[owner],
				"expected_commercial_supply_date": "2027-06-01",
			},
		).name
	return opportunities


def _seed_opportunity_markets(opportunities, markets):
	rows = (
		("teva_india_semaglutide", "US", 240, 820, 196800, "2027-06-01", 40),
		("teva_india_semaglutide", "EU", 180, 800, 144000, "2027-09-01", 35),
		("teva_europe_semaglutide", "EU", 320, 790, 252800, "2027-03-01", 70),
		("novartis_india_apixaban", "US", 1200, 95, 114000, "2028-01-01", 15),
		("novartis_europe_tirzepatide", "EU", 150, 980, 147000, "2028-04-01", 40),
		("novartis_us_tirzepatide", "US", 210, 1000, 210000, "2028-06-01", 20),
		("novartis_us_tirzepatide", "Canada", 40, 1010, 40400, "2028-09-01", 15),
	)
	for opportunity, market, volume, price, revenue, launch_date, probability in rows:
		_ensure(
			"Opportunity Market",
			{"opportunity": opportunities[opportunity], "target_market": markets[market]},
			{
				"opportunity": opportunities[opportunity],
				"target_market": markets[market],
				"estimated_annual_volume": volume,
				"volume_uom": "kg",
				"currency": _existing("Currency", "USD"),
				"expected_selling_price": price,
				"expected_revenue": revenue,
				"expected_launch_date": launch_date,
				"probability_override": probability,
				"filing_status": "Planning",
			},
		)


def _seed_stakeholders(opportunities, affiliations):
	for role in ("Decision Maker", "Procurement", "Technical Evaluator", "Quality", "Regulatory", "Sponsor", "Champion", "Influencer", "Blocker"):
		_ensure(
			"Opportunity Stakeholder Role",
			{"name": role},
			{"role_name": role, "active": 1},
		)

	for opportunity, affiliation, role, primary, influence, sentiment, power in (
		("teva_india_semaglutide", "teva_india", "Procurement", 1, "High", "Positive", "High"),
		("teva_india_semaglutide", "teva_global", "Regulatory", 0, "High", "Neutral", "Medium"),
		("teva_europe_semaglutide", "teva_europe", "Technical Evaluator", 1, "High", "Positive", "High"),
		("novartis_india_apixaban", "novartis_india", "Quality", 1, "High", "Neutral", "High"),
		("novartis_europe_tirzepatide", "novartis_europe", "Procurement", 1, "High", "Positive", "High"),
		("novartis_us_tirzepatide", "novartis_us", "Decision Maker", 1, "High", "Neutral", "High"),
	):
		_ensure(
			"Opportunity Stakeholder",
			{
				"opportunity": opportunities[opportunity],
				"contact_affiliation": affiliations[affiliation],
				"opportunity_role": role,
			},
			{
				"opportunity": opportunities[opportunity],
				"contact_affiliation": affiliations[affiliation],
				"opportunity_role": role,
				"primary_contact": primary,
				"influence": influence,
				"sentiment": sentiment,
				"decision_power": power,
			},
		)


def _ensure_contact(email, first_name, last_name):
	name = frappe.db.get_value("Contact", {"email_id": email}, "name")
	if name:
		contact = frappe.get_doc("Contact", name)
	else:
		contact = frappe.new_doc("Contact")
	changed = not name
	if contact.first_name != first_name:
		contact.first_name = first_name
		changed = True
	if contact.last_name != last_name:
		contact.last_name = last_name
		changed = True
	if not any(row.email_id == email for row in contact.email_ids):
		contact.append("email_ids", {"email_id": email, "is_primary": 1})
		changed = True
	if changed:
		contact.flags.ignore_permissions = True
		contact.save()
	return contact


def _ensure(doctype, filters, values):
	name = frappe.db.get_value(doctype, filters, "name")
	doc = frappe.get_doc(doctype, name) if name else frappe.new_doc(doctype)
	changed = not name
	requested_values = values if name else {**filters, **values}
	for fieldname, value in requested_values.items():
		if cstr(doc.get(fieldname)) != cstr(value):
			doc.set(fieldname, value)
			changed = True
	if changed:
		doc.flags.ignore_permissions = True
		doc.save()
	return doc


def _existing(doctype, name):
	return name if frappe.db.exists(doctype, name) else None
