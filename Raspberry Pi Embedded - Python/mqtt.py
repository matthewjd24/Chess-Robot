import paho.mqtt.client as mqtt
import time

class mqtt_handler:
    def __init__(self):
        broker = "10.0.0.251"  # Replace with your broker address
        port = 1883
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.loop_start()
        self.subscribe("target/base")
        self.subscribe("target/elbow")
        self.subscribe("target/shoulder")
        self.subscribe("target/wrist")
        self.subscribe("waiting_for_button")
        self.subscribe("gripper")
        self.client.on_message = self.on_message

        self.base_target = None
        self.base_vel = None
        self.shoulder_target = None
        self.shoulder_vel = None
        self.elbow_target = None
        self.elbow_vel = None
        self.wrist_target = None
        self.wrist_vel = None
        self.gripper_open = False

        self.waiting_for_button = True


    def publish(self, topic, msg):
        self.client.publish(topic, str(msg), retain=True)

    def disconnect(self):
        print("Disconnecting from MQTT...")
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self, topic):
        self.client.subscribe(topic)
        print(f"Subscribed to '{topic}'")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        #print(f"[MQTT] Received on '{topic}': {payload}")
        if topic == "target/base":
            parts = payload.split(";")
            self.base_target = float(parts[0])
            self.base_vel = float(parts[1])
        if topic == "target/shoulder":
            parts = payload.split(";")
            self.shoulder_target = float(parts[0])
            self.shoulder_vel = float(parts[1])
        elif topic == "target/elbow":
            parts = payload.split(";")
            self.elbow_target = float(parts[0])
            self.elbow_vel = float(parts[1])
        elif topic == "target/wrist":
            parts = payload.split(";")
            self.wrist_target = float(parts[0])
            self.wrist_vel = float(parts[1])
        elif topic == "gripper":
            if payload == "open":
                self.gripper_open = True
            else:
                self.gripper_open = False
        elif topic == "waiting_for_button":
            if payload == "true":
                self.waiting_for_button = True
            else:
                self.waiting_for_button = False

# handler = mqtt_handler()
# i = 20.0
# while True:
#     i -= 0.5
#     handler.publish("base", str(i))
#     time.sleep(0.05)
