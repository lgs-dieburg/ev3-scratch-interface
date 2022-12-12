#!/usr/bin/env python3

import logging
from ev3dev2.motor import MoveTank

logging.basicConfig(format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger('Kalibrierungs Tool')
logger.setLevel(logging.INFO)

motors = MoveTank ("outD", "outA")

if __name__ == '__main__': 
    rotations = input()
    motors.on_for_rotations(-70, 70, rotations)
    ratio = rotations / 360
    logger.info("Rotating %s times. Ratio: %s", rotations, ratio)