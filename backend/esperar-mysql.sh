#!/bin/bash
set -e

host="$1"
port="$2"
shift 2 

echo "⏳ Esperando a que MySQL en $host:$port esté listo..."
until nc -z "$host" "$port"; do
  echo "MySQL aún no responde… reintento en 2 s"
  sleep 2
done

echo "✅ MySQL está listo"
exec "$@" 
