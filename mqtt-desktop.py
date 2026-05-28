import sys
import paho.mqtt.client as mqtt

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QLabel,
)

from PySide6.QtCore import Signal, QObject


# =========================
# SIGNALS
# =========================
class MqttSignals(QObject):
    message_received = Signal(str)


signals = MqttSignals()


# =========================
# MQTT CONFIG
# =========================
BROKER = "localhost"
PORT = 1883

USERNAME = "4c"
PASSWORD = "123123"


# =========================
# GUI
# =========================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dynamic MQTT Topic")
        self.resize(600, 500)

        layout = QVBoxLayout()

        # STATUS
        self.status = QLabel("Disconnected")

        # TOPIC INPUT
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Masukkan topic")

        # SUBSCRIBE BUTTON
        self.subscribe_btn = QPushButton("Subscribe Topic")
        self.unsubscribe_btn = QPushButton("Unsubscribe Topic")

        # LOG
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # MESSAGE INPUT
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ketik pesan")

        # SEND BUTTON
        self.send_btn = QPushButton("Send Message")

        layout.addWidget(self.status)
        layout.addWidget(QLabel("Topic"))
        layout.addWidget(self.topic_input)
        layout.addWidget(self.subscribe_btn)
        layout.addWidget(self.unsubscribe_btn)
        layout.addWidget(self.log)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

        # MQTT CLIENT
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.client.username_pw_set(USERNAME, PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # SIGNAL
        signals.message_received.connect(self.add_log)

        # BUTTON EVENT
        self.subscribe_btn.clicked.connect(self.subscribe_topic)
        self.unsubscribe_btn.clicked.connect(self.unsubscribe_topic)
        self.send_btn.clicked.connect(self.send_message)

        # CURRENT TOPIC
        self.current_topic = ""

        # CONNECT
        self.connect_mqtt()

    # =========================
    # CONNECT MQTT
    # =========================
    def connect_mqtt(self):
        try:
            self.client.connect(BROKER, PORT, 60)
            self.client.loop_start()

        except Exception as e:
            self.add_log(f"ERROR: {e}")

    # =========================
    # ON CONNECT
    # =========================
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.status.setText("Connected")
            signals.message_received.emit("Connected to MQTT Broker")

        else:
            signals.message_received.emit(f"Failed: {rc}")

    # =========================
    # RECEIVE MESSAGE
    # =========================
    def on_message(self, client, userdata, msg):
        text = msg.payload.decode()

        signals.message_received.emit(f"[{msg.topic}] {text}")

    # =========================
    # SUBSCRIBE
    # =========================
    def subscribe_topic(self):
        topic = self.topic_input.text().strip()

        if not topic:
            return

        self.client.subscribe(topic)

        self.current_topic = topic

        self.add_log(f"Subscribed: {topic}")

    #
    # UNSUBSCRIBE
    def unsubscribe_topic(self):
        topic = self.topic_input.text().strip()

        if not topic:
            return

        self.client.unsubscribe(topic)

        self.add_log(f"unsubscribe topic: {topic}")

        # reset current topic jika sama
        if self.current_topic == topic:
            self.current_topic = ""

    # SEND MESSAGE
    # =========================
    def send_message(self):
        message = self.message_input.text().strip()

        if not message:
            return

        if not self.current_topic:
            self.add_log("Topic belum dipilih")
            return

        self.client.publish(self.current_topic, message)

        self.add_log(f"[YOU -> {self.current_topic}] {message}")

        self.message_input.clear()

    # =========================
    # LOG
    # =========================
    def add_log(self, text):
        self.log.append(text)


# =========================
# MAIN
# =========================
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
