FROM python:3.10.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

VOLUME /base_bot
WORKDIR /base_bot

RUN apt-get update && apt-get install build-essential libffi-dev -y
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --user
RUN apt-get --purge remove build-essential -y
RUN apt-get upgrade -y

COPY . .

ENTRYPOINT [ "python3", "bot.py" ]
