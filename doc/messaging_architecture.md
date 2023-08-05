# Messaging architecture

## ZMQ protocol
Protobuf messages are transmitted over ZMQ  sockets as multipart messages. The parts are :
- topic string, for instance 'gui/in/score'
- fully qualified message type,  for instance 'goldo.nucleo.odometry.OdometryConfig'
- Serialized message body