FROM python:3.8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wkhtmltopdf \
    xvfb \
    gettext

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN printf '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf $*' > /usr/bin/wkhtmltopdf.sh
RUN chmod a+x /usr/bin/wkhtmltopdf.sh
RUN ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

RUN python3 manage.py compilemessages

EXPOSE 8000
