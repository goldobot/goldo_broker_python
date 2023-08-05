import struct
import pb2 as _pb2
from goldo_broker.nucleo.topics._registry import *


_sym_db = _pb2._sym_db


@nucleo_out('propulsion/controller/event', 131)
def controller_event(payload):
    msg = _pb2.deserialize('goldo.nucleo.propulsion.PropulsionEvent', payload[:41])
    return msg


@nucleo_in('propulsion/pose/transform', 113)
def transform_pose(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/set_event_sensors_mask', 114)
def set_event_sensors_mask(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/acceleration_limits/set', 104)
def acceleration_limits_set(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/motors/torque_limits/set', 112)
def torque_limits_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/trajectory', 145)
def execute_trajectory(msg):
    return struct.pack('<HHfff', msg.sequence_number, 0, msg.speed, msg.reposition_distance, msg.reposition_speed) + b''.join([_pb2.serialize(p) for p in msg.points])
