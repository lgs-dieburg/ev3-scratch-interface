import logging
import sys
from time import sleep
import struct
import threading
from ev3dev2.led import Leds

# WARNING Triggers are not yet implemented

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('')
logger.setLevel(logging.INFO)


class Gamepad:
    logger = logging.getLogger('GAMEPAD')

    # Constants
    _gamepad_xbox = 1
    _gamepad_ps = 2

    # Defining stick dead zone which is a minimum amount of stick movement
    # from the center position to start motors
    _stick_deadzone = 10  # deadzone 5%

    _enable_xbox_detection = True
    _enable_ps_detection = True

    # long int, long int, unsigned short, unsigned short, long int
    FORMAT = 'llHHl'

    _gamepad_device = None
    _gamepad_type = 0  # gamepad_xbox or gamepad_ps
    # True if Xbox or False if PlayStation
    _xbox = None

    # Tells other classes whether controller is checking inputs
    _checking_for_inputs = False

    # Button Values

    BUTTON_A = 0
    BUTTON_B = 0
    BUTTON_X = 0
    BUTTON_Y = 0
    STICK_LEFT = 0
    STICK_RIGHT = 0
    BUTTON_SELECT = 0
    BUTTON_START = 0
    BUMPER_LEFT = 0
    BUMPER_RIGHT = 0
    DPAD_UP_DOWN = 0
    DPAD_LEFT_RIGHT = 0
    LEFT_STICK_X = 0
    LEFT_STICK_Y = 0
    RIGHT_STICK_X = 0
    RIGHT_STICK_Y = 0

    def __init__(self):
        self._gamepad_device = self._find_controller()
        self._xbox = self._gamepad_type == self._gamepad_xbox

    def _find_controller(self):
        """
        Checks device list by reading content of virtual file "/proc/bus/input/devices"
        looking for gamepad device.
        """
        with open("/proc/bus/input/devices", "r") as fp:
            line = fp.readline()
            while line:
                if self._enable_xbox_detection and line.startswith("N: Name=") and line.find("Xbox") > -1:
                    self._gamepad_type = self._gamepad_xbox
                    logger.info("xBox gamepad detected")
                if self._enable_ps_detection and line.startswith("N: Name=") and line.find(
                        "PLAYSTATION") > -1 and line.find("Motion") == -1:
                    self._gamepad_type = self._gamepad_ps
                    logger.info("PlayStation gamepad detected")
                if self._gamepad_type > 0 and line.startswith("H: Handlers="):
                    line = line[len("H: Handlers="):]
                    pb = line.find("event")
                    pe = line.find(" ", pb)
                    return line[pb:pe]
                line = fp.readline()
        return None

    def _convert_input_stick(self, value):
        """
        Transform range 0..max to -100..100, remove deadzone from the range
        """
        max = 65535 if self._xbox else 255
        half = int((max + 1) / 2)
        deadzone = int((max + 1) / 100 * self._stick_deadzone)
        value -= half
        if abs(value) < deadzone:
            value = 0
        elif value > 0:
            value = (value - deadzone - 1) / (half - deadzone) * 100
        else:
            value = (value + deadzone) / (half - deadzone) * 100
        return value

    def start_reading_inputs(self):
        threading.Thread(target=self._reading_gamepad_inputs, daemon=True).start()

    def _start_led(self):
        leds = Leds()
        leds.animate_police_lights('RED', 'GREEN', sleeptime=0.25, duration=None)

    def _reading_gamepad_inputs(self):
        logger.info("Start reading inputs")
        try:
            infile_path = "/dev/input/" + self._gamepad_device
        except Exception:
            logger.error("Detection error! Please make sure that a gamepad is connected to ev3")
            sleep(10)
            sys.exit(1)

        threading.Thread(target=self._start_led, daemon=True).start()

        with open(infile_path, "rb") as in_file:
            # Read from the file
            EVENT_SIZE = struct.calcsize(self.FORMAT)
            event = in_file.read(EVENT_SIZE)

            self._checking_for_inputs = True

            # Funktion iteriert durch Controller Events und setzt die momentanen Values der Buttons ein
            while event:
                (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(self.FORMAT, event)

                if ev_type == 3 or ev_type == 1:
                    if ev_type == 3 and code == 0:  # Left Stick Horz. Axis
                        # Stick Value wird direkt in Wert zwischen -100 und 100 umgerechnet
                        self.LEFT_STICK_X = self._convert_input_stick(value)
                    elif ev_type == 3 and code == 1:  # Left Stick Vert. Axis
                        # Stick Value wird direkt in Wert zwischen -100 und 100 umgerechnet
                        self.LEFT_STICK_Y = self._convert_input_stick(value)
                    elif ev_type == 3 and code == 2:  # Right Stick Horz. Axis
                        # Stick Value wird direkt in Wert zwischen -100 und 100 umgerechnet
                        self.RIGHT_STICK_X = self._convert_input_stick(value)
                    elif ev_type == 3 and code == 5:  # Right Stick Vert. Axis
                        # Stick Value wird direkt in Wert zwischen -100 und 100 umgerechnet
                        self.RIGHT_STICK_Y = self._convert_input_stick(value)
                    elif ev_type == 1 and code == 304:  # A-Button
                        self.BUTTON_A = value
                    elif ev_type == 1 and code == 305:  # B-Button
                        self.BUTTON_B = value
                    elif ev_type == 1 and code == 307:  # X-Button
                        self.BUTTON_X = value
                    elif ev_type == 1 and code == 308:  # Y-Button
                        self.BUTTON_Y = value
                    elif ev_type == 1 and code == 317:  # Left Stick
                        self.STICK_LEFT = value
                    elif ev_type == 1 and code == 318:  # Right Stick
                        self.STICK_RIGHT = value
                    elif ev_type == 1 and code == 158:  # Button Select
                        self.BUTTON_SELECT = value
                    elif ev_type == 1 and code == 315:  # Button Start
                        self.BUTTON_START = value
                    elif ev_type == 1 and code == 310:  # Left Bumper
                        self.BUMPER_LEFT = value
                    elif ev_type == 1 and code == 311:  # Right Bumper
                        self.BUMPER_RIGHT = value
                    elif ev_type == 3 and code == 17:  # DPad Up Down
                        self.DPAD_UP_DOWN = value
                    elif ev_type == 3 and code == 16:  # DPad Left Right
                        self.DPAD_LEFT_RIGHT = value

                # Finally, read another event
                event = in_file.read(EVENT_SIZE)

            self._checking_for_inputs = False

    @property
    def checking_for_inputs(self):
        return self._checking_for_inputs


def limit_input_percentage(input_percentage, limit):
    """
    limit_input_percentage Checkt ob input_percentage limit ueberschreitet.
    Wenn limit ueberschritten, wird input_percentage auf limit gesetzt und returnt.

    Args:
        input_percentage (float): Percentage die gegen limit getestet werden soll
        limit (float): Max percentage. Es wird immer mit dem Betrag des Limits gearbeitet.

    Returns:
        float: Limitierte percentage
    """
    if input_percentage > abs(limit):
        return abs(limit)
    elif input_percentage < (abs(limit) * -1):
        return (abs(limit) * -1)
    else:
        return input_percentage


class GamepadHandler:
    logger = logging.getLogger('GAMEPAD HANDLER')

    connected_gamepad = None

    def __init__(self, gamepad):
        # Declaring controller
        try:
            self.connected_gamepad = gamepad
        except Exception:
            logger.error("Error while declaring the controller. Please check if controller is connected")
            sleep(10)
            sys.exit(1)

    # TODO Test Handle onlick und handle stick mit neuen Treads
    def handle_onpress_events(self,
                              onpress_button_a=None,
                              onpress_button_b=None,
                              onpress_button_x=None,
                              onpress_button_y=None,
                              onpress_stick_left=None,
                              onpress_stick_right=None,
                              onpress_button_select=None,
                              onpress_button_start=None,
                              onpress_bumper_left=None,
                              onpress_bumper_right=None,
                              onpress_dpad_up=None,
                              onpress_dpad_down=None,
                              onpress_dpad_left=None,
                              onpress_dpad_right=None
                              ):
        logger.info("Start handling inputs")

        def _thread_target():
            while self.connected_gamepad.checking_for_inputs:
                if self.connected_gamepad.BUTTON_A == 1 and onpress_button_a is not None:
                    onpress_button_a()
                elif self.connected_gamepad.BUTTON_B == 1 and onpress_button_b is not None:
                    onpress_button_b()
                elif self.connected_gamepad.BUTTON_X == 1 and onpress_button_x is not None:
                    onpress_button_x()
                elif self.connected_gamepad.BUTTON_Y == 1 and onpress_button_y is not None:
                    onpress_button_y()
                elif self.connected_gamepad.STICK_LEFT == 1 and onpress_stick_left is not None:
                    onpress_stick_left()
                elif self.connected_gamepad.STICK_RIGHT == 1 and onpress_stick_right is not None:
                    onpress_stick_right()
                elif self.connected_gamepad.BUTTON_SELECT == 1 and onpress_button_select is not None:
                    onpress_button_select()
                elif self.connected_gamepad.BUTTON_START == 1 and onpress_button_start is not None:
                    onpress_button_start()
                elif self.connected_gamepad.BUMPER_LEFT == 1 and onpress_bumper_left is not None:
                    onpress_bumper_left()
                elif self.connected_gamepad.BUMPER_RIGHT == 1 and onpress_bumper_right is not None:
                    onpress_bumper_right()
                elif self.connected_gamepad.DPAD_UP_DOWN == -1 and onpress_dpad_up is not None:
                    onpress_dpad_up()
                elif self.connected_gamepad.DPAD_UP_DOWN == 1 and onpress_dpad_down is not None:
                    onpress_dpad_down()
                elif self.connected_gamepad.DPAD_LEFT_RIGHT == -1 and onpress_dpad_left is not None:
                    onpress_dpad_left()
                elif self.connected_gamepad.DPAD_LEFT_RIGHT == 1 and onpress_dpad_right is not None:
                    onpress_dpad_right()

        threading.Thread(target=_thread_target).start()

    def handle_stick_outputs(self, action_left_stick=None, action_right_stick=None):
        def _thread_target():
            while self.connected_gamepad.checking_for_inputs:
                if action_left_stick is not None:
                    action_left_stick()
                if action_right_stick is not None:
                    action_right_stick()

        threading.Thread(target=_thread_target).start()
