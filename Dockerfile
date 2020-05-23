FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev nginx python3-dev
RUN pip install pipenv

# Install dependencies into their own layer so they are cached between code changes
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

ENV DB_PATH=/data/db.sqlite3
ENV DJANGO_SETTINGS_MODULE=settings_prod

RUN chmod +x run.sh

EXPOSE 8080

CMD ["./run.sh"]
