FROM python:3

WORKDIR /app
VOLUME /data

RUN pip install pipenv

# Install dependencies into their own layer so they are cached between code changes
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

ENV DB_PATH=/data/db.sqlite3

EXPOSE 8080
CMD ["gunicorn", "-c","gunicorn.py", "wsgi:application"]
