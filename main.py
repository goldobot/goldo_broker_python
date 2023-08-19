import sys
import signal

from goldo_broker.broker.broker_process import run_broker_process
from goldo_broker.broker.zmq_codecs import nucleo_in_stat,nucleo_out_stat,nucleo_bad_stat,nucleo_very_bad_stat

def goldo_signal_handler(sig,frame):
    print (" DEBUG GOLDO : sys.exit(0)")
    print ("nucleo_in_stat:")
    for k in nucleo_in_stat.keys():
        print (k, nucleo_in_stat[k])
    print ()
    print ("nucleo_out_stat:")
    for k in nucleo_out_stat.keys():
        print (k, nucleo_out_stat[k])
    print ()
    print ("nucleo_bad_stat:")
    for k in nucleo_bad_stat.keys():
        print (k, nucleo_bad_stat[k])
    print ()
    print ("nucleo_very_bad_stat:")
    print (nucleo_very_bad_stat)
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda sig,frame: goldo_signal_handler(sig,frame))
    run_broker_process()
