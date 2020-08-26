from device_controller import DeviceController
from mqtt_client import MqttClient
from config import mqtt as mqtt_config, gpio as devices_config
import re
import json
import time
import threading

class SmartHomeController:
    device_controller = None
    mqtt_client = None
    device_serial = None
    devices = None
    loop_thread = None
    publish_thread = None

    def __init__(self):
        self.device_serial = self.get_device_serial()
        self.device_controller = DeviceController(devices_config)
        self.devices = self.device_controller.get_devices_info()
        topics = [self.device_serial + "/#"]

        print(self.devices)
        
        self.mqtt_client = MqttClient(
            mqtt_config, topics, self.onMessageReceivedCallback)
        self.mqtt_client.connect(self.device_serial)
        
        self.loop_thread = threading.Thread(target=self.mqtt_client.loop, daemon=True)
        self.publish_thread = threading.Thread(target=self.publish_device_data_periodically, daemon=True)

    def onMessageReceivedCallback(self, mqttc, user_data, msg):
        if(msg.topic == (self.device_serial + "/devices/info/req")):
            self.mqtt_client.publish(self.device_serial + "/devices/info", json.dumps(self.device_controller.get_devices_info()))
            return
            
        device = msg.topic.split("/")[1]
        devices_names = list(self.devices.keys())
        
        if(device in devices_names):
            # Set device state
            message = msg.payload.decode("utf-8")
            active = None
            
            if(message == "On"):
                active = True

            if(message == "Off"):
                active = False

            self.device_controller.set_device_active(device, active)
            self.mqtt_client.publish(self.device_serial + "/devices/" + device + "/status", json.dumps(self.device_controller.get_devices_info()[device]))
            
            
    def publish_device_data_periodically(self):
            # Periodically send devices info
        while True:
            self.mqtt_client.publish(self.device_serial + "/devices/info", json.dumps(self.device_controller.get_devices_info()))
            time.sleep(10)
            
    def run(self):
        # Start threads and wacth their status
        while True:
            loop_thread_alive = sh.loop_thread.isAlive()
            publish_thread_alive = sh.publish_thread.isAlive()
            
            print("loop thread active: " + str(loop_thread_alive))
            print("publish thread active: " + str(publish_thread_alive))
            
            if not loop_thread_alive:
                sh.loop_thread.start()
                
            if not publish_thread_alive:
                sh.publish_thread.start()  
                
            
            time.sleep(1)   
        
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
    try:
        sh = SmartHomeController()
        sh.run()
        
    finally:
        sh.device_controller.cleanup()
    
    
        
