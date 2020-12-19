""" Implementation of a SlippiComm client aka 'Slippstream'
                                                    (I'm calling it that)
This can be used to talk to some server implementing the Slippstream protocol
(i.e. the Project Slippi fork of Nintendont or Slippi Ishiiruka).
"""
#adapted from altf4's libmelee project https://github.com/altf4/libmelee
import socket
from enum import Enum
import enet
import json

# pylint: disable=too-few-public-methods
class EventType(Enum):
    """ Replay event types """
    GECKO_CODES = 0x10
    PAYLOADS = 0x35
    GAME_START = 0x36
    PRE_FRAME = 0x37
    POST_FRAME = 0x38
    GAME_END = 0x39
    FRAME_START = 0x3a
    ITEM_UPDATE = 0x3b
    FRAME_BOOKEND = 0x3c

class CommType(Enum):
    """ Types of SlippiComm messages """
    HANDSHAKE = 0x01
    REPLAY = 0x02
    KEEPALIVE = 0x03
    MENU = 0x04

class SlippstreamClient():
    """ Container representing a client to some SlippiComm server """

    def __init__(self, address="127.0.0.1", port=51441, realtime=True):
        """ Constructor for this object """
        self._host = enet.Host(None, 1, 0, 0)
        self._peer = None
        self.buf = bytearray()
        self.realtime = realtime
        self.address = address
        self.port = port

    def shutdown(self):
        """ Close down the socket and connection to the console """
        if self._peer:
            self._peer.send(0, enet.Packet())
            self._host.service(100)
            self._peer.disconnect()
            self._peer = None

        if self._host:
            self._host = None
        return False

    def dispatch(self):
        """Dispatch messages with the peer (read and write packets)"""
        event = None
        event_type = 1000
        while event_type not in [enet.EVENT_TYPE_RECEIVE]:
            wait_time = 1000
            try:
                event = self._host.service(timeout = wait_time)
                event_type = event.type
            except OSError:
                print("OSError! Reconnecting...")
                self.connect()
                continue

            if event.type == enet.EVENT_TYPE_NONE:
                return None
                #print("none event recieved")
            if event.type == enet.EVENT_TYPE_RECEIVE:
                try:
                    return json.loads(event.packet.data)
                except json.JSONDecodeError:
                    # This happens at the end of a game for some reason?
                    if len(event.packet.data) == 0:
                        event_type = 0
                        continue
                    return None
            elif event.type == enet.EVENT_TYPE_CONNECT:
                print("recieved connect in dispatch")
                #handshake = json.dumps({
                #    "type" : "connect_request",
                #    "cursor" : 0,
                #})
                #self._peer.send(0, enet.Packet(handshake.encode()))
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                print("Disconnect event receieved")
                return None
        return None

    def connect(self):
        """ Connect to the server
        Returns True on success, False on failure
        """
        # Try to connect to the server and send a handshake
        try:
            self._peer = self._host.connect(enet.Address(bytes(self.address, 'utf-8'), int(self.port)), 1)
        except OSError: #this should mean that we're already connected
            pass #shouldn't happen unless something is wrong
        try:
            event = None
            attempts = 0
            maxAttempts = 4 #only attempt to connect 4 times
            while True:
                event = self._host.service(1000)
                if event.type == enet.EVENT_TYPE_CONNECT: #this means we've connected
                    break
                attempts = attempts + 1
                if attempts > maxAttempts:
                    return False
            handshake = json.dumps({
                        "type" : "connect_request",
                        "cursor" : 0,
                    })
            self._peer.send(0, enet.Packet(handshake.encode()))
            return True
        except OSError: #shouldn't happen unless something is wrong
            return False