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

        # import host
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host / IP")
        self.host_input.setText("localhost")

        # import port
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setText("1883")

        # import username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        # import PASSWORD
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # TOPIC INPUT
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Masukkan topic")

        # SUBSCRIBE BUTTON
        self.subscribe_btn = QPushButton("Subscribe Topic")
        self.unsubscribe_btn = QPushButton("Unsubscribe Topic")
        self.connect_btn = QPushButton("Connect MQTT")

        # LOG
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # MESSAGE INPUT
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ketik pesan")

        # SEND BUTTON
        self.send_btn = QPushButton("Send Message")

        layout.addWidget(self.status)
        layout.addWidget(QLabel("Host"))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel("Port"))
        layout.addWidget(self.port_input)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)

        layout.addWidget(self.connect_btn)
        layout.addWidget(QLabel("Topic"))
        layout.addWidget(self.topic_input)
        layout.addWidget(self.subscribe_btn)
        layout.addWidget(self.unsubscribe_btn)
        layout.addWidget(self.log)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_btn)

        self.setLayout(layout)

        # MQTT CLIENT
        self.client = None

        # SIGNAL
        signals.message_received.connect(self.add_log)

        # BUTTON EVENT
        self.subscribe_btn.clicked.connect(self.subscribe_topic)
        self.unsubscribe_btn.clicked.connect(self.unsubscribe_topic)
        self.send_btn.clicked.connect(self.send_message)

        # CURRENT TOPIC
        self.current_topic = ""

        # LIST TOPIC YANG SUDAH DISUBSCRIBE
        self.subscribed_topics = set()

        # CONNECT
        self.connect_btn.clicked.connect(self.connect_mqtt)
        # self.connect_mqtt()

    # =========================
    # CONNECT MQTT
    # =========================
    def connect_mqtt(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

        try:
            host = self.host_input.text().strip()
            port = int(self.port_input.text().strip())
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()

            # buat client baru
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

            # auth
            if username:
                self.client.username_pw_set(username, password)

            # callback
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message

            # connect
            self.client.connect(host, port, 60)

            # background loop
            self.client.loop_start()

            self.add_log(f"Connecting to {host}:{port}")

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

        if not self.client:
            self.add_log("Belum connect MQTT")
            return

        # cek duplicate
        if topic in self.subscribed_topics:
            self.add_log(f"Sudah subscribe: {topic}")
            return

        self.client.subscribe(topic)

        self.subscribed_topics.add(topic)

        self.current_topic = topic

        self.add_log(f"Subscribed: {topic}")

    #
    # UNSUBSCRIBE
    def unsubscribe_topic(self):
        topic = self.topic_input.text().strip()

        if not topic:
            return

        if not self.client:
            self.add_log("Belum connect MQTT")
            return

        if topic not in self.subscribed_topics:
            self.add_log(f"Belum subscribe: {topic}")
            return

        self.client.unsubscribe(topic)

        self.subscribed_topics.remove(topic)

        self.add_log(f"Unsubscribe topic: {topic}")

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

        if not self.client:
            self.add_log("Belum connect MQTT")
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
