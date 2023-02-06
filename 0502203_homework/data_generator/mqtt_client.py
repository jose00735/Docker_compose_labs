import random
import os
import time
import paho.mqtt.client as mqtt

servidor = "fgt1.chickenkiller.com"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("$SYS/#")


def on_message(client, userdata, msg):
    print(msg.topic + str(msg.payload))


client = mqtt.Client()
client.username_pw_set("guest", password='guest')

client.connect(servidor, 1883, 60)
client.loop_start()

while (1):
    time.sleep(1)
    random.seed(time.time_ns())
    client.publish("steps_data", 'measures steps={}'.format(
        random.randint(2000, 150000)))
