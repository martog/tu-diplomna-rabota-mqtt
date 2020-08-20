import paho.mqtt.client as paho
import os
import urllib
import re
import hashlib
import time


class MqttClient():
    config = None
    mqtt_client = None
    topics = []

    def __init__(self, config, topicsToSubscribe, onMsgReceivedCallback=None):
        self.config = config
        self.topics = topicsToSubscribe

        self.mqtt_client = paho.Client()

        # Assign event callbacks
        self.mqtt_client.on_message = onMsgReceivedCallback if onMsgReceivedCallback is not None else self.on_message
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_publish = self.on_publish
        self.mqtt_client.on_subscribe = self.on_subscribe

    def wait_for_connection(self):
        print("Waiting for connection...")
        while True:
            try:
                urllib.request.urlopen(self.config["connection_check_url"])
                print("Connected!")
                return
            except:
                time.sleep(self.config["timeout"])
                continue

    def connect(self):
        device_serial = self.get_device_serial()
        password = hashlib.md5(device_serial.encode('utf-8')).hexdigest()

        # Connect
        self.mqtt_client.username_pw_set(device_serial, password)
        self.wait_for_connection()
        self.mqtt_client.connect(
            self.config["url"], self.config["port"], self.config["keep_alive"])

        # Continue the network loop, exit when an error occurs
        self.mqtt_client.loop_forever(timeout=self.config["timeout"])

    def on_connect(self, mqttc, user_data, flags, rc):
        print("rc: " + str(rc))

        for topic in self.topics:
            mqttc.subscribe(topic, self.config["qos"])

    def on_disconnect(self, mqttc, user_data, rc):
        if rc != 0:
            print("Unexpected MQTT disconnection. Will auto-reconnect")

    @staticmethod
    def on_message(mqttc, user_data, msg):
        topic = msg.topic
        message = msg.payload.decode("utf-8")

        print(topic, message)

    @staticmethod
    def on_publish(mqttc, user_data, mid):
        print("mid: " + str(mid))

    @staticmethod
    def on_subscribe(mqttc, user_data, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    @staticmethod
    def get_device_serial():
        device_serial = "0000000000000000"

        with open('/proc/cpuinfo', 'r') as f:
            device_serial = f.read()
            search = re.search(
                r"\nSerial\s+:\s+(?P<serial>[0-9a-f]{16})", device_serial)

            if search is None:
                return "asd"
                # raise BaseException("Cannot find device serial!")

        return search.group("serial")
