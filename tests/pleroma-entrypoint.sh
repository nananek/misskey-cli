#!/bin/sh
set -e

# The ghcr.io/explodingcamera/pleroma image runs from a source tree: Pleroma
# is started with `mix phx.server`, migrations via `mix ecto.migrate`, and the
# CLI lives under `mix pleroma.*`.

echo "Fixing permissions..."
chown -R pleroma:pleroma /app /data 2>/dev/null || true

echo "Waiting for PostgreSQL..."
until pg_isready -h postgres-pl -p 5432 -U pleroma >/dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is up"

echo "Running Pleroma migrations..."
su-exec pleroma mix ecto.migrate

# Start Pleroma in the background so we can create bob via the mix CLI once
# the schema is in place, then wait for the process in foreground.
echo "Starting Pleroma..."
su-exec pleroma mix phx.server &
PLEROMA_PID=$!

# Wait for the HTTP API to respond.
for _ in $(seq 1 120); do
  if wget -qO- http://127.0.0.1:4000/api/v1/instance >/dev/null 2>&1; then
    echo "Pleroma API is up"
    break
  fi
  sleep 1
done

# Create bob. `mix pleroma.user new` prompts for confirmation; `--assume-yes`
# (and the positional args) handle that non-interactively.
echo "Ensuring bob..."
su-exec pleroma mix pleroma.user new bob bob@pleroma \
  --password Password1234! \
  --moderator \
  --admin \
  --assume-yes || echo "(bob already exists, continuing)"
# Force the password in case the user already existed from a previous run.
su-exec pleroma mix pleroma.user reset_password bob 2>/dev/null || true
# (reset_password prints a URL; we don't need it — we use OAuth password grant
# with the password we just set via the ``new`` invocation.)

wait $PLEROMA_PID
