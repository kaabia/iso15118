
import paho.mqtt.client as mqtt
from queue import Queue, Empty

from iso15118.secc.controller.simulator import SimEVSEController
from iso15118.secc.secc_settings import Config

import logging
logger = logging.getLogger(__name__)

MQTT_TOPIC_SIMEVSE_IND_PREFIX =  "SimEVSE/ind/"
MQTT_TOPIC_SIMEVSE_CMD_PREFIX =  "SimEVSE/cmd/"
MQTT_TOPIC_SIMEVSE_RSP_PREFIX =  "SimEVSE/rsp/"
MQTT_TOPIC_CAPL2CPP_IND_PREFIX =  "Capl2Cpp/ind/"
MQTT_TOPIC_CAPL2CPP_CMD_PREFIX =  "Capl2Cpp/cmd/"
MQTT_TOPIC_CAPL2CPP_RSP_PREFIX =  "Capl2Cpp/rsp/"

class evseDataRemoteNode:
    def __init__(self, config:Config, sim_evse_controller: SimEVSEController):

        self.config = Config
        self.evse_controller = SimEVSEController
        self.m_mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.events_secc_set = Queue()
        self.events_secc_release = Queue()
        self.hostname = "127.0.0.1"
        self.port = 1883
        self.m_mqttc.on_connect = self.on_connect
        self.m_mqttc.on_message = self.on_message
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
        logger.debug(f"[MQTT] EVSE DATA REMOTE NODE Connected to '{self.hostname}:{self.port}' with result code : \"{reason_code}\"")
        client.subscribe(MQTT_TOPIC_SIMEVSE_CMD_PREFIX + "SCC_Set/#")

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
        if str(message.topic).find("/ResponseCode") > 0:
            logger.debug("Request received : SECC_SET => ResponseCode")
            self.evse_controller.set_evse_response_code(message.payload)

        elif str(message.topic).find("/ForceStatusCode") > 0:
            logger.debug("Request received : SECC_SET => ForceStatusCode")
            self.evse_controller.set_evse_status_code(message.payload)

        elif str(message.topic).find("/NotificationMaxDelay") > 0:
            logger.debug("Request received : SECC_SET => NotificationMaxDelay")
            self.evse_controller.set_notification_max_delay(message.payload)

        elif str(message.topic).find("/EVSEProcessing") > 0:
            logger.debug("Request received : SECC_SET => EVSEProcessing")
            self.evse_controller.set_evse_processing(message.payload)

        elif str(message.topic).find("/EVSENotification") > 0:
            logger.debug("Request received : SECC_SET => EVSENotification")
            self.evse_controller.set_evse_notification(message.payload)

        elif str(message.topic).find("/MaxPower") > 0:
            logger.debug("Request received : SECC_SET => MaxPower")
            self.evse_controller.set_evse_max_power(message.payload)

        elif str(message.topic).find("/MinCurrent") > 0:
            logger.debug("Request received : SECC_SET => MinCurrent")
            self.evse_controller.set_evse_min_power(message.payload)

        elif str(message.topic).find("/MaxVoltage") > 0:
            logger.debug("Request received : SECC_SET => MaxVoltage")
            self.evse_controller.set_evse_max_voltage(message.payload)

        elif str(message.topic).find("/TargetVoltage") > 0:
            logger.debug("Request received : SECC_SET => TargetVoltage")
            self.evse_controller.set_evse_target_voltage(message.payload)

        elif str(message.topic).find("/TargetCurrent") > 0:
            logger.debug("Request received : SECC_SET => TargetCurrent")
            self.evse_controller.set_evse_target_current(message.payload)

        elif str(message.topic).find("/SCC_RequestDone") > 0:
            self.events_secc_release.put(message.payload)

    def wait_for_remote_scc_request(self, timeout_val=10) -> bool:
        while True:
            try:
                message = self.events_secc_release.get(block=True, timeout=float(timeout_val/1000.000))
                logger.debug("SCC release received")
                return True
            except Empty as exc:
                logger.debug("Timeout Exeeded: no SCC release received")
                return False
