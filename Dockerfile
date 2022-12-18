FROM python:3.8-alpine

WORKDIR /app

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv sync

COPY . .

CMD ["python", "dictator/dictator.py"]