#!/bin/sh
set -e

# Build Tailwind CSS con el CLI v4 (@tailwindcss/cli procesa "@import tailwindcss" correctamente)
# Corre desde /app donde esta tailwind.config.js y package.json
cd /app
echo "test"
#npx @tailwindcss/cli \
#    -i gastos_personales/static/css/src/input.css \
#    -o gastos_personales/static/css/src/output.css \
#    || echo "Warning: CSS build fallido, la app carga igual via CDN"

# Django desde su directorio para que manage.py resuelva paths correctamente
#cd /app/gastos_personales
#python manage.py migrate
#exec python manage.py runserver 0.0.0.0:8000
