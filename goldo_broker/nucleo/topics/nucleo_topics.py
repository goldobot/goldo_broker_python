from goldo_broker.nucleo.topics._registry import *
import pb2 as _pb2
import struct
import math
import nucleo_message_ids

_sym_db = _pb2._sym_db

#_in = {}
#_out = {}

_msg_BytesValue = _sym_db.GetSymbol('google.protobuf.BytesValue')
_msg_propulsion_Telemetry =  _sym_db.GetSymbol('goldo.nucleo.propulsion.Telemetry')
_unpack_propulsion_Telemetry = struct.Struct('<hhhhhhhHHbbBB').unpack

_msg_propulsion_TelemetryEx =  _sym_db.GetSymbol('goldo.nucleo.propulsion.TelemetryEx')
_unpack_propulsion_TelemetryEx = struct.Struct('<hhhhhhhhhhhh').unpack

_unpack_heartbeat = struct.Struct('<I').unpack



@nucleo_out('os/heartbeat', nucleo_message_ids.Heartbeat)
def heartbeat(payload):
    msg = _sym_db.GetSymbol('goldo.nucleo.Heartbeat')()
    msg.timestamp = _unpack_heartbeat(payload)[0]
    return msg

@nucleo_in('os/ping', nucleo_message_ids.CommUartPing)
def ping(msg):
    return b''

@nucleo_out('os/heap_stats', nucleo_message_ids.HeapStats)
def watchdog_state(payload):
    return _pb2.deserialize('goldo.nucleo.FreeRTOSHeapStats', payload[:8])
    
