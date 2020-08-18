import paho.mqtt.client as paho
import os
import urllib.parse as urlparse
import re
import hashlib
import RPi.GPIO as GPIO 

# Define event callbacks


RELAY_1_PIN = 23;
RELAY_2_PIN = 24;
RELAY_3_PIN = 22;
RELAY_4_PIN = 27;

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


if __name__ == "__main__":
    setup_relay_pins()
    relay_1_on()
    relay_2_off()
    relay_3_off()
    relay_4_off()
    try:
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
    finally:
        GPIO.cleanup()
