FROM python:buster

WORKDIR /app

COPY ./app /app
RUN pip install gunicorn
RUN pip install -r /app/requirements.txt

EXPOSE 8967

HEALTHCHECK CMD curl --fail http://localhost:8967 || exit 1

CMD ["gunicorn"  , "-b", "0.0.0.0:8967", "main:app"]
