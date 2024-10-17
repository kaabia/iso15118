
import paho.mqtt.client as mqtt
from queue import Queue, Empty
import logging

from iso15118.secc.controller.simulator import SimEVSEController
from iso15118.secc.secc_settings import Config
from iso15118.shared.messages.iso15118_2.body import ResponseCode as ResponseCodeV2
from iso15118.shared.messages.datatypes import (
    DCEVSEChargeParameter,
    DCEVSEStatus,
    DCEVSEStatusCode)
from iso15118.shared.messages.enums import (
    AuthEnum,
    AuthorizationStatus,
    AuthorizationTokenType,
    CpState,
    DCEVErrorCode,
    EVSEProcessing,
    IsolationLevel,
    Namespace,
    Protocol,
    SessionStopAction,
)

from iso15118.shared.messages.datatypes import EVSENotification as EVSENotificationV2
from iso15118.shared.settings import SettingKey, shared_settings

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
        self.evse_controller = sim_evse_controller
        self.m_mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.events_secc_set = Queue()
        self.events_secc_release = Queue()
        self.hostname = shared_settings[SettingKey.MQTT_HOST_NAME]
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
            self.evse_controller.set_evse_response_code(self, ResponseCodeV2(message.payload.decode("utf-8")))
        elif str(message.topic).find("/ForceStatusCode") > 0:
            self.evse_controller.set_evse_status_code(self, DCEVSEStatusCode(message.payload.decode("utf-8")))
        elif str(message.topic).find("/NotificationMaxDelay") > 0:
            self.evse_controller.set_notification_max_delay(self, float(message.payload.decode("utf-8")))
        elif str(message.topic).find("/EVSEProcessing") > 0:
            self.evse_controller.set_evse_processing(self, EVSEProcessing(message.payload.decode("utf-8")))
        # NOT YET TESTED 
        elif str(message.topic).find("/EVSENotification") > 0:            
            #self.evse_controller.set_evse_notification(self, EVSENotificationV2(message.payload.decode("utf-8")))
            self.evse_controller.evse_notification = EVSENotificationV2.RE_NEGOTIATION
        elif str(message.topic).find("/MaxPower") > 0:
            self.evse_controller.evse_data_context.session_limits.dc_limits.max_charge_power = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/MaxCurrent") > 0:
            self.evse_controller.evse_data_context.session_limits.dc_limits.max_charge_current = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/MaxVoltage") > 0:
            self.evse_controller.evse_data_context.session_limits.dc_limits.max_voltage = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/MinCurrent") > 0:
            self.evse_controller.evse_data_context.session_limits.dc_limits.min_current = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/MinVoltage") > 0:
            self.evse_controller.evse_data_context.session_limits.dc_limits.min_voltage = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/PeakCurrentRipple") > 0:
            self.evse_controller.evse_data_context.peak_current_ripple = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/PresentVoltage") > 0:
            self.evse_controller.evse_data_context.present_voltage = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/PresentCurrent") > 0:
            self.evse_controller.evse_data_context.present_current = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/NominalVoltage") > 0:
            self.evse_controller.evse_data_context.nominal_voltage = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/CurrentRegulationTolerance") > 0:
            self.evse_controller.evse_data_context.current_regulation_tolerance = float(message.payload.decode("utf-8"))
        elif str(message.topic).find("/TargetVoltage") > 0:
            pass
        elif str(message.topic).find("/TargetCurrent") > 0:
            pass
        # TESTED OK
        elif str(message.topic).find("/SCC_RequestDone") > 0:
            self.events_secc_release.put(message.payload)

    def wait_for_remote_scc_request(self, timeout_val=10) -> bool:
        while True:
            try:
                self.events_secc_release.get(block=True, timeout=float(timeout_val))
                return True
            except Empty as exc:
                return False
