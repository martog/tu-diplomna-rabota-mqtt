from device_controller import DeviceController
from mqtt_client import MqttClient
from config import mqtt as mqtt_config, gpio as devices_config
import re


class SmartHomeController:
    device_controller = None
    mqtt_client = None
    device_serial = None

    def __init__(self):
        self.device_serial = self.get_device_serial()
        self.device_controller = DeviceController(devices_config)
        devices = self.device_controller.get_devices()
        topics = list(map(lambda device: self.device_serial + "/" + device, devices))

        try:
            self.mqtt_client = MqttClient(
                mqtt_config, topics, self.onMessageReceivedCallback)
            self.mqtt_client.connect(self.device_serial)
        finally:
            self.device_controller.cleanup()

    def onMessageReceivedCallback(self, mqttc, user_data, msg):
        device = msg.topic.split("/")[1]
        message = msg.payload.decode("utf-8")

        # Set device state
        active = None
        if(message == "On"):
            active = True

        if(message == "Off"):
            active = False

        self.device_controller.set_device_active(device, active)
        
    @staticmethod
    def get_device_serial():
        device_serial = "0000000000000000"

        with open('/proc/cpuinfo', 'r') as f:
            device_serial = f.read()
            search = re.search(
                r"\nSerial\s+:\s+(?P<serial>[0-9a-f]{16})", device_serial)

            if search is None:
                raise BaseException("Cannot find device serial!")

        return search.group("serial")


if __name__ == "__main__":
    sh = SmartHomeController()
