import paho.mqtt.client as paho
import os
import urllib.parse as urlparse
import re
import hashlib
import RPi.GPIO as GPIO
import time
import config


class MqttClient():
    def __init__(self):


RELAY_1_PIN = 23
RELAY_2_PIN = 24
RELAY_3_PIN = 22
RELAY_4_PIN = 27


def setup_relay_pins():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_1_PIN, GPIO.OUT)
    GPIO.setup(RELAY_2_PIN, GPIO.OUT)
    GPIO.setup(RELAY_3_PIN, GPIO.OUT)
    GPIO.setup(RELAY_4_PIN, GPIO.OUT)


def relay_1_on():
    GPIO.output(RELAY_1_PIN, 0)


def relay_1_off():
    GPIO.output(RELAY_1_PIN, 1)


def relay_2_on():
    GPIO.output(RELAY_2_PIN, 0)


def relay_2_off():
    GPIO.output(RELAY_2_PIN, 1)


def relay_3_on():
    GPIO.output(RELAY_3_PIN, 0)


def relay_3_off():
    GPIO.output(RELAY_3_PIN, 1)


def relay_4_on():
    GPIO.output(RELAY_4_PIN, 0)


def relay_4_off():
    GPIO.output(RELAY_4_PIN, 1)


def on_connect(mosq, obj, rc):
    print("rc: " + str(rc))


def on_disconnect(mosq, obj, rc):
    if rc != 0:
        print("Unexpected MQTT disconnection. Will auto-reconnect")
        connect_to_mqtt_server(mqttc)


def on_message(mosq, obj, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    topic = msg.topic
    message = msg.payload.decode("utf-8")

    print(topic, message)

    if topic == "device_1":
        if message == "On":
            relay_1_on()
        else:
            relay_1_off()

    if topic == "device_2":
        if message == "On":
            relay_2_on()
        else:
            relay_2_off()

    if topic == "device_3":
        if message == "On":
            relay_3_on()
        else:
            relay_3_off()

    if topic == "device_4":
        if message == "On":
            relay_4_on()
        else:
            relay_4_off()


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mosq, obj, level, string):
    print(string)


def connect_to_mqtt_server(mqttc):
    device_serial = get_device_serial()
    password = hashlib.md5(device_serial.encode('utf-8')).hexdigest()

    # Connect
    mqttc.username_pw_set(device_serial, password)
    while True:
        print("Trying to connect to MQTT server...")
        time.sleep(2)
        try:
            mqttc.connect("mqtt.eclipse.org", 1883, 5)
        except:
            continue

        print("Connected")
        break

   # Start subscribe, with QoS level 0
    mqttc.subscribe("device_1", 0)
    mqttc.subscribe("device_2", 0)
    mqttc.subscribe("device_3", 0)
    mqttc.subscribe("device_4", 0)

    # Publish a message
    # mqttc.publish("hello/world", "my message")

    # # Continue the network loop, exit when an error occurs
    mqttc.loop_forever()


if __name__ == "__main__":
    setup_relay_pins()
    relay_1_off()
    relay_2_off()
    relay_3_off()
    relay_4_off()

    try:
        # Create new mqtt Client instance
        mqttc = paho.Client()

        # Assign event callbacks
        mqttc.on_message = on_message
        mqttc.on_connect = on_connect
        mqttc.on_disconnect = on_disconnect
        mqttc.on_publish = on_publish
        mqttc.on_subscribe = on_subscribe

        connect_to_mqtt_server(mqttc)

    finally:
        GPIO.cleanup()
