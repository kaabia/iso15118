import logging
from enum import Enum, IntEnum
from typing import List, Union

logger = logging.getLogger(__name__)

# For XSD type xs:unsignedLong with value range [0..18446744073709551615]
UINT_64_MAX = 2 ** 64 - 1
# For XSD type xs:unsignedInt with value range [0..4294967296]
UINT_32_MAX = 2 ** 32 - 1
# For XSD type xs:unsignedShort with value range [0..65535]
UINT_16_MAX = 2 ** 16 - 1
# For XSD type xs:unsignedByte with value range [0..255]
UINT_8_MAX = 2 ** 8 - 1
# For XSD type xs:short with value range [-32768..32767]
INT_16_MAX = 2 ** 15 - 1
INT_16_MIN = -(2 ** 15)
# For XSD type xs:byte with value range [-128..127]
INT_8_MAX = 2 ** 7 - 1
INT_8_MIN = -(2 ** 7)


class AuthEnum(str, Enum):
    """
    The enum values for the authorisation options differ between ISO 15118-2 and
    ISO 15118-20. This enumeration helps to unify different values.

    The default value for the enum members (EIM and PNC) are the ones from
    ISO 15118-20. They are used in the session variables and evcc/secc settings.

    For the ISO 15118-2 messages (see class AuthOptions), we add enum values
    EIM_V2 and PNC_V2, which provide the specific string value used in that
    standard.
    """

    EIM = "EIM"
    PNC = "PnC"
    EIM_V2 = "ExternalPayment"
    PNC_V2 = "Contract"


class V2GTPVersion(IntEnum):
    """
    These enums are used in the header of a V2G Transfer Protocol (V2GTP)
    message, as defined in both ISO 15118-2 and ISO 15118-20
    """

    PROTOCOL_VERSION = 0x01
    INV_PROTOCOL_VERSION = 0xFE

    @classmethod
    def options(cls) -> list:
        return list(cls)


class DINPayloadTypes(IntEnum):
    """
    The following payload types are defined in
    Table 16 of DIN SPEC 70121, Section 8.7.3.1
    """

    EXI_ENCODED = 0x8001
    SDP_REQUEST = 0x9000
    SDP_RESPONSE = 0x9001
    # 0xA000 - 0xFFFF: Available for manufacturer specific use.
    # Uniqueness of those identifiers is not guaranteed.
    # All other values not mentioned are Reserved

    @classmethod
    def options(cls) -> list:
        return list(cls)


class ISOV2PayloadTypes(IntEnum):
    """
    The following payload types are defined in
    Table 10 of ISO 15118-2, Ed. 1, 2014-04-01, Section 7.8.3
    """

    EXI_ENCODED = 0x8001
    SDP_REQUEST = 0x9000
    SDP_RESPONSE = 0x9001
    # 0xA000 - 0xFFFF: Available for manufacturer specific use.
    # Uniqueness of those identifiers is not guaranteed.
    # All other values not mentioned are Reserved

    @classmethod
    def options(cls) -> list:
        return list(cls)


class ISOV20PayloadTypes(IntEnum):
    """See Table 12 of ISO 15118-20"""

    SAP = 0x8001
    MAINSTREAM = 0x8002
    AC_MAINSTREAM = 0x8003
    DC_MAINSTREAM = 0x8004
    ACDP_MAINSTREAM = 0x8005
    WPT_MAINSTREAM = 0x8006
    # 0x8007 - 0x8100: Reserved for future use
    SCHEDULE_RENEGOTIATION = 0x8101
    METERING_CONFIRMATION = 0x8102
    ACDP_SYSTEM_STATUS = 0x8103
    PARKING_STATUS = 0x8104
    # 0x8105 - 0x8FFF: Reserved for future use
    SDP_REQUEST = 0x9000
    SDP_RESPONSE = 0x9001
    SDP_REQUEST_WIRELESS = 0x9002  # Used e.g. for ACDP (ACD Pantograph)
    SDP_RESPONSE_WIRELESS = 0x9003  # Used e.g. for ACDP (ACD Pantograph)
    # 0x9004 - 0x9FFF: Reserved for future use
    # 0xA000 - 0xFFFF: Available for manufacturer specific use. Uniqueness of
    #                  those identifiers is not guaranteed.

    @classmethod
    def options(cls) -> list:
        return list(cls)


