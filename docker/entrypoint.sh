#!/bin/sh
set -eu

echo "Starting Sardoba bot container..."

# Best-effort wait for MySQL (avoid race on first start).
python - <<'PY'
import os, time
import mysql.connector

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "sardoba_bot")

deadline = time.time() + 60
last_err = None
while time.time() < deadline:
    try:
        conn = mysql.connector.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        conn.close()
        print("MySQL is ready.")
        break
    except Exception as e:
        last_err = e
        time.sleep(2)
else:
    print(f"MySQL is not ready after 60s: {last_err}")
PY

exec python /app/bot.py

