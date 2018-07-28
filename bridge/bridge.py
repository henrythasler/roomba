#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
import ssl

import json
import pprint
import csv

from settings import settings


class RoombaBridge(object):
    def __init__(self, settings):
        self.settings = settings

        # setup roomba mqtt stuff
        self.client = mqtt.Client(
                client_id=self.settings["roomba"]["user"], 
                clean_session=True,
                protocol=mqtt.MQTTv311
            )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.client.tls_set(
                ca_certs="/etc/ssl/certs/ca-certificates.crt", 
                cert_reqs=ssl.CERT_NONE,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
        
        self.client.tls_insecure_set(True)
        self.client.username_pw_set(self.settings["roomba"]["user"], self.settings["roomba"]["pass"])    

        self.client.connect(self.settings["roomba"]["host"], port=self.settings["roomba"]["port"])
        self.client.loop_start()

        # setup upstream mqtt stuff
        self.upstream = mqtt.Client()
        self.upstream.on_connect = self.on_connect

        self.upstream.connect(self.settings["upstream"]["host"], port=self.settings["upstream"]["port"])
        self.upstream.loop_start()

    def debug(self, message):
        if self.settings["debug"]:
          try:
            print(datetime.now().strftime("%H:%M:%S") + ' ' + str(message))
          except:
            pass

    def on_connect(self, client, userdata, flags, rc):
        """The callback for when the client receives a CONNACK response from the server."""
        if id(client) == id(self.client):
            self.debug("Connected to Roomba mqtt broker with result code "+str(rc))
        elif id(client) == id(self.upstream):
            self.debug("Connected to upstream mqtt broker with result code "+str(rc))

        client.subscribe("#")

    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        if id(client) == id(self.client): 
            data = json.loads(msg.payload)
            if msg.topic.startswith('wifistat') or msg.topic.startswith('$aws/things'):
                if "state" in data:
                    if "reported" in data["state"]:
                        for key, value in data["state"]["reported"].items():
                            self.upstream.publish("home/roomba/"+str(key), json.dumps(value))
                    else:
                        self.debug(str(msg.topic) + ': ' + str(msg.payload))
                else:
                    self.debug(str(msg.topic) + ': ' + str(msg.payload))
            else:
                self.debug(str(msg.topic) + ': ' + str(msg.payload))

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
