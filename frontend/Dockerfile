# =========================================================
# Enterprise AI Business Decision Intelligence Platform
# Frontend Dockerfile (Vite + React, served by nginx)
# =========================================================

# ---------------------------------------------------------
# Stage 1 — build the static bundle
# ---------------------------------------------------------
FROM node:22-slim AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# VITE_API_URL is baked into the static bundle at build time,
# since it's a client-side env var (Vite convention).
# Override at build time with:
#   docker build --build-arg VITE_API_URL=https://api.example.com
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ---------------------------------------------------------
# Stage 2 — serve with nginx
# ---------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
