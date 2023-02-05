import pika
import os
import math
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class Analytics():
    max_value = -math.inf
    min_value = math.inf
    influx_bucket = 'rabbit'
    influx_token = 'token-secreto'
    influx_url = 'http://influxdb:8086'
    influx_org = 'org'
    step_days = 0
    step_sum = 0
    day_max_min_preset = [5000, 100000]
    days_100k = 0
    days_5k = 0
    prev_value = 0
    days_consecutive = 0

    def write_db(self, tag, key, value):
        client = InfluxDBClient(
            url=self.influx_url,
            token=self.influx_token,
            org=self.influx_org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = Point('Analytics').tag("Descriptive", tag).field(key, value)
        write_api.write(bucket=self.influx_bucket, record=point)

    def add_max_value(self, _measurement):
        if _measurement > self.max_value:
            # print("New max", flush=True)
            self.max_value = _measurement
        self.write_db('steps', "Maximum", self.max_value)

    def add_min_value(self, _measurement):
        if _measurement < self.min_value:
            # print("New min", flush=True)
            self.min_value = _measurement
        self.write_db('steps', "Minimum", self.min_value)

    def get_mean(self, _measurement):
        self.step_days += 1
        self.step_sum += _measurement
        mean = self.step_sum / self.step_days
        print("mean {}".format(mean), flush=True)
        self.write_db('steps', "mean", mean)

    def get_days_100k(self, _measurement):
        if _measurement >= self.day_max_min_preset[1]:
            self.days_100k += 1
            print("days_100k {}".format(self.days_100k), flush=True)
        self.write_db('steps', "higher_than_days_100k", self.days_100k)

    def get_days_5k(self, _measurement):
        if _measurement <= self.day_max_min_preset[0]:
            self.days_5k += 1
            print("days_5k {}".format(self.days_5k), flush=True)
        self.write_db('steps', "less_than_days_5k", self.days_5k)

    def get_consecutive_days(self, _measurement):
        if _measurement >= self.day_max_min_preset[0]:
            self.days_consecutive += 1
        else:
            self.days_consecutive = 0
        print("days_consecutive {}".format(self.days_consecutive), flush=True)
        self.prev_value = _measurement
        self.write_db('steps', "days_consecutive", self.days_consecutive)

    def add_days_steps(self, _measurement):
        print(f'Steps today {_measurement}')
        self.write_db('steps', "days_steps", _measurement)

    def take_measurement(self, _message):
        message = _message.split("=")
        measurement = float(message[-1])
        print("measurement {}".format(measurement), flush=True)
        self.add_max_value(measurement)
        self.add_min_value(measurement)
        self.get_mean(measurement)
        self.get_days_100k(measurement)
        self.get_days_5k(measurement)
        self.get_consecutive_days(measurement)
        self.add_days_steps(measurement)


if __name__ == '__main__':

    analytics = Analytics()

    def callback(ch, method, properties, body):
        global analytics
        # print(" [x] Received %r" % body)
        message = body.decode("utf-8")
        # print("message from rabbit: {}".format(message), flush=True)
        analytics.take_measurement(message)

    url = os.environ.get('AMQP_URL', 'amqp://guest:guest@rabbit:5672/%2f')
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()
    channel.queue_declare(queue='watch_measurements')
    channel.queue_bind(
        exchange='amq.topic',
        queue='watch_measurements',
        routing_key='steps_data')
    channel.basic_consume(
        queue='watch_measurements',
        on_message_callback=callback,
        auto_ack=True)
    channel.start_consuming()
