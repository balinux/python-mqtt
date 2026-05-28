import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC = "sensor/suhu"
USERNAME = "4c"
PASSWORD  = "123123"

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected:", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}")
    print(f"Message: {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set(USERNAME,PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

client.loop_forever()
