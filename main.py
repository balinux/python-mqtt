import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from mqtt_manager import MqttManager

app = QGuiApplication(sys.argv)

engine = QQmlApplicationEngine()

mqttManager = MqttManager()

engine.rootContext().setContextProperty(
    "mqttManager",
    mqttManager,
)

engine.rootContext().setContextProperty(
    "logModel",
    mqttManager.logModel,
)

engine.load("qml/Main.qml")

if not engine.rootObjects():
    sys.exit(-1)

sys.exit(app.exec())