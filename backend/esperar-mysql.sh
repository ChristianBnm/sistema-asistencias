#!/bin/bash
set -e

host="$1"
port="$2"
shift 2

MAX_RETRIES=30
RETRY_INTERVAL=2
COUNTER=0

echo "⏳ Esperando a que MySQL en $host:$port esté listo..."

until nc -z "$host" "$port"; do
  COUNTER=$((COUNTER + 1))
  if [ "$COUNTER" -ge "$MAX_RETRIES" ]; then
    echo "❌ Error: MySQL no respondió tras $((MAX_RETRIES * RETRY_INTERVAL)) segundos."
    exit 1
  fi
  echo "🔁 MySQL aún no responde… reintento ($COUNTER/$MAX_RETRIES) en $RETRY_INTERVAL s"
  sleep "$RETRY_INTERVAL"
done

echo "✅ MySQL está listo en $host:$port"
exec "$@"