import nucleo_message_ids
import pb2 as _pb2
import struct

from goldo_broker.nucleo.topics._registry import *

_sym_db = _pb2._sym_db

import logging

LOGGER = logging.getLogger(__name__)


@nucleo_out('servo/ack', nucleo_message_ids.ServoAck)
def servo_ack(payload):
    return _sym_db.GetSymbol('google.protobuf.UInt32Value')(value=struct.unpack('<H', payload)[0])


@nucleo_in('servo/disable_all', nucleo_message_ids.ServoDisableAll)
def servo_disable_all(msg):
    return _pb2.serialize(msg)


@nucleo_in('servo/enable/set', nucleo_message_ids.ServoSetEnable)
def servo_set_enable(msg):
    return struct.pack('<H', msg.sequence_number) + b''.join([_pb2.serialize(enable) for enable in msg.enables])


@nucleo_in('servo/set_max_torques', nucleo_message_ids.ServoSetMaxTorques)
def servo_set_max_torques(msg):
    return struct.pack('<H', msg.sequence_number) + b''.join([_pb2.serialize(torque) for torque in msg.torques])


@nucleo_in('servo/move_multiple', nucleo_message_ids.ServoMoveMultiple)
def servo_move_multiple(msg):
    return struct.pack('<HH', msg.sequence_number, msg.speed) + b''.join([_pb2.serialize(pos) for pos in msg.positions])

@nucleo_in('lift/set_enable', nucleo_message_ids.LiftSetEnable)
def lift_set_enable(msg):
    return _pb2.serialize(msg)

@nucleo_in('lift/do_homing', nucleo_message_ids.LiftDoHoming)
def lift_do_homing(msg):
    return _pb2.serialize(msg)
    
@nucleo_out('lift/homing_done', nucleo_message_ids.LiftHomingDone)
def lift_homing_done(payload):
    lift_id = struct.unpack('<B', payload)[0]
    msg = _sym_db.GetSymbol('google.protobuf.UInt32Value')(value=lift_id)
    LOGGER.debug('lift homing done, id', lift_id)
    return msg
    
@nucleo_in('lift/cmd_raw', nucleo_message_ids.LiftsCmdRaw)
def lift_do_cmd_raw(msg):
    return _pb2.serialize(msg)

@nucleo_out('servo/status/states', nucleo_message_ids.ServoState)
def servo_status_states(payload):
    num_servos = (len(payload) - 6) // 6
    header = struct.unpack('IBB', payload[0:6])
    states = [_pb2.deserialize('goldo.nucleo.servos.ServoState', payload[(6 + i * 6):(6 + 6 * (i + 1))]) for i in
              range(num_servos)]
    msg = _sym_db.GetSymbol('goldo.nucleo.servos.ServoStates')(
        timestamp=header[0],
        servos=states)
    return msg


@nucleo_out('servo/status/moving', nucleo_message_ids.ServosMoving)
def servo_status_moving(payload):
    msg = _sym_db.GetSymbol('google.protobuf.UInt32Value')(value=struct.unpack('<I', payload)[0])
    return msg
