from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class ACCLLimits:
    # Optional in both Scheduled and Dynamic CL (both AC CL and BPT AC CL)
    evse_target_active_power: Optional[float] = None  # Required in Dynamic AC CL
    evse_target_active_power_l2: Optional[float] = None
    evse_target_active_power_l3: Optional[float] = None
    evse_target_reactive_power: Optional[float] = None
    evse_target_reactive_power_l2: Optional[float] = None
    evse_target_reactive_power_l3: Optional[float] = None
    evse_present_active_power: Optional[float] = None  # Optional in AC CPD
    evse_present_active_power_l2: Optional[float] = None  # Optional in AC CPD
    evse_present_active_power_l3: Optional[float] = None  # Optional in AC CPD


@dataclass
class ACLimits:
    # 15118-2 AC CPD
    evse_nominal_voltage: Optional[float] = None  # Also required for 15118-20 CPD
    evse_max_current: Optional[float] = None  # Required

    # 15118-20 AC CPD (Required)
    evse_max_charge_power: Optional[float] = None
    evse_min_charge_power: Optional[float] = None

    # 15118-20 AC CPD (Optional)
    evse_max_charge_power_l2: Optional[float] = None
    evse_max_charge_power_l3: Optional[float] = None
    evse_min_charge_power_l2: Optional[float] = None
    evse_min_charge_power_l3: Optional[float] = None
    evse_nominal_frequency: Optional[float] = None
    max_power_asymmetry: Optional[float] = None
    evse_power_ramp_limit: Optional[float] = None

    evse_present_active_power: Optional[float] = None  # Optional in AC Scheduled CL
    evse_present_active_power_l2: Optional[float] = None  # Optional in AC Scheduled CL
    evse_present_active_power_l3: Optional[float] = None  # Optional in AC Scheduled CL

    # 15118-20 BPT CPD (Required)
    evse_max_discharge_power: Optional[float] = None
    evse_min_discharge_power: Optional[float] = None

    # 15118-20 BPT CPD (Optional)
    evse_max_discharge_power_l2: Optional[float] = None
    evse_max_discharge_power_l3: Optional[float] = None
    evse_min_discharge_power_l2: Optional[float] = None
    evse_min_discharge_power_l3: Optional[float] = None

    # TODO REMOVE - CL PARAMS HAVE BEEN MOVED TO A DIFFERENT STRUCT.
    # EVSE -20 AC CL (Optional)
    evse_target_active_power: Optional[float] = None
    evse_target_active_power_l2: Optional[float] = None
    evse_target_active_power_l3: Optional[float] = None
    evse_target_reactive_power: Optional[float] = None
    evse_target_reactive_power_l2: Optional[float] = None
    evse_target_reactive_power_l3: Optional[float] = None

    def update(
        self,
        params: dict,
    ):
        evse_params = {}
        for k, v in params.items():
            if type(v) is dict:
                evse_params.update({k: v["value"] * 10 ** v["exponent"]})
            elif type(v) in [int, float]:
                evse_params.update({k: v})

        self.__dict__.update(evse_params)

    def as_dict(self):
        return self.__dict__


@dataclass
class DCCLLimits:
    # Optional in 15118-20 DC CL (Scheduled)
    evse_max_charge_power: Optional[float] = None  # Required in 15118-20 Dynamic CL
    evse_min_charge_power: Optional[float] = None  # Required in 15118-20 Dynamic CL
    evse_max_charge_current: Optional[float] = None  # Required in 15118-20 Dynamic CL
    evse_max_voltage: Optional[float] = None  # Required in 15118-20 Dynamic CL

    # Optional and present in 15118-20 DC BPT CL (Scheduled)
    evse_max_discharge_power: Optional[float] = None  # Req in 15118-20 Dynamic BPT CL
    evse_min_discharge_power: Optional[float] = None  # Req in 15118-20 Dynamic BPT CL
    evse_max_discharge_current: Optional[float] = None  # Req in 15118-20 Dynamic BPT CL
    evse_min_voltage: Optional[float] = None  # Required in 15118-20 Dynamic BPT CL


