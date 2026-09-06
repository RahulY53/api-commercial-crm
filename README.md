# API Commercial CRM

Phase 1 of a commercial CRM for an Active Pharmaceutical Ingredient business.

The application extends Frappe Framework and Frappe CRM without modifying or
forking their core code. The supported local development baseline is:

- Frappe Framework: `version-15`
- Frappe CRM: `main` (stable v1.x)
- Custom application: `api_commercial`

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

