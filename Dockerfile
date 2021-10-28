FROM python:3.8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wkhtmltopdf \
    xvfb

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000