@dataclass
class DCLimits:
    # Required in 15118-20 DC CPD
    evse_max_charge_power: Optional[float] = None  # Required for -2 DC, DIN CPD
    evse_min_charge_power: Optional[float] = None  # Required for -2 DC, DIN CPD
    evse_max_charge_current: Optional[float] = None  # Required for -2 DC, DIN CPD
    evse_min_charge_current: Optional[float] = None  # Required for -2 DC, DIN CPD
    evse_max_voltage: Optional[float] = None  # Required for -2 DC, DIN CPD
    evse_min_voltage: Optional[float] = None  # Required for -2 DC, DIN CPD

    #  Optional in 15118-20 DC CPD
    evse_power_ramp_limit: Optional[float] = None

    # Required in 15118-20 DC BPT CPD
    evse_max_discharge_power: Optional[float] = None
    evse_min_discharge_power: Optional[float] = None
    evse_max_discharge_current: Optional[float] = None
    evse_min_discharge_current: Optional[float] = None

    #  Optional in 15118-2 CPD
    evse_current_regulation_tolerance: Optional[float] = None
    evse_peak_current_ripple: Optional[float] = None
    evse_energy_to_be_delivered: Optional[float] = None

    # TODO REQUIRED FOR -2, DIN. Required params present in DCCLLimits.
    #  To be tested and removed.
    # 15118-2 DC, DINSPEC
    evse_maximum_current_limit: Optional[float] = None
    evse_maximum_power_limit: Optional[float] = None
    evse_maximum_voltage_limit: Optional[float] = None
    evse_minimum_current_limit: Optional[float] = None
    evse_minimum_voltage_limit: Optional[float] = None

    def update(
        self,
        params: dict,
    ):
        evse_params = {}
        for k, v in params.items():
            if type(v) is dict:
                evse_params.update({k: v["value"] * 10 ** v["exponent"]})
            elif type(v) in [int, float]:
                evse_params.update({k: v})

        self.__dict__.update(evse_params)

    def as_dict(self):
        return self.__dict__


@dataclass
class EVSERatedLimits:
    ac_limits: Optional[ACLimits] = None
    dc_limits: Optional[DCLimits] = None


@dataclass
class EVSESessionContext:
    # Optional in -20 Dynamic CL Res
    departure_time: Optional[int] = None
    min_soc: Optional[int] = None
    target_soc: Optional[int] = None
    ack_max_delay: Optional[int] = None

    # Required for -2 DC CurrentDemand, -20 DC CL
    evse_present_current: Union[float, int] = 0
    evse_present_voltage: Union[float, int] = 0

    ac_limits: Optional[ACCLLimits] = None
    dc_limits: Optional[DCCLLimits] = None


@dataclass
class EVSEDataContext:
    rated_limits: Optional[EVSERatedLimits] = None
    session_context: Optional[EVSESessionContext] = None


# @dataclass
# class EVSEDataContext_:
#     departure_time: Optional[int] = None
#     min_soc: Optional[int] = None
#     target_soc: Optional[int] = None
#     ack_max_delay: Optional[int] = None
#     evse_present_voltage: Union[float, int] = 0
#     evse_present_current: Union[float, int] = 0
#     # EVSE -20 DC
#     evse_max_charge_power: Optional[float] = None  # Also in -20 AC
#     evse_min_charge_power: Optional[float] = None  # Also in -20 AC
#     evse_max_charge_current: Optional[float] = None
#     evse_min_charge_current: Optional[float] = None
#     evse_max_voltage: Optional[float] = None
#     evse_min_voltage: Optional[float] = None
#     evse_power_ramp_limit: Optional[float] = None  # Also in -20 AC
#
#     # EVSE -20 AC and DC BPT
#     evse_max_discharge_power: Optional[float] = None
#     evse_min_discharge_power: Optional[float] = None
#     evse_max_discharge_current: Optional[float] = None
#     evse_min_discharge_current: Optional[float] = None
#
#     # EVSE -20 AC
#     evse_max_charge_power_l2: Optional[float] = None
#     evse_max_charge_power_l3: Optional[float] = None
#     evse_min_charge_power_l2: Optional[float] = None
#     evse_min_charge_power_l3: Optional[float] = None
#     evse_nominal_frequency: Optional[float] = None
#     max_power_asymmetry: Optional[float] = None
#     evse_present_active_power: Optional[float] = None
#     evse_present_active_power_l2: Optional[float] = None
#     evse_present_active_power_l3: Optional[float] = None
#
#     # EVSE -20 AC BPT
#     evse_max_discharge_power_l2: Optional[float] = None
#     evse_max_discharge_power_l3: Optional[float] = None
#     evse_min_discharge_power_l2: Optional[float] = None
#     evse_min_discharge_power_l3: Optional[float] = None
#
#     # EVSE -20 AC CL
#     evse_target_active_power: Optional[float] = None
#     evse_target_active_power_l2: Optional[float] = None
#     evse_target_active_power_l3: Optional[float] = None
#     evse_target_reactive_power: Optional[float] = None
#     evse_target_reactive_power_l2: Optional[float] = None
#     evse_target_reactive_power_l3: Optional[float] = None
#
#     def update(
#         self,
#         params: dict,
#     ):
#         evse_params = {}
#         for k, v in params.items():
#             if type(v) is dict:
#                 evse_params.update({k: v["value"] * 10 ** v["exponent"]})
#             elif type(v) in [int, float]:
#                 evse_params.update({k: v})
#
#         self.__dict__.update(evse_params)
#
#     def as_dict(self):
#         return self.__dict__