class Namespace(str, Enum):
    """
    The namespaces used in DIN SPEC 70121, ISO 15118-2, and ISO 15118-20.
    They are used for the AppProtocol entries in the SupportedAppProtocolReq
    and for the EXI codec.
    """

    DIN_MSG_DEF = "urn:din:70121:2012:MsgDef"
    DIN_MSG_BODY = "urn:din:70121:2012:MsgBody"
    DIN_MSG_DT = "urn:din:70121:2012:MsgDataTypes"
    ISO_V2_MSG_DEF = "urn:iso:15118:2:2013:MsgDef"
    ISO_V2_MSG_BODY = "urn:iso:15118:2:2013:MsgBody"
    ISO_V2_MSG_DT = "urn:iso:15118:2:2013:MsgDataTypes"
    ISO_V20_BASE = "urn:iso:std:iso:15118:-20"
    ISO_V20_COMMON_MSG = ISO_V20_BASE + ":CommonMessages"
    ISO_V20_COMMON_TYPES = ISO_V20_BASE + ":CommonTypes"
    ISO_V20_AC = ISO_V20_BASE + ":AC"
    ISO_V20_DC = ISO_V20_BASE + ":DC"
    ISO_V20_WPT = ISO_V20_BASE + ":WPT"
    ISO_V20_ACDP = ISO_V20_BASE + ":ACDP"
    XML_DSIG = "http://www.w3.org/2000/09/xmldsig#"
    SAP = "urn:iso:15118:2:2010:AppProtocol"


class Protocol(Enum):
    """
    Available communication protocols supported by Josev. The values of these
    enum members are tuples, with the first tuple entry being the namespace
    (given as a string) and the second tuple entry being the according payload
    types (given as enums).
    """

    UNKNOWN = ("", ISOV2PayloadTypes)
    DIN_SPEC_70121 = (Namespace.DIN_MSG_DEF, DINPayloadTypes)
    ISO_15118_2 = (Namespace.ISO_V2_MSG_DEF, ISOV2PayloadTypes)
    ISO_15118_20_AC = (Namespace.ISO_V20_AC, ISOV20PayloadTypes)
    ISO_15118_20_DC = (Namespace.ISO_V20_DC, ISOV20PayloadTypes)
    ISO_15118_20_WPT = (Namespace.ISO_V20_WPT, ISOV20PayloadTypes)
    ISO_15118_20_ACDP = (Namespace.ISO_V20_ACDP, ISOV20PayloadTypes)

    def __init__(
        self,
        namespace: Namespace,
        payload_types: Union[DINPayloadTypes, ISOV2PayloadTypes, ISOV20PayloadTypes],
    ):
        """
        The value of each enum member is a tuple, where the first tuple entry
        is the associated protocol namespace (ns) and the second tuple entry are
        the associated payload types, given as an enum itself.
        """
        self.namespace = namespace
        self.payload_types = payload_types

    @property
    def ns(self) -> Namespace:
        return self.namespace

    @property
    def payloads(self) -> Union[DINPayloadTypes, ISOV2PayloadTypes, ISOV20PayloadTypes]:
        return self.payload_types

    @classmethod
    def options(cls) -> list:
        return list(cls)

    @classmethod
    def names(cls) -> list:
        return [protocol.name for protocol in cls]

    @classmethod
    def allowed_protocols(cls) -> list:
        return [
            protocol.name
            for protocol in cls
            if protocol.name not in ["UNKNOWN", "ISO_15118_20"]
        ]

    @classmethod
    def get_by_ns(cls, namespace: str) -> "Protocol":
        """Retrieves a Protocol entry by namespace"""
        for protocol in cls.options():
            if protocol.ns == namespace:
                return protocol

        logger.error(f"No available protocol matching namespace '{namespace}'")
        return Protocol.UNKNOWN

    def __str__(self):
        return str(self.name)

    @classmethod
    def v20_namespaces(cls) -> List[str]:
        return [
            protocol.namespace
            for protocol in cls
            if "urn:iso:std:iso:15118:-20" in protocol.namespace
        ]


