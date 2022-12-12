#!/usr/bin/env python3
import json
import logging
import threading
from time import sleep

from ev3dev2.motor import Motor, MoveJoystick, MoveTank
import ev3_server

from gamepad_util import Gamepad, GamepadHandler, limit_input_percentage

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('EV3 CONTROLLER')
logger.setLevel(logging.DEBUG)

gamepad = GamepadHandler(Gamepad())

motors = MoveJoystick("outA", "outB")
movetank = MoveTank("outA", "outB")


def action_left_stick():
    motors.on(limit_input_percentage(gamepad.connected_gamepad.LEFT_STICK_X, 70),
              limit_input_percentage((gamepad.connected_gamepad.LEFT_STICK_Y * -1), 70))


class EV3Controller:

    def __init__(self):
        self.ev3_server = ev3_server.EV3ControlServer(self)
        self._response = None
        self._command = None
        self._distance_data = None
        threading.Thread(target=self.ev3_server.start_server).start()
        with open("settings.json") as file:
            self._rotation_ratio = json.load(file).get("rotation-ratio")

    def process_request(self, request):

        logger.info("Processing Request: %s", request)
        if request.get("methode") == "POST":
            if request.get("parameter").get("command") == "forwards":
                timeout = float(request.get("parameter").get("timeout"))
                speed = float(request.get("parameter").get("speed"))
                movetank.on_for_seconds(speed, speed, timeout)
                self._response = dict(methode="RESPONSE", description="CONFIRMATION")
            elif request.get("parameter").get("command") == "backwards":
                timeout = float(request.get("parameter").get("timeout"))
                speed = float(request.get("parameter").get("speed")) * -1
                movetank.on_for_seconds(speed, speed, timeout)
                self._response = dict(methode="RESPONSE", description="CONFIRMATION")
            elif request.get("parameter").get("command") == "rotate":
                degrees = float(request.get("parameter").get("degrees"))
                corrected = degrees * self._rotation_ratio
                logger.info("%s ROTATIONS", corrected)
                movetank.on_for_rotations(34.7222222, -34.7222222, corrected)
                self._response = dict(methode="RESPONSE", description="CONFIRMATION")

    @property
    def response(self):
        logger.debug("Response %s", self._response)
        return self._response


if __name__ == '__main__':
    ev3_controller = EV3Controller()
    logger.debug("Use Controller to start input handling")

    gamepad.connected_gamepad.start_reading_inputs()
    while not gamepad.connected_gamepad.checking_for_inputs:
        sleep(1)

    gamepad.handle_stick_outputs(action_left_stick=action_left_stick)
    #Change checking for inputs to false to stop handleing --> bei Command
