#!/usr/bin/env python3
"""
Iconic Arcade Power Button Service Daemon
This daemon is launched through /etc/init.d/S92switch
"""
import os
import sys
import logging
import gpiod
from gpiod.line import Edge
from datetime import datetime, timedelta
from threading import Thread

SHUTDOWN_PIN = 3
CHIP = "/dev/gpiochip0"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, handlers=[
        logging.FileHandler("/userdata/iconicarcade.log", mode="w"),
        logging.StreamHandler(),
    ]
)

def shutdown_check():
    try:
        request = gpiod.request_lines(CHIP, consumer="watch-line-falling", config={SHUTDOWN_PIN: gpiod.LineSettings(edge_detection=Edge.BOTH)})
    except OSError as e:
        logger.error(f"Error requesting gpio lines: {e}")
        return
    last_falling = datetime.fromtimestamp(0)
    while True:
        for event in request.read_edge_events():
            if event.event_type is event.Type.FALLING_EDGE:
                last_falling = datetime.now()
            if event.event_type is event.Type.RISING_EDGE:
                if last_falling.timestamp() == 0: 
                    continue

                delta = datetime.now() - last_falling
                last_falling = datetime.fromtimestamp(0)
                if delta > timedelta(seconds=3):
                    logger.info("Longpress detected")
                    os.system("/usr/bin/batocera-es-swissknife --shutdown")
                elif delta < timedelta(seconds=1):
                    logger.info("Shortpress detected")
                    os.system("/usr/bin/batocera-es-swissknife --emukill")

if len(sys.argv) > 1 and str(sys.argv[1]) == "start":
    logger.info("starting rpi-iconicarcade")
    if not gpiod.is_gpiochip_device(CHIP):
        logger.error(f"failed opening {device}")
        sys.exit(1)
    try:
        t = Thread(target=shutdown_check)
        t.start()
    except Exception as e:
        logger.error(f"Could not launch daemon: {e}")
        t.stop()
