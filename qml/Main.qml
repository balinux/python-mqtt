import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1200
    height: 720

    title: "MQTT Desktop"

    Material.theme: Material.Dark
    Material.accent: Material.Teal

    property bool connected: false

    Connections {
        target: mqttManager

        function onConnectionChanged(state) {
            connected = state
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 320
            Layout.fillHeight: true
            color: "#1b1b1b"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20

                Label {
                    text: "MQTT Desktop"
                    font.pixelSize: 24
                    font.bold: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 60
                    radius: 12

                    color: connected
                        ? "#133b24"
                        : "#4d1f1f"

                    Row {
                        anchors.centerIn: parent
                        spacing: 10

                        Rectangle {
                            width: 12
                            height: 12
                            radius: 6

                            color: connected
                                ? "#00ff66"
                                : "#ff4444"
                        }

                        Label {
                            text: connected
                                ? "Connected"
                                : "Disconnected"
                        }
                    }
                }

                TextField {
                    id: hostInput
                    Layout.fillWidth: true
                    text: "localhost"
                    placeholderText: "Host"
                }

                TextField {
                    id: portInput
                    Layout.fillWidth: true
                    text: "1883"
                    placeholderText: "Port"
                }

                TextField {
                    id: usernameInput
                    Layout.fillWidth: true
                    placeholderText: "Username"
                }

                TextField {
                    id: passwordInput
                    Layout.fillWidth: true
                    placeholderText: "Password"
                    echoMode: TextInput.Password
                }

                Button {
                    Layout.fillWidth: true
                    text: "Connect"

                    onClicked: {
                        mqttManager.connectBroker(
                            hostInput.text,
                            Number(portInput.text),
                            usernameInput.text,
                            passwordInput.text
                        )
                    }
                }

                Label {
                    text: "Topic"
                    font.bold: true
                }

                TextField {
                    id: topicInput
                    Layout.fillWidth: true
                    placeholderText: "sensor/temp"
                }

                RowLayout {
                    Layout.fillWidth: true

                    Button {
                        Layout.fillWidth: true
                        text: "Subscribe"

                        onClicked: {
                            mqttManager.subscribeTopic(
                                topicInput.text
                            )
                        }
                    }

                    Button {
                        Layout.fillWidth: true
                        text: "Unsubscribe"

                        onClicked: {
                            mqttManager.unsubscribeTopic(
                                topicInput.text
                            )
                        }
                    }
                }

                Item {
                    Layout.fillHeight: true
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true

            color: "#252526"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20

                Label {
                    text: "Messages"
                    font.pixelSize: 22
                    font.bold: true
                }

                ListView {
                    id: logView

                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    model: logModel

                    spacing: 10

              delegate: Item {

    width: logView.width
    height: bubble.height + 10

    Rectangle {
        id: bubble

        anchors.left: parent.left
        anchors.leftMargin: 10

        width: Math.min(
            parent.width * 0.8,
            textItem.implicitWidth + 40
        )

        height: contentColumn.implicitHeight + 20

        radius: 12

        color: {
            if(type === "send")
                return "#005C97"

            if(type === "receive")
                return "#2E2E2E"

            if(type === "success")
                return "#0E6B3F"

            if(type === "error")
                return "#7A2424"

            return "#333333"
        }

        Column {
            id: contentColumn

            anchors.fill: parent
            anchors.margins: 10

            spacing: 4

            Label {
                text: time
                font.pixelSize: 10
                opacity: 0.6
            }

            Text {
                id: textItem

                text: message

                color: "white"

                wrapMode: Text.WordWrap

                width: bubble.width - 20
            }
        }
    }
}
                    onCountChanged: {
                        positionViewAtEnd()
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 70
                    radius: 12
                    color: "#2d2d2d"

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10

                        TextField {
                            id: messageInput
                            Layout.fillWidth: true

                            placeholderText:
                                "Type message..."

                            onAccepted: {
                                mqttManager.publishMessage(
                                    text
                                )

                                clear()
                            }
                        }

                        Button {
                            text: "Send"

                            onClicked: {
                                mqttManager.publishMessage(
                                    messageInput.text
                                )

                                messageInput.clear()
                            }
                        }
                    }
                }
            }
        }
    }
}