from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion, MQTTProtocolVersion

from config import MqttConfig

from .mqtt_app import MqttApp


def create_paho_client(config: MqttConfig, app: MqttApp) -> Client:
    match config.protocol_version:
        case "3.1":
            protocol = MQTTProtocolVersion.MQTTv31

        case "3.1.1":
            protocol = MQTTProtocolVersion.MQTTv311

        case "5.0":
            protocol = MQTTProtocolVersion.MQTTv5

    client = Client(CallbackAPIVersion.VERSION2, config.client_id, protocol=protocol)
    app.change_client(client)
    app.change_topics(config.topics)

    client.on_connect = lambda *args: app.on_connect()
    client.on_connect_fail = lambda *args: app.on_connect_fail()
    client.on_disconnect = lambda *args: app.on_disconnect()

    try:
        client.username_pw_set(config.username, config.password)
        client.connect(config.host, config.port)
    except Exception:  # noqa: BLE001, S110
        pass

    return client
