FROM python:3.9.16

WORKDIR /app

RUN apt-get update && apt install -y python3-aiohttp

RUN pip install python-weather

RUN pip install influxdb-client==1.36

COPY ./app.py /app/

CMD ["python", "/app/app.py"]
