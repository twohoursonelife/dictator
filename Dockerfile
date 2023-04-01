FROM python:3.11-alpine as requirements

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv requirements > requirements.txt



FROM python:3.11-alpine

WORKDIR /usr/local/dictator

COPY --from=requirements requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV BOT_TOKEN=token \
    DB_PASS=password \
    OC_GRAPHQL_KEY=key

CMD ["python", "-u", "dictator/dictator.py"]
