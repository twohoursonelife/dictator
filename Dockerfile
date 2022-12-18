FROM python:3.10-alpine

WORKDIR /dictator

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv sync

COPY . .

CMD ["python", "dictator/dictator.py"]