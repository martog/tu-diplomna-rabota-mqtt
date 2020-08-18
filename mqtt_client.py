import paho.mqtt.client as paho
import os
import urllib.parse as urlparse
import re
import hashlib

# Define event callbacks


def on_connect(mosq, obj, rc):
    print("rc: " + str(rc))


def on_message(mosq, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mosq, obj, level, string):
    print(string)


def get_device_serial():
    device_serial = "0000000000000000"

    with open('/proc/cpuinfo', 'r') as f:
        device_serial = f.read()
        search = re.search(
            "\nSerial\s+:\s+(?P<serial>[0-9a-f]{16})$", device_serial)

        if search is None:
            raise BaseException("Cannot find device serial!")

    return search.group("serial")


# Create new mqtt Client instance
mqttc = paho.Client()

# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#mqttc.on_log = on_log

device_serial = get_device_serial()
password = hashlib.md5(device_serial.encode('utf-8')).hexdigest()


# Connect
mqttc.username_pw_set(device_serial, password)
mqttc.connect("mqtt.eclipse.org", 1883, 60)

# Start subscribe, with QoS level 0
mqttc.subscribe("relay/1", 0)
mqttc.subscribe("relay/2", 0)
mqttc.subscribe("relay/3", 0)
mqttc.subscribe("relay/4", 0)


# Publish a message
# mqttc.publish("hello/world", "my message")

# # Continue the network loop, exit when an error occurs
mqttc.loop_forever()
