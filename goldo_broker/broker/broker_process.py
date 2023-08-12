import asyncio
import zmq
import zmq.utils.monitor
from zmq.asyncio import Context, Poller
import struct
import logging
import re
import socket
import setproctitle
import enum

from .zmq_codecs import *

import google.protobuf as _pb
import google.protobuf.descriptor_pb2

_sym_db = _pb.symbol_database.Default()

LOGGER = logging.getLogger(__name__)


# FIXME : TODO : REMOVE (reminder of the old broker implementation..)
class ZmqBrokerCmd(enum.Enum):
    PUBLISH_TOPIC = 0
    REGISTER_CALLBACK = 1
    REGISTER_FORWARD = 2


class ZmqBrokerProcess(object):
    socket_types = {
        'pub': zmq.PUB,
        'sub': zmq.SUB,
        'req': zmq.REQ,
        'rep': zmq.REP
    }

    def __init__(self):
        self._context = Context.instance()
        self._poller = Poller()
        self._sockets = {}
        self._monitors = {}
        self._socket_codecs = {}
        self._callbacks = []
        self._forwards = []
        self._tasks = {}
        ip = 'robot01'
        self.register_socket('nucleo:pub', 'tcp://{}:3002'.format(ip), 'connect', NucleoCodec())
        self.register_socket('nucleo:sub', 'tcp://{}:3001'.format(ip), 'connect', NucleoCodec())

        self._sockets['nucleo:sub'].connect('tcp://{}:3003'.format(ip))

        self.register_socket('rplidar:pub', 'tcp://{}:3101'.format(ip), 'connect', RPLidarCodec())
        self.register_socket('rplidar:sub', 'tcp://{}:3102'.format(ip), 'connect', RPLidarCodec())

        self.register_socket('debug:pub', 'tcp://*:3801', 'bind', ProtobufCodec())
        self.register_socket('debug:sub', 'tcp://*:3802', 'bind', ProtobufCodec())

        self.register_socket('main:rep', 'tcp://*:3301', 'bind', ProtobufCodec())

        socket_out = self._context.socket(zmq.PUB)
        socket_out.bind('tcp://*:3701')
        self._sockets['strat:pub'] = socket_out

        socket_in = self._context.socket(zmq.SUB)
        socket_in.setsockopt(zmq.SUBSCRIBE, b'')
        socket_in.bind('tcp://*:3702')
        self._sockets['strat:sub'] = socket_in
        self._socket_codecs[socket_in] = ('strat', self.onBrokerCmd)
        self._poller.register(socket_in, zmq.POLLIN)

    async def run(self):
        while True:
            events = await self._poller.poll()
            await asyncio.wait([self._readSocket(s, self._socket_codecs[s]) for s, e in events if e & zmq.POLLIN])

    async def onBrokerCmd(self, cmd):
        topic_b, full_name_b, payload = cmd
        topic = topic_b.decode('utf8')
        if topic.startswith("broker/admin/"):
            if topic == "broker/admin/cmd/register_callback":
                full_name = full_name_b.decode('utf8')
                msg_class = _sym_db.GetSymbol(full_name)
                if msg_class is None:
                    print ("broker/admin protocol error!")
                    return
                cmd_msg = msg_class()
                cmd_msg.ParseFromString(payload)
                pattern = cmd_msg.value
                print ("received REGISTER_CALLBACK {}".format(pattern))
                self._callbacks.append((re.compile(f"^{pattern}$"), 0))
                return
            elif topic == "broker/admin/cmd/register_forward":
                full_name = full_name_b.decode('utf8')
                msg_class = _sym_db.GetSymbol(full_name)
                if msg_class is None:
                    print ("broker/admin protocol error!")
                    return
                cmd_msg = msg_class()
                cmd_msg.ParseFromString(payload)
                pattern, forward_str = cmd_msg.value.split('>')
                print ("received REGISTER_FORWARD {} {}".format(pattern,forward_str))
                self._forwards.append((re.compile(f"^{pattern}$"), forward_str))
                return
            elif topic == "broker/admin/cmd/stop":
                print ("received STOP")
                print (" DEBUG GOLDO : sys.exit(0)")
                sys.exit(0)
            elif topic == "broker/admin/cmd/ping":
                full_name = full_name_b.decode('utf8')
                msg_class = _sym_db.GetSymbol(full_name)
                if msg_class is None:
                    print ("broker/admin protocol error!")
                    return
                cmd_msg = msg_class()
                cmd_msg.ParseFromString(payload)
                seq_no = cmd_msg.value
                print ("received PING seq={}".format(seq_no))
                topic = "broker/admin/cmd/pong"
                await self.publishTopic(topic, cmd_msg)
                return
        else:
            full_name = full_name_b.decode('utf8')
            msg_class = _sym_db.GetSymbol(full_name)
            if msg_class is not None:
                cmd_msg = msg_class()
                cmd_msg.ParseFromString(payload)
            else:
                cmd_msg = _sym_db.GetSymbol('google.protobuf.Empty')()
            await self.publishTopic(topic, cmd_msg)
            return

    async def _readSocket(self, socket, codec):
        if codec[0] == 'monitor':
            return await self._readSocketMonitor(socket)
        elif codec[0] == 'strat':
            flags = socket.getsockopt(zmq.EVENTS)
            while flags & zmq.POLLIN:
                payload = await socket.recv_multipart()
                return await self.onBrokerCmd(payload)
        else:
            flags = socket.getsockopt(zmq.EVENTS)
            while flags & zmq.POLLIN:
                payload = await socket.recv_multipart()
                topic, msg = codec[0].deserialize(payload)
                if topic is not None:
                    await codec[1](topic, msg)
                flags = socket.getsockopt(zmq.EVENTS)

    async def _readSocketMonitor(self, socket_):
        flags = socket_.getsockopt(zmq.EVENTS)
        while flags & zmq.POLLIN:
            descr, endpoint = await socket_.recv_multipart()
            event, value = struct.unpack('<HI', descr)
            if event == zmq.EVENT_ACCEPTED:
                try:
                    s = socket.socket(fileno=value)
                    LOGGER.debug(s.getpeername())
                    LOGGER.debug(event, value)
                    s.detach()
                except:
                    LOGGER.debug('ERR')
            flags = socket_.getsockopt(zmq.EVENTS)

    async def _writeSocket(self, socket, topic, msg):
        payload = self._socket_codecs[socket][0].serialize(topic, msg)
        if payload is not None:
            await socket.send_multipart(payload)

    async def onTopicReceived(self, topic, msg=None):
        #print (topic)

        if msg is None:
            msg = _sym_db.GetSymbol('google.protobuf.Empty')()
        callback_matches = tuple((regexp.match(topic), callback) for regexp, callback in self._callbacks)
        callbacks_list = tuple((callback, tuple(match.groups())) for match, callback in callback_matches if match)
        if len(callbacks_list):
            #print (topic)
            await self._sockets['strat:pub'].send_multipart([topic.encode('utf8'), msg.DESCRIPTOR.full_name.encode('utf8'), msg.SerializeToString()])

        forwards_matches = tuple((regexp.match(topic), forward_str) for regexp, forward_str in self._forwards)
        forwards = tuple(
            self.publishTopic(forward_str.format(*match.groups()), msg) for match, forward_str in forwards_matches if
            match)
        if len(forwards):
            self._create_task(asyncio.wait(forwards))

        await self.publishTopic(topic, msg)

    async def publishTopic(self, topic, msg):
        #print (topic)
        if topic.startswith('nucleo/in/'):
            self._create_task(self._writeSocket(self._sockets['nucleo:pub'], topic, msg))
        if topic.startswith('rplidar/in/'):
            await self._create_task(self._writeSocket(self._sockets['rplidar:pub'], topic, msg))
        await self._create_task(self._writeSocket(self._sockets['debug:pub'], topic, msg))

    async def _onRequestReceived(self, topic, msg=None):
        descriptor = _sym_db.pool.FindMessageTypeByName(msg.value)
        proto = google.protobuf.descriptor_pb2.DescriptorProto()
        descriptor.CopyToProto(proto)
        await self._writeSocket(self._sockets['main:rep'], topic + '/resp', proto)

    def register_socket(self, name, url, connection_type, codec):
        socket_type = self.__class__.socket_types.get(name.split(':')[-1])
        socket = self._context.socket(socket_type)
        func = None
        if socket_type == zmq.PUB:
            monitor = socket.get_monitor_socket()
            self._monitors[socket] = monitor
            self._socket_codecs[monitor] = ('monitor', None)
            self._poller.register(monitor, zmq.POLLIN)
        if socket_type == zmq.SUB:
            socket.setsockopt(zmq.SUBSCRIBE, b'')
            self._poller.register(socket, zmq.POLLIN)
            func = self.onTopicReceived
        if socket_type == zmq.REP:
            func = self._onRequestReceived
            self._poller.register(socket, zmq.POLLIN)
        if connection_type == 'connect':
            socket.connect(url)
        if connection_type == 'bind':
            socket.bind(url)
        self._sockets[name] = socket
        self._socket_codecs[socket] = (codec, func)
        
    def _create_task(self, aw):
        task = asyncio.create_task(aw)
        self._tasks[id(task)] = task
        task.add_done_callback(self._on_task_done)
        return task

    def _on_task_done(self, task):
        del self._tasks[id(task)]
        try:
            task.result()
        except Exception:
            LOGGER.exception('error in broker callback')


def run_broker_process():
    setproctitle.setproctitle('goldo_broker.broker')
    broker = ZmqBrokerProcess()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(broker.run())
