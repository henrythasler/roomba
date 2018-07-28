#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

# mqtt stuff
import paho.mqtt.client as mqtt

# global settings
from settings import settings

import json

# pip3 install matplotlib
import matplotlib

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects


class WifiMap(object):
    def __init__(self, settings):
        self.settings = settings

        # setup upstream mqtt stuff
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.settings["broker"]["host"], port=self.settings["broker"]["port"])

        # use password authentication with broker
        if "user" in self.settings["broker"] and "pass" in self.settings["broker"]:
            self.client.username_pw_set(self.settings["broker"]["user"], self.settings["broker"]["pass"])    

        self.client.loop_start()

    def debug(self, message):
        if self.settings["debug"]:
          try:
            print(datetime.now().strftime("%H:%M:%S") + ' ' + str(message))
          except:
            pass

    def on_connect(self, client, userdata, flags, rc):
        """The callback for when the client receives a CONNACK response from the server."""
        if id(client) == id(self.client):
            self.debug("Connected to mqtt broker with result code "+str(rc))

        # subscribe to relevant topics 
        client.subscribe(self.settings["topics"]["pos"])    # position 
        client.subscribe(self.settings["topics"]["signal"])  # wifi-signal
        client.subscribe(self.settings["topics"]["status"])  # cleaning status

    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        if id(client) == id(self.client): 
            if msg.topic.startswith(self.settings["topics"]["pos"]):
                data = json.loads(msg.payload)


    def loop(self):
        """main loop"""
        while True:
            time.sleep(1)


if __name__ == '__main__':
    
    bridge = WifiMap(settings)
    try:
        bridge.loop()
    except (KeyboardInterrupt, SystemExit):
        pass
