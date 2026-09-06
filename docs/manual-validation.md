# Manual Phase 1 persona validation

Automated tests remain the authoritative regression check. This checklist
verifies that list views, direct URLs, forms, and role-oriented workflows expose
the same server-side policy. A hidden menu item or client-side filter is not a
security test.

## Prepare deterministic test data

Create separate enabled users for these personas and assign only the stated
commercial role unless a test explicitly combines roles:

- India Account Manager
- India Region Head
- Europe Account Manager
- Global Account Manager
- Semaglutide Product Manager
- Leadership User

Create Regions `India`, `Europe`, and `North America`. Create `Teva Global` with
children `Teva India` and `Teva Europe`, plus an unrelated `Novartis Global`
hierarchy. Give operating Customers the appropriate relationship-owning Region.
Add a Teva India Manufacturing Site and Contact Affiliation. Create Semaglutide
and Apixaban Products, then create Product Opportunities for multiple Customers
and Regions.

Create active, currently effective grants:

- India Account Manager -> Teva India account assignment
- India Region Head -> India Region membership with Region Head role
- Global Account Manager -> Teva Global cascading account assignment
- Semaglutide Product Manager -> Semaglutide Product Responsibility

Use fictional contact data. Record each generated document URL so the same
record can be tested by direct navigation, not only from filtered lists.

## Account Manager

Sign in as the India Account Manager.

- Confirm Teva India is visible in My Accounts/customer search.
- Confirm its Manufacturing Sites, affiliated Contacts, Product Opportunities,
  Opportunity Markets, and Stakeholders are visible.
- Confirm an unrelated India Customer is not visible without an assignment.
- Confirm Teva Europe is not visible merely because it shares Teva Global.
- Paste the recorded Teva Europe and unrelated Customer URLs directly; both
  must be denied.
- Confirm catalogue Products remain readable while Product editing is denied.

## Region Head

Sign in as the India Region Head.

- Confirm every Customer in India and their Sites, Contacts, and Opportunities
  is visible, including Customers without an Account Manager assignment.
- Confirm Europe-only Customers and Opportunities are absent.
- Paste a Europe Customer and Opportunity URL directly; access must be denied.
- If Regions are nested, confirm child Regions inside India inherit visibility
  while sibling Regions do not.

## Global Account Manager

Sign in as the Global Account Manager.

- Confirm Teva Global, Teva India, and Teva Europe are visible across Regions.
- Confirm Sites, Contacts, and Opportunities below those Customers are visible.
- Confirm the unrelated Novartis hierarchy is not visible.
- Confirm access to a child does not make the user Opportunity Owner.
- Assign the user only to Teva India in a separate check and confirm that Teva
  Europe does not become visible sideways through the shared parent.

## Product Manager

Sign in as the Semaglutide Product Manager.

- Confirm the full Product Catalogue is readable.
- Confirm Semaglutide Product Opportunities are visible across India and Europe.
- Confirm Apixaban Opportunities are not visible solely through the
  Semaglutide responsibility.
- Confirm Opportunity Markets and Stakeholders inherit the same readable scope.
- Confirm Product-responsibility access is read-only and does not make the user
  Account Manager, GAM, or Opportunity Owner.
- Paste a known Apixaban Opportunity URL directly; access must be denied unless
  another valid grant applies.

## Leadership

Sign in as the Leadership User.

- Confirm Customers and Product Opportunities are broadly readable across
  Regions and Products.
- Confirm broad read access does not confer broad edit, delete, assignment, or
  administration rights.
- Confirm Product Catalogue access is read-only.
- Confirm restricted configuration pages remain unavailable unless the user
  also has CRM Admin.

## Additive and dated access

Give one user both an Account assignment and Product Responsibility. Confirm the
visible records are the union of both grants, while write access does not widen
from a read-only Product Manager path.

Then test each assignment type with a future start date, past end date, and
inactive flag. In every case the expired or inactive path must disappear from
lists and direct document access after cache refresh. Restore a current active
grant and confirm access returns.

## Audit and integrity

- Change an Account Assignment, Product Responsibility, Product Opportunity
  owner/stage/probability, Region, and an Opportunity Market assumption; confirm
  Frappe version history identifies the actor and changed values.
- Attempt overlapping dated assignments and responsibilities; saving must fail.
- Attempt a Customer hierarchy cycle; saving must fail.
- Attempt a second active Customer + Product Opportunity without an authorized
  override; saving must fail.
- Confirm Region and Target Market remain distinct and that Opportunity Region
  derives from the Customer rather than a Target Market.

After manual checks, run the complete automated suite documented in
`developer-setup.md` and record the commit, browser, persona, and result for the
acceptance review.
