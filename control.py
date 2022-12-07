#!/usr/bin/env python3
import logging
import threading
from flask import Flask
from flask import request
from time import sleep
import client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('PI CONTROLLER')
logger.setLevel(logging.INFO)

app = Flask(__name__)


class PiController:
    _response = None
    _command = None
    _request_queue = []
    _requesting_thread = None

    # Hier wird die Response des EV3 Servers angenommen
    def process_response(self, response):
        if response.get("methode") == "RESPONSE":
            if response.get("description") == "distance_data":
                try:
                    self.distance_data = round(float(response.get("value")))
                    self.queue_get_distance_data()
                    self._response_received = True
                except ValueError:
                    logger.error("Error while casting response into int. Current value of distance data: %s",
                                 self._distance_data)
            elif response.get("description") == "CONFIRMATION":
                logger.info("EV3 has received to command.")
                self._response_received = True

    # Fügt einen neue Request der Queue hinzu.
    def add_request_to_queue(self, methode, parameter):
        self._request_queue.append(dict(methode=methode, parameter=parameter))

    def start_requesting(self):
        def _start_requesting(self):
            self._running = True
            while True:
                self._response_received = False
                _request = self._request_queue.pop(0)
                self.pi_client.send_server_request(_request.get("methode"), _request.get("parameter"))
                sleep(1)
                while self._response_received is False:
                    sleep(1)

        self._requesting_thread = threading.Thread(target=_start_requesting, args=(self,))
        self._requesting_thread.start()

    @property
    def response(self):
        logger.debug("Response %s", self._response)
        return self._response

    @property
    def distance_data(self):
        return self._distance_data

    @distance_data.setter
    def distance_data(self, distance_data):
        if isinstance(self._distance_data, int):
            logger.debug("New distance data set")
            self._distance_data = distance_data
        else:
            logger.error("New distance data not set. Data not instance of int")

    def queue_get_distance_data(self):
        def _queue_get_distance_data(self):
            sleep(0.5)
            self.add_request_to_queue("GET", "distance_data")

        threading.Thread(target=_queue_get_distance_data, args=(self,), daemon=True).start()

    def __init__(self):
        self.pi_client = pi_client.PiClient(self)
        self._response_received = False
        logger.debug("Server created. Going to start server")
        self.start_requesting()
        self.queue_get_distance_data()


@app.route('/forward')
async def move_forwards():
    timeout = request.args.get("timeout")
    speed = request.args.get("speed")

    global ev3_commands_active
    timeout = int(timeout)
    speed = int(speed)
    if not ev3_commands_active:
        logger.info("Commands are not active")
        return "Befehle sind gerade deaktiviert."
    elif timeout is None and speed is None:
        # TODO None handling hinzufügen
        logger.debug("param timeout or speed is None")
    else:
        if timeout > 15:
            timeout = 15
        elif timeout < 0:
            timeout = 0
        if speed < 0:
            speed = abs(speed)
        if speed > 100:
            speed = 100
        if speed > 0 and timeout > 0:
            pi_controller.add_request_to_queue("POST", dict(command="forwards", timeout=timeout, speed=speed))
            return f"Fahre vorwärts {timeout} Sekunden lang mit einer Geschwindigkeit von {speed} %"


async def move_backwards(timeout=None, speed=None):
    global ev3_commands_active
    timeout = int(timeout)
    speed = int(speed)
    if not ev3_commands_active:
        logger.info("Commands are not active")
    elif timeout is None or speed is None:
        # TODO None handling hinzufügen
        logger.debug("param timeout or speed is None")
    else:
        if timeout > 15:
            timeout = 15
        elif timeout < 0:
            timeout = 0
        if speed < 0:
            speed = abs(speed)
        if speed > 100:
            speed = 100
        if speed > 0 and timeout > 0:
            pi_controller.add_request_to_queue("POST", dict(command="backwards", timeout=timeout, speed=speed))


async def rotate_for(degrees=None):
    """
    Führt Rotate Befehl aus
    :param degrees: Gradzahl wie weit sich EV3 drehen soll
    :return:
    """
    global ev3_commands_active
    if not ev3_commands_active:
        logger.info("Commands are not active")
    elif degrees is None:
        # TODO None handling hinzufügen
        logger.debug("param degrees is None")
    else:
        degrees = int(degrees)
        if degrees < 0:
            if (abs(degrees) / 360) > 1:
                degrees = abs(degrees) % 360 * -1
        else:
            if (degrees / 360) > 1:
                degrees = degrees % 360
        if degrees != 0:
            pi_controller.add_request_to_queue("POST", dict(command="rotate", degrees=degrees))


if __name__ == "__main__":
    pi_controller = PiController()
    ev3_commands_active = True

    logger = logging.getLogger('DISCORD BOT')
    logger.setLevel(level=logging.INFO)

    app.run()
