# Arkenstone CRM

Arkenstone CRM is a commercial CRM for an Active Pharmaceutical Ingredient business.

The application extends Frappe Framework and Frappe CRM without modifying or
forking their core code. The reproducible development baseline is:

- Frappe Framework: `v15.120.0`
- Frappe CRM: `v1.83.0`
- Custom application: `api_commercial`

Phase 1 architecture and scope decisions are recorded in
[`docs/architecture.md`](docs/architecture.md). The planned schema and access
rules are in [`docs/data-model.md`](docs/data-model.md) and
[`docs/security.md`](docs/security.md).

Brand assets and the upgrade-safe branding configuration are documented in
[`docs/branding.md`](docs/branding.md).

## Local development

Prerequisites: Docker Desktop and Git.

```bash
docker compose up -d
docker compose logs -f frappe
```

Initial setup downloads Frappe Framework and Frappe CRM and creates the local
site, so it can take several minutes. When setup completes, open:

- CRM: <http://api-crm.localhost:8000/crm>
- User: `Administrator`
- Development password: `admin`

Generated bench files and database data remain in Docker volumes and are not
committed to this repository.
