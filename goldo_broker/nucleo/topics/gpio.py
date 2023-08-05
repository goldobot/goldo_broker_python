import pb2 as _pb2
import struct

from goldo_broker.nucleo.topics._registry import *

_sym_db = _pb2._sym_db

@nucleo_in('gpio/set', 22)
def gpio_set(msg):
    return _pb2.serialize(msg)