@nucleo_out('os/tasks_stats', nucleo_message_ids.TaskStats)
def os_tasks_stats(payload):
    items = []
    try:
        for i in range(len(payload)//24):
            name, runtime_counter, stack_wm, task_number = struct.unpack('<16sIHH', payload[i*24:(i+1)*24])
            items.append(_sym_db.GetSymbol('goldo.nucleo.FreeRTOSTaskStats')(
                task_name=name.strip(b'\x00').decode('utf8'),
                runtime_counter=runtime_counter,
                task_number=task_number
                ))
    except:
        pass
    return _sym_db.GetSymbol('goldo.nucleo.FreeRTOSTasksStats')(tasks=items)
    
@nucleo_out('os/dbg_trace', nucleo_message_ids.DbgTrace)
def os_dbg_trace(payload):
    return _sym_db.GetSymbol('google.protobuf.BytesValue')(value=payload)
    items = []
    for i in range(len(payload)//8):
        a, b, c, d = struct.unpack('<I3Bx', payload[i*8:(i+1)*8])
        print(a,b,c,d)
    return _sym_db.GetSymbol('goldo.nucleo.FreeRTOSTasksStats')(tasks=items)

@nucleo_out('os/reset', nucleo_message_ids.Reset)
def os_reset(payload):
    return _sym_db.GetSymbol('google.protobuf.Empty')()

@nucleo_out('os/task_statistics/uart_comm', nucleo_message_ids.UartCommTaskStatistics)
def os_task_statistics_uart_comm(payload):
    return _pb2.deserialize('goldo.nucleo.statistics.UARTCommTaskStatistics', payload)


@nucleo_out('os/task_statistics/odrive_comm', nucleo_message_ids.ODriveCommTaskStatistics)
def os_task_statistics_odrive_comm(payload):
    return _pb2.deserialize('goldo.nucleo.statistics.ODriveCommTaskStatistics', payload)

@nucleo_out('os/task_statistics/propulsion', nucleo_message_ids.PropulsionTaskStatistics)
def os_task_statistics_uart_comm(payload):
    return _pb2.deserialize('goldo.nucleo.statistics.PropulsionTaskStatistics', payload)


@nucleo_out('watchdog/state', nucleo_message_ids.WatchdogStatus)
def watchdog_state(payload):
    return _pb2.deserialize('goldo.nucleo.WatchdogState', payload[:6])

@nucleo_out('sensors/state', nucleo_message_ids.SensorsState)
def sensors_state(payload):
    return _pb2.deserialize('goldo.nucleo.SensorsState', payload)

@nucleo_out('match/timer', nucleo_message_ids.MatchTimer)
def match_timer(payload):
    return _pb2.deserialize('google.protobuf.Int32Value', payload)

@nucleo_in('match/timer/start', nucleo_message_ids.MatchTimerStart)
def match_timer_start(msg):
    return b''
    
@nucleo_in('match/timer/stop', nucleo_message_ids.MatchTimerStop)
def match_timer_start(msg):
    return b''

@nucleo_out('match/end', nucleo_message_ids.MatchEnd)
def match_end(payload):
    return None

@nucleo_in('robot/config/load_begin', nucleo_message_ids.RobotConfigLoadBegin)
def robot_config_load_begin(msg):
    return struct.pack('<H', msg.size)

@nucleo_in('robot/config/load_chunk', nucleo_message_ids.RobotConfigLoadChunk)
def robot_config_load_chunk(msg):
    return msg.data

@nucleo_in('robot/config/load_end', nucleo_message_ids.RobotConfigLoadEnd)
def robot_config_load_end(msg):
    return struct.pack('<H', msg.crc)

@nucleo_out('robot/config/load_status', nucleo_message_ids.RobotConfigLoadStatus)
def robot_config_load_status(payload):
    msg = _sym_db.GetSymbol('goldo.nucleo.robot.ConfigLoadStatus')()
    msg.status = struct.unpack('<B', payload)[0]
    return msg

@nucleo_in('odrive/request', nucleo_message_ids.ODriveRequestPacket)
def odrive_request(msg):
    # bit 15 is reserved by odrive protocol, bit 14 is set to 0
    buff = struct.pack('<HHH', msg.sequence_number & 0x3fff, msg.endpoint_id, msg.expected_response_size)
    buff += msg.payload
    buff += struct.pack('<H', msg.protocol_version)
    return buff

@nucleo_out('odrive/response', nucleo_message_ids.ODriveResponsePacket)
def odrive_response(payload):
    msg = _sym_db.GetSymbol('goldo.nucleo.odrive.ResponsePacket')()
    msg.sequence_number = struct.unpack('<H', payload[0:2])[0] & 0x3fff
    msg.payload = payload[2:]
    return msg

@nucleo_out('odrive/telemetry', nucleo_message_ids.ODriveTelemetry)
def odrive_telemetry(payload):
    return _pb2.deserialize('goldo.nucleo.odrive.Telemetry', payload)

@nucleo_in('dynamixels/request', nucleo_message_ids.DynamixelsRequest)
def dynamixels_request(msg):
    buff = struct.pack('<Hbbb',
        msg.sequence_number,
        msg.protocol_version,
        msg.id,
        msg.command
        )
    buff = buff + msg.payload
    return buff

@nucleo_out('dynamixels/response', nucleo_message_ids.DynamixelsResponse)
def dynamixels_response(payload):
    msg = _sym_db.GetSymbol('goldo.nucleo.dynamixels.ResponsePacket')()
    vals = struct.unpack('<HBBB', payload[0:5])
    msg.sequence_number = vals[0]
    msg.protocol_version = vals[1]
    msg.id = vals[2]
    msg.error_flags = vals[3]
    msg.payload = payload[4:]
    return msg


@nucleo_in('fpga/reg/read', nucleo_message_ids.FpgaReadReg)
def fpga_reg_read(msg):
    return _pb2.serialize(msg)

@nucleo_out('fpga/reg', nucleo_message_ids.FpgaReadRegStatus)
def fpga_reg_read_status(payload):
    return _pb2.deserialize('goldo.nucleo.fpga.RegReadStatus', payload)

@nucleo_in('fpga/reg/write', nucleo_message_ids.FpgaWriteReg)
def fpga_reg_write(msg):
    return _pb2.serialize(msg)

@nucleo_in('fpga/adc/read', nucleo_message_ids.FpgaReadAdc)
def fpga_adc_read(msg):
    return _pb2.serialize(msg)

@nucleo_out('fpga/adc/read_out', nucleo_message_ids.FpgaReadAdcOut)
def fpga_adc_read_out(payload):
    return _pb2.deserialize('goldo.nucleo.fpga.AdcReadOut', payload)


@nucleo_in('odometry/config/get', nucleo_message_ids.OdometryConfigGet)
def odometry_config_get(msg):
    return b''

@nucleo_out('odometry/config', nucleo_message_ids.OdometryConfigGetStatus)
def odometry_config_get_status(payload):
    return _pb2.deserialize('goldo.nucleo.propulsion.OdometryConfig', payload)

@nucleo_in('odometry/config/set', nucleo_message_ids.OdometryConfigSet)
def odometry_config_set(msg):
    return _pb2.serialize(msg)


@nucleo_in('propulsion/config/get', nucleo_message_ids.PropulsionConfigGet)
def propulsion_config_get(msg):
    return b''

@nucleo_out('propulsion/config', nucleo_message_ids.PropulsionConfigGetStatus)
def propulsion_config_get_status(payload):
    return _pb2.deserialize('goldo.nucleo.propulsion.PropulsionControllerConfig', payload)

@nucleo_in('propulsion/config/set', nucleo_message_ids.PropulsionConfigSet)
def propulsion_config_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/enable/set', nucleo_message_ids.PropulsionEnableSet)
def propulsion_enable_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/simulation/enable', nucleo_message_ids.PropulsionSetSimulationMode)
def propulsion_simulation_enable_set(msg):
    return struct.pack('<B', msg.value)

@nucleo_in('propulsion/motors/enable/set', nucleo_message_ids.PropulsionMotorsEnableSet)
def propulsion_motors_enable_set(msg):
    return struct.pack('<B', msg.value)

@nucleo_in('propulsion/emergency_stop', nucleo_message_ids.PropulsionEmergencyStop)
def propulsion_emergency_stop(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/clear_error', nucleo_message_ids.PropulsionClearError)
def propulsion_clear_error(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/motors/velocity_setpoints/set', nucleo_message_ids.PropulsionMotorsVelocitySetpointsSet)
def propulsion_motors_velocity_setpoints_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/target_speed/set', nucleo_message_ids.PropulsionSetTargetSpeed)
def propulsion_target_speed_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/pose/set', nucleo_message_ids.PropulsionSetPose)
def propulsion_pose_set(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/calibrate_odrive', nucleo_message_ids.PropulsionCalibrateODrive)
def propulsion_calibrate_odrive(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/odrive/clear_errors', nucleo_message_ids.PropulsionODriveClearErrors)
def propulsion_odrive_clear_errors(msg):
    return _pb2.serialize(msg)

@nucleo_out('propulsion/odrive/statistics', nucleo_message_ids.PropulsionODriveStatistics)
def propulsion_odrive_statistics(payload):
    return _pb2.deserialize('goldo.nucleo.odrive.ClientStatistics', payload[:9])


@nucleo_out('propulsion/odrive/axis_states', nucleo_message_ids.PropulsionODriveAxisStates)
def propulsion_odrive_axis_states(payload):
    msg = _pb2.deserialize('goldo.nucleo.odrive.AxisStates', payload)
    return msg

@nucleo_out('propulsion/odrive/errors', nucleo_message_ids.PropulsionODriveAxisErrors)
def propulsion_odrive_errors(payload):
    msg = _pb2.deserialize('goldo.nucleo.odrive.AxisErrorStates', payload)
    return msg

@nucleo_in('propulsion/clear_command_queue', nucleo_message_ids.PropulsionClearCommandQueue)
def propulsion_clear_command_queue(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/translation', nucleo_message_ids.PropulsionExecuteTranslation)
def propulsion_execute_translation(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/reposition', nucleo_message_ids.PropulsionExecuteReposition)
def propulsion_execute_reposition(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/measure_normal', nucleo_message_ids.PropulsionMeasureNormal)
def propulsion_execute_reposition(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/move_to', nucleo_message_ids.PropulsionExecuteMoveTo)
def propulsion_execute_move_to(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/rotation', nucleo_message_ids.PropulsionExecuteRotation)
def propulsion_execute_rotation(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/point_to', nucleo_message_ids.PropulsionExecutePointTo)
def propulsion_execute_point_to(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/point_to_back', nucleo_message_ids.PropulsionExecutePointToBack)
def propulsion_execute_point_to(msg):
    return _pb2.serialize(msg)

@nucleo_in('propulsion/cmd/face_direction', nucleo_message_ids.PropulsionExecuteFaceDirection)
def propulsion_execute_face_direction(msg):
    return _pb2.serialize(msg)


@nucleo_out('propulsion/cmd_event', nucleo_message_ids.PropulsionCommandEvent)
def propulsion_cmd_ack(payload):
    return _pb2.deserialize('goldo.nucleo.propulsion.CommandStatus', payload)

@nucleo_out('propulsion/telemetry', nucleo_message_ids.PropulsionTelemetry)
def propulsion_telemetry(payload):
    msg = _msg_propulsion_Telemetry()
    vals = _unpack_propulsion_Telemetry(payload)
    msg.pose.position.x = vals[0] * 0.25e-3
    msg.pose.position.y = vals[1] * 0.25e-3
    msg.pose.yaw = vals[2] * math.pi / 32767
    msg.pose.speed = vals[3] * 1e-3
    msg.pose.yaw_rate = vals[4] * 1e-3
    msg.pose.acceleration = vals[5] * 1e-3
    msg.pose.angular_acceleration = vals[6] * 1e-3
    msg.left_encoder = vals[7]
    msg.right_encoder = vals[8]
    msg.left_pwm = vals[9] * 1e-2
    msg.right_pwm = vals[10] * 1e-2
    msg.state = vals[11]
    msg.error = vals[12]
    return msg

@nucleo_out('propulsion/telemetry_ex', nucleo_message_ids.PropulsionTelemetryEx)
def propulsion_telemetry_ex(payload):
    msg = _msg_propulsion_TelemetryEx()
    vals = _unpack_propulsion_TelemetryEx(payload)
    msg.target_pose.position.x = vals[0] * 0.25e-3
    msg.target_pose.position.y = vals[1] * 0.25e-3
    msg.target_pose.yaw = vals[2] * math.pi / 32767
    msg.target_pose.speed = vals[3] * 1e-3
    msg.target_pose.yaw_rate = vals[4] * 1e-3
    msg.lookahead_position.x = vals[5] * 0.25e-3
    msg.lookahead_position.y = vals[6] * 0.25e-3
    msg.error_longi = vals[7] * 0.25e-3
    msg.error_lateral = vals[8] * 0.25e-3
    msg.error_speed = vals[9] * 1e-3
    msg.error_yaw = vals[10]  * math.pi / 32767
    msg.error_yaw_rate = vals[11]
    return msg

@nucleo_out('propulsion/state', nucleo_message_ids.PropulsionState)
def propulsion_state(payload):
    return _pb2.deserialize('goldo.nucleo.propulsion.StateChange', payload)

@nucleo_out('propulsion/odrive/telemetry', nucleo_message_ids.PropulsionODriveTelemetry)
def propulsion_telemetry(payload):
    return _pb2.deserialize('goldo.nucleo.odrive.Telemetry', payload)

@nucleo_out('propulsion/odometry_stream', nucleo_message_ids.PropulsionOdometryStream)
def odometry_stream(payload):
    return _msg_BytesValue(value=payload)

@nucleo_out('propulsion/odrive_stream', nucleo_message_ids.PropulsionODriveStream)
def odrive_stream(payload):
    return _msg_BytesValue(value=payload)

@nucleo_in('propulsion/scope/config/set', nucleo_message_ids.PropulsionScopeConfig)
def propulsion_scope_config_set(msg):
    if len(msg.channels) > 8:
        raise RuntimeError('ScopeConfig channels count > 8')
    return struct.pack('<HH', msg.period, len(msg.channels)) + b''.join([_pb2.serialize(channel) for channel in msg.channels])

@nucleo_out('propulsion/scope/data', nucleo_message_ids.PropulsionScopeData)
def propulsion_scope(payload):
    msg = _sym_db.GetSymbol('goldo.nucleo.ScopeData')()
    msg.timestamp = struct.unpack('<H', payload[0:2])[0]
    msg.data = payload[2:]
    return msg

@nucleo_in('dbg_goldo', nucleo_message_ids.DbgGoldo)
def dbg_goldo_in(msg):
    #print ("in : {:x}".format(msg.value))
    return struct.pack('<I', msg.value)

@nucleo_out('dbg_goldo', nucleo_message_ids.DbgGoldo)
def dbg_goldo_out(payload):
    val = struct.unpack("<I", payload)
    #print ("out : {:x}".format(val[0]))
    msg = _sym_db.GetSymbol('google.protobuf.UInt32Value')(value = val[0])
    return msg

@nucleo_in('get_nucleo_firmware_version', nucleo_message_ids.GetNucleoFirmwareVersion)
def get_nucleo_firmware_version_in(msg):
    return b''

@nucleo_out('get_nucleo_firmware_version', nucleo_message_ids.GetNucleoFirmwareVersion)
def get_nucleo_firmware_version_out(payload):
    msg = _sym_db.GetSymbol('google.protobuf.StringValue')(value = payload.decode('utf-8'))
    return msg

