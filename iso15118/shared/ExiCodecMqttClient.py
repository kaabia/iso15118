"""
Module: ExiCodecMqttClient

This module provides an MQTT client for encoding and decoding EXI messages.
The ExiCodecMqttClient class allows you to connect to an MQTT broker, subscribe
to topics, and publish messages for encoding and decoding EXI data.

The class uses the Paho MQTT Python client library and provides methods for
encoding and decoding EXI messages using a separate EXI codec server.

Example usage:

    client = ExiCodecMqttClient()
    encoded_message = client.encode("[V2G_Message...]", "urn:iso:15118:2:2013:MsgDef")
    decoded_message = client.decode("8098023c2d5764f7601f87d151000600",
                                    "urn:iso:15118:2:2013:MsgDef")

"""

import json
import uuid
import time
import logging
from queue import Queue, Empty
import paho.mqtt.client as mqtt

EXI_CODED_MQTT_SERVER_CMD_TOPIC = "ExiCodedMqttServer/cmd/"
EXI_CODED_MQTT_SERVER_RSP_TOPIC = "ExiCodedMqttServer/rsp/"

logger = logging.getLogger(__name__)

class ExiCodecMqttClient():
    """
    A class that represents an MQTT client for encoding and decoding EXI messages.
    """
    def __init__(self, hostname="127.0.0.1") -> None:
        """
        Initializes the ExiCodecMqttClient instance.
        """
        super().__init__()
        self.m_mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.events_rsp = Queue()
        self.hostname = hostname
        self.port = 1883
        self.m_mqttc.on_connect = self.on_connect
        self.m_mqttc.on_message = self.on_message
        self.m_mqttc.on_subscribe = self.on_subscribe
        self.m_mqttc.connect(self.hostname, self.port)

        self.m_mqttc.loop_start()

    def on_connect(self, client:mqtt.Client, _userdata, _flags, reason_code, _properties):
        """
        Callback function called when the MQTT client connects to the broker.

        Args:
            client (mqtt.Client): The MQTT client instance.
            _userdata (Any): User data (unused).
            _flags (dict): Response flags sent by the broker (unused).
            reason_code (int): The reason code for the connection.
            _properties (Properties): The properties sent by the broker (unused).
        """
        logger.debug(f"[MQTT] Connected to '{self.hostname}:{self.port}' with result code : \"{reason_code}\"")
        client.subscribe(EXI_CODED_MQTT_SERVER_RSP_TOPIC + "#")

    def on_message(self, _client, _userdata, message) -> dict :
        """
        Callback function called when a message is received from the broker.

        Args:
            _client (mqtt.Client): The MQTT client instance (unused).
            _userdata (Any): User data (unused).
            message (MQTTMessage): The received message.

        Returns:
            dict: A dictionary containing the message payload.
        """
        if str(message.topic).find("/decode") > 0:
            self.events_rsp.put(message.payload)
        elif str(message.topic).find("/encode") > 0:
            self.events_rsp.put(message.payload)

    def on_subscribe(self, _client, _userdata, _mid, reason_code_list, _properties):
        """
        Callback function called when the broker responds to a subscription request.

        Args:
            _client (mqtt.Client): The MQTT client instance (unused).
            _userdata (Any): User data (unused).
            _mid (int): The message ID of the subscription request (unused).
            reason_code_list (list): A list of reason codes for the subscription.
            _properties (Properties): The properties sent by the broker (unused).
        """
        if reason_code_list[0].is_failure:
            logger.debug(f"[MQTT] Broker rejected you subscription: {reason_code_list[0]}")
        else:
            logger.debug(f"[MQTT] Subscrition done with granted QoS: {reason_code_list[0].value}")

    def encode(self, message: str, ns: str) -> bytes:
        """
        Encodes the given message using the EXI codec.

        Args:
            message (str): The message to be encoded.
            ns (str): The namespace for the EXI codec.

        Returns:
            bytes: The encoded message as bytes, or None if no response is received.
        """
        identifier = str(uuid.uuid4())
        logger.debug(f"[MQTT] Request encoding : reqID=<{identifier}>")
        request = str(json.dumps({"id" : identifier, "v2g": message, "ns": ns}))
        self.m_mqttc.publish(EXI_CODED_MQTT_SERVER_CMD_TOPIC + "/encode", request)
        while True:
            try:
                message = self.events_rsp.get(block=True, timeout=2)
                response = json.loads(message.decode())
                if 'id' in response and response['id'] == identifier:
                    if "exi" in response:
                        logger.debug(f"[MQTT] Encoding response received : reqID=<{response['id']}>")
                        return bytes.fromhex(response["exi"])
            except Empty as exc:
                raise Exception('No response received within 2 seconds') from exc

    def decode(self, message: bytes, ns: str):
        """
        Decodes the given message using the EXI codec.

        Args:
            message (bytes): The message to be decoded.
            ns (str): The namespace for the EXI codec.

        Returns:
            str: The decoded message as a string, or None if no response is received.
        """
        identifier = str(uuid.uuid4())
        logger.debug(f"[MQTT] Request decoding : reqID=<{identifier}>")
        request = str(json.dumps({'id' : identifier, 'exi': message.hex(), 'ns': ns}))
        self.m_mqttc.publish(EXI_CODED_MQTT_SERVER_CMD_TOPIC + "/decode", request)
        while True:
            try:
                message = self.events_rsp.get(block=True, timeout=2)
                response = json.loads(message.decode())
                if 'id' in response and response['id'] == identifier:
                    if "v2g" in response:
                        logger.debug(f"[MQTT] Decoding response received : reqID=<{response['id']}>")
                        return str(response["v2g"])
            except Empty as exc:
                raise Exception('No response received within 2 seconds') from exc

    def get_version(self) -> str:
        return "1.0.0"

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s    %(asctime)s - %(name)s (%(lineno)d): %(message)s', level=logging.DEBUG)
    exiClient = ExiCodecMqttClient("test.mosquitto.org")
    time.sleep(0.5)

    EXI_BYTES = "8098023c2d5764f7601f87d151000600"
    NS = "urn:iso:15118:2:2013:MsgDef"
    print(f"Decode : exi = {EXI_BYTES}, ns = {NS}")
    decoded_exi = exiClient.decode(bytes.fromhex(EXI_BYTES), NS)
    print(f"Decoded message = {decoded_exi}")
    print(f"Encode : {decoded_exi}")
    encoded_exi = exiClient.encode(decoded_exi, NS)
    print(f"Encoded message = \"{encoded_exi.hex()}\"")
