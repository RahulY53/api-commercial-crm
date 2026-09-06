#!/usr/bin/env bash
set -euo pipefail

BENCH_DIR=/home/frappe/frappe-bench
SITE_NAME=api-crm.localhost
CUSTOM_APP=api_commercial
CUSTOM_APP_DIR="$BENCH_DIR/apps/$CUSTOM_APP"
FRAPPE_REF=v15.120.0
CRM_REF=v1.83.0
CRM_BRANDING_PATCH=/workspace/docker/crm-branding.patch
CRM_BRANDING_MARKER="$BENCH_DIR/apps/crm/.arkenstone-branding-v1-built"

if [ ! -d "$BENCH_DIR/apps/frappe" ]; then
	bench init --ignore-exist --skip-redis-config-generation "$BENCH_DIR" --version "$FRAPPE_REF"
fi

cd "$BENCH_DIR"

bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

if [ ! -d "$BENCH_DIR/apps/crm" ]; then
	bench get-app crm --branch "$CRM_REF"
fi

# The pinned CRM frontend hardcodes its product name and logo in a handful of
# places with no extension hook. Keep that unavoidable branding delta explicit,
# reviewable and version-checked instead of forking the upstream repository.
if git -C "$BENCH_DIR/apps/crm" apply --check "$CRM_BRANDING_PATCH" 2>/dev/null; then
	git -C "$BENCH_DIR/apps/crm" apply "$CRM_BRANDING_PATCH"
elif ! git -C "$BENCH_DIR/apps/crm" apply --reverse --check "$CRM_BRANDING_PATCH" 2>/dev/null; then
	printf '%s\n' "CRM branding patch does not match pinned CRM ref $CRM_REF" >&2
	exit 1
fi

if [ ! -f "$CRM_BRANDING_MARKER" ]; then
	bench build --app crm
	touch "$CRM_BRANDING_MARKER"
fi

if ! grep -qx "$CUSTOM_APP" "$BENCH_DIR/sites/apps.txt"; then
	printf '%s\n' "$CUSTOM_APP" >> "$BENCH_DIR/sites/apps.txt"
fi

bench pip install --editable "$CUSTOM_APP_DIR"
bench build --app "$CUSTOM_APP"

if [ ! -d "$BENCH_DIR/sites/$SITE_NAME" ]; then
	bench new-site "$SITE_NAME" \
		--mariadb-root-password 123 \
		--admin-password admin \
		--mariadb-user-host-login-scope=%
	bench --site "$SITE_NAME" install-app crm
	bench --site "$SITE_NAME" set-config developer_mode 1
	bench --site "$SITE_NAME" set-config mute_emails 1
	bench --site "$SITE_NAME" set-config server_script_enabled 1
fi

if ! bench --site "$SITE_NAME" list-apps | grep -qx "$CUSTOM_APP"; then
	bench --site "$SITE_NAME" install-app "$CUSTOM_APP"
fi

bench use "$SITE_NAME"
bench --site "$SITE_NAME" clear-cache
exec bench start
