# ==========================================
# STAGE 1: Backend Base
# ==========================================
FROM python:3.10-slim AS backend-runner

WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
# Assume models are pre-trained and saved in backend/models
# Run Flask app on container port 5000
CMD ["python", "app.py"]
EXPOSE 5000


# ==========================================
# STAGE 2: Frontend Base
# ==========================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# ==========================================
# STAGE 3: Frontend Runner
# ==========================================
FROM node:18-alpine AS frontend-runner
WORKDIR /app/frontend

COPY --from=frontend-builder /app/frontend/package.json ./
COPY --from=frontend-builder /app/frontend/.next ./.next
COPY --from=frontend-builder /app/frontend/public ./public
COPY --from=frontend-builder /app/frontend/node_modules ./node_modules

CMD ["npm", "run", "start"]
EXPOSE 3000
