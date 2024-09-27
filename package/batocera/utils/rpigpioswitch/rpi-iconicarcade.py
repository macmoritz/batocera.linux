#!/usr/bin/env python3
"""
Iconic Arcade Power Button Service Daemon
This daemon is launched through /etc/init.d/S92switch
"""
import os
import sys
import gpiod
from gpiod.line import Edge
from datetime import datetime, timedelta
from threading import Thread

SHUTDOWN_PIN = 3
CHIP = "/dev/gpiochip0"

def shutdown_check():
    request = gpiod.request_lines(CHIP, consumer="watch-line-falling", config={SHUTDOWN_PIN: gpiod.LineSettings(edge_detection=Edge.BOTH)})
    last_falling = datetime.fromtimestamp(0)
    while True:
        for event in request.read_edge_events():
            if event.event_type is event.Type.FALLING_EDGE:
                print("Falling Edge")
                last_falling = datetime.now()
            if event.event_type is event.Type.RISING_EDGE:
                print("Rising Edge")
                if last_falling.timestamp() == 0: 
                    continue

                delta = datetime.now() - last_falling
                last_falling = datetime.fromtimestamp(0)
                if delta > timedelta(seconds=3):
                    print("Longpress detected")
                    os.system("/usr/bin/batocera-es-swissknife --reboot")
                elif delta < timedelta(seconds=1):
                    print("Shortpress detected")
                    os.system("/usr/bin/batocera-es-swissknife --emukill")

if len(sys.argv) > 1 and str(sys.argv[1]) == "start":
    if not gpiod.is_gpiochip_device(CHIP):
        print(f"failed opening {device}")
        sys.exit(1)
    try:
        t = Thread(target=shutdown_check)
        t.start()
    except Exception as e:
        print(f"Could not launch daemon: {e}")
        t.stop()
