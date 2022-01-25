FROM python:3.8

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wkhtmltopdf \
    xvfb

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN printf '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf -q $*' > /usr/bin/wkhtmltopdf.sh
RUN chmod a+x /usr/bin/wkhtmltopdf.sh
RUN ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000