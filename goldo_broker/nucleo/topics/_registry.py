import pb2 as _pb2
import struct

__all__ = [
    'nucleo_out',
    'nucleo_in'
]

_sym_db = _pb2._sym_db

_in = {}
_out = {}

_msg_BytesValue = _sym_db.GetSymbol('google.protobuf.BytesValue')
_msg_propulsion_Telemetry = _sym_db.GetSymbol('goldo.nucleo.propulsion.Telemetry')
_unpack_propulsion_Telemetry = struct.Struct('<hhhhhhhHHbbBB').unpack

_msg_propulsion_TelemetryEx = _sym_db.GetSymbol('goldo.nucleo.propulsion.TelemetryEx')
_unpack_propulsion_TelemetryEx = struct.Struct('<hhhhhhhhhhhh').unpack

_unpack_heartbeat = struct.Struct('<I').unpack


def nucleo_out(topic, msg_type):
    def register_out(fn):
        _out[msg_type] = ('nucleo/out/' + topic, fn)

    return register_out


def nucleo_in(topic, msg_type):
    def register_in(fn):
        _in['nucleo/in/' + topic] = (msg_type, fn)

    return register_in
