#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
import ssl

import json

from settings import settings

class RoombaBridge(object):
    """ Bridge topics from the roomba broker to any MQTT broker 
    The roomba uses a certificate signed by some "ROOMBA CA". This root CA is not publicly available afaik.
    To connect to the roomba broker via TLS w/o checking the certificate we MUST set
        cert_reqs=ssl.CERT_NONE
    """
    def __init__(self, settings):
        self.settings = settings

        # setup roomba mqtt stuff
        self.roomba = mqtt.Client(
                client_id=self.settings["roomba"]["user"], 
                clean_session=True,
                protocol=mqtt.MQTTv311
            )
        self.roomba.on_connect = self.on_connect
        self.roomba.on_message = self.on_message
        
        self.roomba.tls_set(
                ca_certs=self.settings["roomba"]["ca"], 
                cert_reqs=ssl.CERT_NONE,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
        
        self.roomba.tls_insecure_set(True)
        self.roomba.username_pw_set(self.settings["roomba"]["user"], self.settings["roomba"]["pass"])    

        self.roomba.connect(self.settings["roomba"]["host"], port=self.settings["roomba"]["port"])
        self.roomba.loop_start()

        # setup upstream mqtt stuff
        self.upstream = mqtt.Client()
        self.upstream.on_connect = self.on_connect
        self.upstream.on_message = self.on_message

        self.upstream.connect(self.settings["upstream"]["host"], port=self.settings["upstream"]["port"])
        self.upstream.loop_start()

    def debug(self, message, level=2):
        if self.settings["debug"] >= level:
          try:
            print(datetime.now().strftime("%H:%M:%S") + ' ' + str(message))
          except:
            pass

    def on_connect(self, client, userdata, flags, rc):
        """The callback for when the client receives a CONNACK response from the server."""
        if id(client) == id(self.roomba):
            self.debug("Connected to roomba mqtt broker with result code "+str(rc))
            client.subscribe("#")

        elif id(client) == id(self.upstream):
            self.debug("Connected to upstream mqtt broker with result code "+str(rc))
            client.subscribe(self.settings["upstream"]["subscribe"])

    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        if id(client) == id(self.roomba): 
            # forward message from roomba to upstream broker
            self.debug("msg from roomba - " + str(msg.topic) + ': ' + str(msg.payload), 3)
            data = json.loads(msg.payload)
            if msg.topic.startswith('wifistat') or msg.topic.startswith('$aws/things'):
                if "state" in data:
                    if "reported" in data["state"]:
                        for key, value in data["state"]["reported"].items():
                            retain = True
                            # disable message retain for specific topics
                            if key in self.settings["upstream"]["non_retain"]:
                                retain = False
                            self.upstream.publish(self.settings["upstream"]["publish"]+"/"+str(key), json.dumps(value), retain=retain)
                    else:
                        self.debug(str(msg.topic) + ': ' + str(msg.payload))
                else:
                    self.debug(str(msg.topic) + ': ' + str(msg.payload))
            else:
                self.debug(str(msg.topic) + ': ' + str(msg.payload))
        elif id(client) == id(self.upstream):
            # forward commands from upstream broker to roomba
            self.debug("msg from upstream - " + str(msg.topic) + ': ' + str(msg.payload), 2)
            
            cmd = msg.payload.decode("utf-8")
            if ( self.settings["roomba"]["enable_whitelist"] == True and cmd in self.settings["roomba"]["whitelist"] ) or self.settings["roomba"]["enable_whitelist"] == False:
                payload = {
                    "command": cmd,
                    "time" : int(datetime.utcnow().timestamp()),
                    "initiator": "localApp",
                }
                self.debug("sending to roomba:" + json.dumps(payload), 3)
                self.roomba.publish("cmd", json.dumps(payload))                
            else:
                self.debug("command blocked by whitelist - " + cmd, 1)

    def loop(self):
        """main loop"""
        while True:
            time.sleep(1)


if __name__ == '__main__':
    
    bridge = RoombaBridge(settings)
    try:
        bridge.loop()
    except (KeyboardInterrupt, SystemExit):
        pass
