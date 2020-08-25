import RPi.GPIO as GPIO

class DeviceController:
    config = None
    devices = {}

    def __init__(self, config):
        self.config = config
        self.devices = config["devices"]
        self.setup()

    def setup(self):
        # set gpio mode
        if self.config["mode"] == "BCM":
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)

        # set devices pins as output
        for (device, pin) in self.devices.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 1)

    def get_devices(self):
        return self.devices
        
    def get_devices_info(self):
        devices_info = {}
        
        for (device, pin) in self.devices.items():
            devices_info[device] = {
                "pin": pin,
                "status": "Off" if GPIO.input(pin) else "On"  
            }      
        
        return devices_info  

    def cleanup(self):
        print("Calling GPIO.cleanup()")
        GPIO.cleanup()

    def set_device_active(self, device_name, active: bool):
        device_pin = self.devices.get(device_name)

        if active:
            GPIO.output(device_pin, 0)
            print(device_pin, 0)
        else:
            GPIO.output(device_pin, 1)
            print(device_pin, 1)
