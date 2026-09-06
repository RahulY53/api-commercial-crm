# Developer setup

## Supported local baseline

| Component | Pinned version |
| --- | --- |
| Frappe Framework | `v15.120.0` |
| Frappe CRM | `v1.83.0` |
| MariaDB | `10.8` locally (`10.6` in CI) |
| Node.js | `18` in CI |
| Python | `3.10` in CI |

The application is developed as a separate Frappe app. Do not edit files below
the generated bench copies of Frappe or CRM. Dependency revisions are pinned in
`docker/init.sh` and `.github/workflows/ci.yml`; upgrades must be deliberate and
must rerun the complete permission and domain test suites.

## First-time setup

Install Docker Desktop and Git, then clone and start the repository:

```bash
git clone https://github.com/RahulY53/api-commercial-crm.git
cd api-commercial-crm
docker compose up -d
docker compose logs -f frappe
```

The first run initializes the bench, downloads the pinned Frappe and CRM
versions, builds assets, creates `api-crm.localhost`, and installs
`api_commercial`. Wait until the web process is ready, then open
<http://api-crm.localhost:8000/crm>.

Local development login:

- User: `Administrator`
- Password: `admin`

These credentials are for the disposable local site only and must never be
used in another environment.

## Everyday commands

Start or stop the stack from the repository root:

```bash
docker compose up -d
docker compose stop
```

Inspect container state and follow the application log:

```bash
docker compose ps
docker compose logs -f frappe
```

After pulling schema, customization, or hook changes, run the supported Frappe
migration and clear cached metadata:

```bash
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site api-crm.localhost migrate'
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site api-crm.localhost clear-cache'
```

Rebuild application assets when frontend or workspace assets change:

```bash
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench build --app api_commercial'
```

## Tests and checks

Enable tests on the local development site once, then run the app suite:

```bash
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site api-crm.localhost set-config allow_tests true'
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site api-crm.localhost run-tests --app api_commercial'
```

Run the same tests after every schema or permission change. Before opening a
pull request, also run the repository checks:

```bash
pre-commit run --all-files
git diff --check
```

CI creates a clean site with the pinned dependency versions and runs the whole
server test suite. A passing local site is useful but is not a substitute for a
clean-install CI run.

## Demo data

Load or reconcile the deterministic fictional Phase 1 persona dataset with:

```bash
docker compose exec frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site api-crm.localhost execute api_commercial.demo.seed'
```

The command is idempotent. It uses reserved `.example` email addresses, sends
no welcome mail, and assigns no known password. An administrator must explicitly
set a local password before signing in as a demo persona.

## Troubleshooting

- If the CRM page is unavailable, use `docker compose ps` and inspect the
  `frappe` log for an incomplete first-time build.
- If a new field or DocType is missing, run `migrate`, then `clear-cache`, and
  refresh the browser.
- If port `8000` or `9000` is already occupied, stop the conflicting local
  process before starting this stack; do not silently change the checked-in
  ports.
- Generated bench state is stored in `.bench` and database state in the Docker
  volume. Treat removal of either as destructive because it discards local
  site state.
