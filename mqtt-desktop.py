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


# signal bridge
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

# TOPIC = "kampus/suhu"


# =========================
# GUI
# =========================
#
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PySide6 MQTT Client")
        self.resize(500, 400)

        layout = QVBoxLayout()

        self.status = QLabel("Disconnected")

        # topic input
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Masukkan Topic")

        # subscribe button
        self.subscribe_btn = QPushButton("subscribe topic")

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ketik pesan...")

        self.send_btn = QPushButton("Send")

        layout.addWidget(self.status)
        layout.addWidget(QLabel("Topic"))
        layout.addWidget(self.topic_input)
        layout.addWidget(self.subscribe_btn)
        layout.addWidget(self.log)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

        # MQTT Setup
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.client.username_pw_set(USERNAME, PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # SIGNAL
        signals.message_received.connect(self.add_log)

        # BUTTON
        self.send_btn.clicked.connect(self.send_message)

        # BUTTON EVENT
        self.subscribe_btn.clicked.connect(self.subscribe_topic)

        # current topic
        self.current_topic = ""

        # CONNECT MQTT
        self.connect_mqtt()

    def connect_mqtt(self):
        try:
            self.client.connect(BROKER, PORT, 60)

            # MQTT loop di background thread
            self.client.loop_start()

        except Exception as e:
            self.add_log(f"ERROR: {e}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.status.setText("Connected")

            signals.message_received.emit("Connected to MQTT broker")

        else:
            signals.message_received.emit(f"Failed: {rc}")

    def on_message(self, client, userdata, msg):
        text = msg.payload.decode()

        signals.message_received.emit(f"[{msg.topic}] : {text}")

    def send_message(self):
        message = self.message_input.text().strip()

        if not message:
            return

        if not self.current_topic:
            self.add_log("Topic belum di tambah")
            return

        self.client.publish(self.current_topic, message)

        self.add_log(f"[YOU -> {self.current_topic}] {message}")
        self.message_input.clear()

    def add_log(self, text):
        self.log.append(text)

    # subscribe EVENT
    def subscribe_topic(self):
        topic = self.topic_input.text().strip()

        if not topic:
            return

        self.client.subscribe(topic)
        self.current_topic = topic
        self.add_log(f"subscribe: {topic}")


# =========================
# MAIN
# =========================
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
