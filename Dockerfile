FROM python:3.13-alpine3.21

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]