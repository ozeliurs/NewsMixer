FROM python:3.8-slim-buster

WORKDIR /app

COPY ./app /app
RUN pip install gunicorn
RUN pip install -r /app/requirements.txt

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000 || exit 1

CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "main:app"]