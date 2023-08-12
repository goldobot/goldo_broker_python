import sys
import signal

from goldo_broker.broker.broker_process import run_broker_process

def goldo_signal_handler(sig,frame):
    print (" DEBUG GOLDO : sys.exit(0)")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda sig,frame: goldo_signal_handler(sig,frame))
    run_broker_process()
