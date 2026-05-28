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

TOPIC = "kampus/suhu"


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
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ketik pesan...")

        self.send_btn = QPushButton("Send")

        layout.addWidget(self.status)
        layout.addWidget(self.log)
        layout.addWidget(self.input)
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

            self.client.subscribe(TOPIC)

            signals.message_received.emit(f"Connected to broker\nSubscribed: {TOPIC}")

        else:
            signals.message_received.emit(f"Failed: {rc}")

    def on_message(self, client, userdata, msg):
        text = msg.payload.decode()

        signals.message_received.emit(f"[{msg.topic}] : {text}")

    def send_message(self):
        text = self.input.text()

        if text:
            self.client.publish(TOPIC, text)

            self.input.clear()

    def add_log(self, text):
        self.log.append(text)


# =========================
# MAIN
# =========================
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())
