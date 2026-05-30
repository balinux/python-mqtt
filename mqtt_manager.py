from PySide6.QtCore import QObject, Signal, Slot
import paho.mqtt.client as mqtt


class MqttManager(QObject):
    logMessage = Signal(str)
    connectionChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        self.client = None
        self.current_topic = ""
        self.subscribed_topics = set()

    @Slot(str, int, str, str)
    def connectBroker(self, host, port, username, password):

        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

            if username:
                self.client.username_pw_set(username, password)

            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message

            self.client.connect(host, port, 60)

            self.client.loop_start()

            self.logMessage.emit(f"Connecting to {host}:{port}")

        except Exception as e:
            self.logMessage.emit(f"ERROR: {e}")

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties=None,
    ):
        if reason_code == 0:
            self.connectionChanged.emit(True)
            self.logMessage.emit("Connected")
        else:
            self.connectionChanged.emit(False)
            self.logMessage.emit(f"Failed: {reason_code}")

    def on_message(self, client, userdata, msg):
        self.logMessage.emit(f"[{msg.topic}] {msg.payload.decode()}")

    @Slot(str)
    def subscribeTopic(self, topic):

        if not self.client:
            return

        self.client.subscribe(topic)

        self.subscribed_topics.add(topic)
        self.current_topic = topic

        self.logMessage.emit(f"Subscribed: {topic}")

    @Slot(str)
    def unsubscribeTopic(self, topic):

        if not self.client:
            return

        self.client.unsubscribe(topic)

        self.subscribed_topics.discard(topic)

        self.logMessage.emit(f"Unsubscribe: {topic}")

    @Slot(str)
    def publishMessage(self, message):

        if not self.client:
            return

        if not self.current_topic:
            return

        self.client.publish(self.current_topic, message)

        self.logMessage.emit(f"[YOU] {message}")
