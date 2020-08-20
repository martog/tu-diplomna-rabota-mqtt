from device_controller import DeviceController
from mqtt_client import MqttClient
from config import mqtt as mqtt_config, gpio as devices_config


class SmartHomeController:
    device_controller = None
    mqtt_client = None

    def __init__(self):
        self.device_controller = DeviceController(devices_config)
        devices = self.device_controller.get_devices()

        try:
            self.mqtt_client = MqttClient(
                mqtt_config, devices, self.onMessageReceivedCallback)
            self.mqtt_client.connect()
        finally:
            self.device_controller.cleanup()

    def onMessageReceivedCallback(self, mqttc, user_data, msg):
        device = msg.topic
        message = msg.payload.decode("utf-8")

        # Set device state
        active = None
        if(message == "On"):
            active = True

        if(message == "Off"):
            active = False

        self.device_controller.set_device_active(device, active)


if __name__ == "__main__":
    sh = SmartHomeController()
