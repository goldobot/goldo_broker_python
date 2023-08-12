import struct
import pb2 as _pb2
from goldo_broker.nucleo.topics._registry import *
import nucleo_message_ids


_sym_db = _pb2._sym_db


@nucleo_out('propulsion/controller/event', nucleo_message_ids.PropulsionControllerEvent)
def controller_event(payload):
    msg = _pb2.deserialize('goldo.nucleo.propulsion.PropulsionEvent', payload[:41])
    return msg


@nucleo_in('propulsion/pose/transform', nucleo_message_ids.PropulsionTransformPose)
def transform_pose(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/set_event_sensors_mask', nucleo_message_ids.PropulsionSetEventSensorsMask)
def set_event_sensors_mask(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/acceleration_limits/set', nucleo_message_ids.PropulsionSetAccelerationLimits)
def acceleration_limits_set(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/motors/torque_limits/set', nucleo_message_ids.PropulsionMotorsTorqueLimitsSet)
def torque_limits_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/trajectory', nucleo_message_ids.PropulsionExecuteTrajectory)
def execute_trajectory(msg):
    return struct.pack('<HHfff', msg.sequence_number, 0, msg.speed, msg.reposition_distance, msg.reposition_speed) + b''.join([_pb2.serialize(p) for p in msg.points])
