#!/usr/bin/env python3
import socket
import traceback
import logging
import sys
import selectors
import json
import io
import struct
from ev3_control import EV3Controller

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('EV3 SERVER')
logger.setLevel(logging.DEBUG)


class EV3ControlServer:
    sel = selectors.DefaultSelector()
    settings = None
    lsock = None

    def _accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        logger.info("Server accepted connection from %s", addr)
        conn.setblocking(False)
        message = Message(self.sel, conn, addr, self.ev3_controller)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def start_server(self):
        logger.info("Starting server...")
        host, port = self.settings["host-ip"], int(self.settings["host-port"])
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((host, port))
        self.lsock.listen()
        logger.info("Server is listening on %s", (host, port))
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self._accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            logger.error("main: error: exception for %s: \n%s", message.addr, traceback.format_exc())
                            message.close()
        except KeyboardInterrupt:
            logger.error("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

    def __init__(self, ev3_controller):
        self.ev3_controller = ev3_controller

        with open("settings.json") as file:
            self.settings = json.load(file)

        logger.info("Server created.")


class Message:

    def __init__(self, selector, sock, addr, ev3_controller):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.ev3_controller = ev3_controller

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            logger.error("ValueError: Invalid events mask mode.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                logger.debug("Data received")
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            logger.info("Sending response to %s", self.addr)
            logger.debug("Sending %s to %s", repr(self._send_buffer), self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                logger.error("Resource unavailable")
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
            self, *, content_bytes, content_type, content_encoding
    ):
        # INFO Hier wird die erstellt Response in das Messageformat convertiert: Header(2bytes) + jsonheader + content
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        content_encoding = "utf-8"
        content = self.ev3_controller.response
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    # Response wird dann an control.py weitergeben
    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    # Hier wird die Response erstellt
    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        logger.info("Closing connection to %s", self.addr)
        print()
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logger.error("error: selector.unregister() exception for %s: %s", self.addr, repr(e))

        try:
            self.sock.close()
        except OSError as e:
            logger.error("error: socket.close() exception for %s: %s", self.addr, repr(e))
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                    "byteorder",
                    "content-length",
                    "content-type",
                    "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    logger.error("ValueError: Missing required header")

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            logger.error("Content length to long. Content not processed")
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            logger.info("Received request %s - %s from %s", repr(self.request.get("methode")),
                        repr(self.request.get("parameter")), self.addr)
            self.ev3_controller.process_request(self.request)
        else:
            # Binary or unknown content-type
            logging.error("Server only accepts JSON")
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        response = self._create_response_json_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message
