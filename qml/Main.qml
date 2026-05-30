import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1200
    height: 700

    title: "MQTT Desktop"

    Material.theme: Material.Dark
    Material.accent: Material.Teal

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 320
            Layout.fillHeight: true

            color: "#1E1E1E"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Label {
                    text: "MQTT Broker"
                    font.pixelSize: 24
                    font.bold: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 50
                    radius: 8
                    color: "#2D2D2D"

                    Label {
                        anchors.centerIn: parent
                        text: "Disconnected"
                        color: "#ff6b6b"
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

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#404040"
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

                        onClicked: mqttManager.subscribeTopic(
                            topicInput.text
                        )
                    }

                    Button {
                        Layout.fillWidth: true
                        text: "Unsubscribe"

                        onClicked: mqttManager.unsubscribeTopic(
                            topicInput.text
                        )
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
                spacing: 15

                Label {
                    text: "Message Console"
                    font.pixelSize: 24
                    font.bold: true
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TextArea {
                        id: logArea
                        readOnly: true

                        color: "#FFFFFF"
                        font.family: "JetBrains Mono"
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 70
                    radius: 10
                    color: "#2D2D2D"

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10

                        TextField {
                            id: messageInput
                            Layout.fillWidth: true
                            placeholderText: "Write message..."
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

    Connections {
        target: mqttManager

        function onLogMessage(message) {
            logArea.text += message + "\n"
        }
    }
}