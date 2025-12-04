FROM python:3.12-alpine
LABEL maintainer="andreyomem@gmail.com"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .