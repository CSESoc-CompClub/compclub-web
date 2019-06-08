FROM python:3

WORKDIR /app
VOLUME /data

RUN pip install -r requirements.txt

COPY . .

ENV DB_PATH=/data/db.sqlite3

EXPOSE 8080
CMD ["gunicorn", "-c","gunicorn.py", "wsgi:application"]
