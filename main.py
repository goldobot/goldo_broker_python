import sys
import signal
import time

from goldo_broker.broker.broker_process import run_broker_process
from goldo_broker.broker.zmq_codecs import nucleo_in_stat,nucleo_out_stat,nucleo_out_bad_stat,nucleo_very_bad_stat

stats_t0 = 0

def goldo_signal_handler(sig,frame):
    stats_t1 = time.time()
    print (" DEBUG GOLDO : sys.exit(0)")
    print ("elapsed time:")
    print (stats_t1 - stats_t0)
    print ("nucleo_in_stat:")
    for k in nucleo_in_stat.keys():
        print (k, nucleo_in_stat[k])
    print ()
    print ("nucleo_out_stat:")
    for k in nucleo_out_stat.keys():
        print (k, nucleo_out_stat[k])
    print ()
    print ("nucleo_out_bad_stat:")
    for k in nucleo_out_bad_stat.keys():
        print (k, nucleo_out_bad_stat[k])
    print ()
    print ("nucleo_very_bad_stat:")
    print (nucleo_very_bad_stat)
    sys.exit(0)

if __name__ == '__main__':
    stats_t0 = time.time()
    signal.signal(signal.SIGINT, lambda sig,frame: goldo_signal_handler(sig,frame))
    run_broker_process()
