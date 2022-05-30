# pull base image
FROM python:3.10
WORKDIR /WAYD
ENV PYTHONDONTWIRTEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY Pipfile Pipfile.lock /WAYD/
RUN pip install pipenv && pipenv install --dev --system
