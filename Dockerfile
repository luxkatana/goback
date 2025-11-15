FROM node:20 as builder

WORKDIR goback-frontend
COPY goback-frontend/ .
RUN npm i && npm run build
WORKDIR /app


FROM python:3.13.7 as webserver
WORKDIR /app
COPY *.py requirements.txt /app/

COPY --from=builder goback-frontend/dist /app/goback-frontend/dist

RUN pip3 install -r requirements.txt


EXPOSE 8000
CMD ["uvicorn", "webserver:app", "--port", "8000", "--host", "0.0.0.0"]

