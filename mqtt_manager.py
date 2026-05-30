from datetime import datetime

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    Qt,
    QAbstractListModel,
    QModelIndex,
)

import paho.mqtt.client as mqtt


class LogModel(QAbstractListModel):
    MessageRole = Qt.UserRole + 1
    TypeRole = Qt.UserRole + 2
    TimeRole = Qt.UserRole + 3

    def __init__(self):
        super().__init__()
        self._logs = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._logs)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self._logs[index.row()]

        if role == self.MessageRole:
            return item["message"]

        if role == self.TypeRole:
            return item["type"]

        if role == self.TimeRole:
            return item["time"]

        return None

    def roleNames(self):
        return {
            self.MessageRole: b"message",
            self.TypeRole: b"type",
            self.TimeRole: b"time",
        }

    def addLog(self, message, log_type="info"):
        self.beginInsertRows(
            QModelIndex(),
            len(self._logs),
            len(self._logs),
        )

        self._logs.append(
            {
                "message": message,
                "type": log_type,
                "time": datetime.now().strftime("%H:%M:%S"),
            }
        )

        self.endInsertRows()


class MqttManager(QObject):
    connectionChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        self.client = None
        self.connected = False

        self.current_topic = ""
        self.subscribed_topics = set()

        self.logModel = LogModel()

    def add_log(self, message, log_type="info"):
        self.logModel.addLog(message, log_type)

    @Slot(str, int, str, str)
    def connectBroker(
        self,
        host,
        port,
        username,
        password,
    ):
        try:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2
            )

            if username:
                self.client.username_pw_set(
                    username,
                    password,
                )

            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            self.client.connect(host, port, 60)
            self.client.loop_start()

            self.add_log(
                f"Connecting to {host}:{port}",
                "info",
            )

        except Exception as e:
            self.add_log(
                f"ERROR: {e}",
                "error",
            )

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties=None,
    ):
        if reason_code == 0:
            self.connected = True

            self.connectionChanged.emit(True)

            self.add_log(
                "Connected to broker",
                "success",
            )
        else:
            self.add_log(
                f"Connection failed: {reason_code}",
                "error",
            )

    def on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties=None,
    ):
        self.connected = False

        self.connectionChanged.emit(False)

        self.add_log(
            "Disconnected",
            "error",
        )

    def on_message(
        self,
        client,
        userdata,
        msg,
    ):
        self.add_log(
            f"[{msg.topic}] {msg.payload.decode()}",
            "receive",
        )

    @Slot(str)
    def subscribeTopic(self, topic):
        if not self.connected:
            return

        self.client.subscribe(topic)

        self.subscribed_topics.add(topic)

        self.current_topic = topic

        self.add_log(
            f"Subscribed: {topic}",
            "success",
        )

    @Slot(str)
    def unsubscribeTopic(self, topic):
        if not self.connected:
            return

        self.client.unsubscribe(topic)

        self.subscribed_topics.discard(topic)

        self.add_log(
            f"Unsubscribed: {topic}",
            "info",
        )

    @Slot(str)
    def publishMessage(self, message):
        if not self.connected:
            return

        if not self.current_topic:
            return

        self.client.publish(
            self.current_topic,
            message,
        )

        self.add_log(
            f"[{self.current_topic}] {message}",
            "send",
        )