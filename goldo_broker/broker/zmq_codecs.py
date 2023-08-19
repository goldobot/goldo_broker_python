import struct
import logging
import goldo_broker.nucleo.topics._registry as _reg
import struct

import google.protobuf as _pb

_sym_db = _pb.symbol_database.Default()

_msg_type_struct = struct.Struct('<BBHIi')
_lidar_point_struct = struct.Struct('<ff')
_lidar_detection_message_struct = struct.Struct('<IIhhhhhhI')

import pb2 as _pb2

__all__ = ['NucleoCodec', 'ProtobufCodec', 'RPLidarCodec']

LOGGER = logging.getLogger(__name__)

nucleo_in_stat = {}
nucleo_out_stat = {}
nucleo_out_bad_stat = {}
nucleo_very_bad_stat = 0

class NucleoCodec:
    def serialize(self, topic, msg):
        msg_type, encoder = _reg._in.get(topic, (None, None))
        if msg_type not in nucleo_in_stat:
            nucleo_in_stat[msg_type] = 0
        else:
            nucleo_in_stat[msg_type] = nucleo_in_stat[msg_type] + 1
        if encoder is None:
            LOGGER.error("NucleoCodec.serialize() error: topic='{}' msg_type={}".format(topic, msg_type))
            nucleo_very_bad_stat = nucleo_very_bad_stat + 1
            return None
        return [_msg_type_struct.pack(0, 0, msg_type, 0, 0), encoder(msg)]

    def deserialize(self, payload):
        msg_header, msg_body = payload[:2]

        comm_id, reserved, msg_type, t_seconds, t_nanoseconds = _msg_type_struct.unpack(msg_header)
        topic, decoder = _reg._out.get(msg_type, (None, None))
        if topic is not None:
            if msg_type not in nucleo_out_stat:
                nucleo_out_stat[msg_type] = 0
            else:
                nucleo_out_stat[msg_type] = nucleo_out_stat[msg_type] + 1
            try:
                msg = decoder(msg_body)
                if msg is None:
                    msg = _sym_db.GetSymbol('google.protobuf.Empty')()
            except Exception as e:
                logging.exception(e)
                return None, None
            return topic, msg
        else:
            if msg_type not in nucleo_out_bad_stat:
                nucleo_out_bad_stat[msg_type] = 0
            else:
                nucleo_out_bad_stat[msg_type] = nucleo_out_bad_stat[msg_type] + 1
            return None, None


class ProtobufCodec:
    def serialize(self, topic, msg):
        return [topic.encode('utf8'),
                msg.DESCRIPTOR.full_name.encode('utf8'),
                msg.SerializeToString()
                ]

    def deserialize(self, payload):
        topic, full_name, payload = payload
        topic = topic.decode('utf8')
        full_name = full_name.decode('utf8')
        msg_class = _sym_db.GetSymbol(full_name)
        if msg_class is not None:
            msg = msg_class()
            msg.ParseFromString(payload)
            return topic, msg
        else:
            return None, None


class RPLidarCodec:
    def serialize(self, topic, msg):
        if topic == 'rplidar/in/start':
            return [struct.pack('<b', 1), b'']
        if topic == 'rplidar/in/stop':
            return [struct.pack('<b', 2), b'']
        if topic == 'rplidar/in/config/theta_offset':
            return [struct.pack('<b', 3), struct.pack('<f', msg.value)]
        if topic == 'rplidar/in/config/distance_tresholds':
            return [struct.pack('<b', 5), struct.pack('<fff', msg.near, msg.mid, msg.far)]
        if topic == 'rplidar/in/robot_pose':
            return [struct.pack('<b', 4), struct.pack('<fff', msg.position.x, msg.position.y, msg.yaw)]
        if topic == 'rplidar/in/config/autotest_enable':
            return [struct.pack('<b', 6), struct.pack('<B', msg.value)]
        if topic == 'rplidar/in/config/send_scan_enable':
            return [struct.pack('<b', 7), struct.pack('<B', msg.value)]
        return None

    def deserialize(self, payload):
        msg_type = struct.unpack('<B', payload[0])[0]
        if msg_type == 1:
            msg = _sym_db.GetSymbol('goldo.common.geometry.PointCloud')(
                num_points=len(payload[2]) // 8,
                data=payload[2])
            return 'rplidar/out/scan', msg
        if msg_type == 2:
            vals = _lidar_detection_message_struct.unpack(payload[1])
            msg = _sym_db.GetSymbol('goldo.rplidar.RobotDetection')(
                timestamp_ms=vals[0],
                id=vals[1],
                x=vals[2] * 0.25e-3,
                y=vals[3] * 0.25e-3,
                vx=vals[4] * 1e-3,
                vy=vals[5] * 1e-3,
                ax=vals[6] * 1e-3,
                ay=vals[7] * 1e-3,
                detect_quality=vals[8]
            )
            return 'rplidar/out/robot_detection', msg
        if msg_type == 42:
            msg = _pb2.deserialize('goldo.rplidar.Zones', payload[1])
            return 'rplidar/out/detections', msg
        return None, None
