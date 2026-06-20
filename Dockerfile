FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (requirements.txt esta en el nivel gastos_personales/gastos_personales/)
COPY gastos_personales/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Node deps: instala desde el package.json del proyecto y agrega el CLI v4 explicitamente
# El package.json lista tailwindcss v3 pero el CSS usa sintaxis v4 (@import "tailwindcss")
# @tailwindcss/cli es el CLI oficial de v4 y procesa la sintaxis correctamente
COPY package*.json ./
RUN npm install && npm install --no-save @tailwindcss/cli

# entrypoint fuera de /app para que el volume mount no lo pise
COPY entrypoint.sh /entrypoint.sh

EXPOSE 8000

CMD ["sh", "/entrypoint.sh"]
