#!/usr/bin/env python3
import logging
import threading
from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
from time import sleep
import client

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('CONTROLLER')
logger.setLevel(logging.INFO)

commands_active = True
controller = None


class Controller:
    _response = None
    _command = None
    _request_queue = []
    _requesting_thread = None
    _response_received = False

    # Hier wird die Response des EV3 Servers angenommen
    def process_response(self, response):
        if response.get("methode") == "RESPONSE":
            logger.info("EV3 has received to command.")
            self._response_received = True

    # Fügt einen neue Request der Queue hinzu.
    def add_request_to_queue(self, methode, parameter):
        logger.info(f"Added {methode}, {parameter}")
        self._request_queue.append(dict(methode=methode, parameter=parameter))

    def start_requesting(self):
        logger.info("Monit Requests")
        while True:
            self._response_received = False
            if len(self._request_queue) > 0:
                _request = self._request_queue.pop(0)
                self._client.send_server_request(_request.get("methode"), _request.get("parameter"))
                sleep(1)
                while self._response_received is False:
                    sleep(1)

    @property
    def response(self):
        logger.debug("Response %s", self._response)
        return self._response

    def __init__(self):
        logger.info("Create Logger")

        self._client = client.Client(self)
        self._response_received = False
        self._requesting_thread = threading.Thread(
            target=self.start_requesting, args=(), daemon=True)
        self._requesting_thread.start()


def create_app():
    global controller

    app = Flask(__name__)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    with app.app_context():
        controller = Controller()

    return app


app = create_app()


@app.route('/forwards')
@cross_origin()
def move_forwards():
    global controller

    timeout = request.args.get("timeout")
    speed = request.args.get("speed")

    timeout = int(timeout)
    speed = int(speed)

    if not commands_active:
        logger.info("Commands are not active")
        return "Befehle sind gerade deaktiviert."
    elif timeout is None and speed is None:
        # TODO None handling hinzufügen
        logger.info("param timeout or speed is None")
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
            logger.info(f"{dict(command='forwards', timeout=timeout, speed=speed)}")
            controller.add_request_to_queue("POST", dict(command="forwards", timeout=timeout, speed=speed))
            return f"Fahre vorwärts {timeout} Sekunden lang mit einer Geschwindigkeit von {speed} %"


@app.route('/backwards')
@cross_origin()
def move_backwards():
    global controller

    timeout = request.args.get("timeout")
    speed = request.args.get("speed")

    timeout = int(timeout)
    speed = int(speed)

    if not commands_active:
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
            controller.add_request_to_queue("POST", dict(
                command="backwards", timeout=timeout, speed=speed))
            return "backwards"


@app.route("/turn")
@cross_origin()
def rotate_for():
    """
    Führt Rotate Befehl aus
    :param degrees: Gradzahl wie weit sich EV3 drehen soll
    :return:
    """
    global controller

    degrees = request.args.get("degrees")

    if not commands_active:
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
            controller.add_request_to_queue(
                "POST", dict(command="rotate", degrees=degrees))
            return 'Turn'


if __name__ == "__main__":
    app.run(port=5000)