class ServiceV20(Enum):
    """
    Available services in ISO 15118-20. The values of these enum members are tuples,
    with the first tuple entry being the service ID (given as an int) and the second
    tuple entry being the according service name (given as string).

    See Table 204 in section 8.4.3.1 of ISO 15118-20
    """

    AC = (1, "AC")
    DC = (2, "DC")
    WPT = (3, "WPT")
    DC_ACDP = (4, "DC_ACDP")
    AC_BPT = (5, "AC_BPT")
    DC_BPT = (6, "DC_BPT")
    DC_ACDP_BPT = (7, "DC_ACDP_BPT")
    INTERNET = (65, "Internet")
    PARKING_STATUS = (66, "ParkingStatus")

    def __init__(
        self,
        service_id: int,
        service_name: str,
    ):
        """
        The value of each enum member is a tuple, where the first tuple entry
        is the associated protocol namespace (ns) and the second tuple entry are
        the associated payload types, given as an enum itself.
        """
        self.service_id = service_id
        self.service_name = service_name

    @classmethod
    def get_by_id(cls, service_id: int) -> "ServiceV20":
        """
        Returns the ServiceV20 enum member given a service ID.

        Raises:
            ValueError if an invalid service ID is provided.
        """
        if service_id == 1:
            return cls.AC
        elif service_id == 2:
            return cls.DC
        elif service_id == 3:
            return cls.WPT
        elif service_id == 4:
            return cls.DC_ACDP
        elif service_id == 5:
            return cls.AC_BPT
        elif service_id == 6:
            return cls.DC_BPT
        elif service_id == 7:
            return cls.DC_ACDP_BPT
        elif service_id == 65:
            return cls.INTERNET
        elif service_id == 66:
            return cls.PARKING_STATUS
        else:
            raise ValueError(f"Invalid service ID {service_id}")

    @property
    def id(self) -> int:
        return self.service_id

    @property
    def name(self) -> str:
        return self.service_name


class ParameterName(str, Enum):
    CONNECTOR = "Connector"
    CONTROL_MODE = "ControlMode"
    EVSE_NOMINAL_VOLTAGE = "EVSENominalVoltage"
    MOBILITY_NEEDS_MODE = "MobilityNeedsMode"
    PRICING = "Pricing"
    BPT_CHANNEL = "BPTChannel"
    GENERATOR_MODE = "GeneratorMode"
    GRID_CODE_ISLANDING_DETECTION_MODE = "GridCodeIslandingDetectionMethod"


class ACConnector(IntEnum):
    """See Table 205 in section 8.4.3.2.2 of ISO 15118-20"""

    SINGLE_PHASE = 1
    THREE_PHASE = 2


class DCConnector(IntEnum):
    """See Table 207 in section 8.4.3.2.3 of ISO 15118-20"""

    CORE = 1
    EXTENDED = 2
    DUAL2 = 3
    DUAL4 = 4


class ControlMode(IntEnum):
    """See e.g. Table 205 in section 8.4.3.2.2 of ISO 15118-20"""

    SCHEDULED = 1
    DYNAMIC = 2


class MobilityNeedsMode(IntEnum):
    """See e.g. Table 205 in section 8.4.3.2.2 of ISO 15118-20"""

    EVCC_ONLY = 1
    EVCC_AND_SECC = 2


class Pricing(IntEnum):
    """See e.g. Table 205 in section 8.4.3.2.2 of ISO 15118-20"""

    NONE = 0
    ABSOLUTE = 1
    LEVELS = 2


class BPTChannel(IntEnum):
    """See e.g. Table 206 in section 8.4.3.2.2.1 of ISO 15118-20"""

    UNIFIED = 1
    SEPARATED = 2


class GeneratorMode(IntEnum):
    """See e.g. Table 206 in section 8.4.3.2.2.1 of ISO 15118-20"""

    GRID_FOLLOWING = 1
    GRID_FORMING = 2


class GridCodeIslandingDetectionMode(IntEnum):
    """See e.g. Table 206 in section 8.4.3.2.2.1 of ISO 15118-20"""

    ACTIVE = 1
    PASSIVE = 2


class PriceAlgorithm(str, Enum):
    POWER = "urn:iso:std:iso:15118:-20:PriceAlgorithm:1-Power"
    PEAK_POWER = "urn:iso:std:iso:15118:-20:PriceAlgorithm:2-PeakPower"
    STACKED_POWER = "urn:iso:std:iso:15118:-20:PriceAlgorithm:3-StackedEnergy"


class Contactor(IntEnum):
    OPENED = 1
    CLOSED = 2


class SignatureMethod(str, Enum):
    SHA_256 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"
    SHA_512 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha512"
    ED448 = "urn:iso:std:iso:15118:-20:Security:xmldsig#Ed448"


class DigestMethod(str, Enum):
    SHA_256 = "http://www.w3.org/2001/04/xmlenc#sha256"
    SHA_512 = "http://www.w3.org/2001/04/xmlenc#sha512"
    SHAKE_256 = "urn:iso:std:iso:15118:-20:Security:xmlenc#SHAKE256"
