FROM node:20 AS frontend-builder

WORKDIR /app/goback-frontend

COPY goback-frontend/package.json goback-frontend/package-lock.json ./
RUN npm install

COPY goback-frontend/ ./

RUN npm run build

FROM python:3.11-slim

WORKDIR /app

COPY --from=frontend-builder /app/goback-frontend/dist ./goback-frontend/dist

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "webserver:app", "--host", "0.0.0.0", "--port", "80"]
