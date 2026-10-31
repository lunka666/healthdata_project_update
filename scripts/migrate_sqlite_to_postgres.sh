#!/usr/bin/env bash
set -euo pipefail

# Run from the project root after copying the old PythonAnywhere db.sqlite3 here.
if [[ ! -f db.sqlite3 ]]; then
  echo "ERROR: db.sqlite3 not found. Copy the SQLite database into the project root first." >&2
  exit 1
fi

mkdir -p migration
echo "Exporting HealthRecord rows from SQLite..."
DB_ENGINE=sqlite python manage.py dumpdata records.HealthRecord --indent 2 --output migration/health_records.json

echo "Starting PostgreSQL and Django containers..."
docker compose up -d db web

WEB_ID=$(docker compose ps -q web)
if [[ -z "$WEB_ID" ]]; then
  echo "ERROR: web container is not running." >&2
  exit 1
fi

docker cp migration/health_records.json "$WEB_ID:/tmp/health_records.json"
echo "Importing rows into PostgreSQL..."
docker compose exec web python manage.py loaddata /tmp/health_records.json

echo "Migration completed. Verify record counts in the application before archiving the SQLite file."
