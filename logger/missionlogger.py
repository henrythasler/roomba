#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# basic packages
import time
import os
from datetime import datetime

# mqtt stuff
import paho.mqtt.client as mqtt

# global settings
from settings import settings

# misc utils
import json
import numpy as np

class MissionLogger(object):
    def __init__(self, settings):
        self.settings = settings

        # setup upstream mqtt stuff
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.roomba_active = False
        self.roomba_pos = None
        self.roomba_signal = None
        self.points = []
        self.values = []
        self.path = []
        self.heading = []

        self.client.connect(self.settings["broker"]["host"], port=self.settings["broker"]["port"])

        # use password authentication with broker
        if "user" in self.settings["broker"] and "pass" in self.settings["broker"]:
            self.client.username_pw_set(self.settings["broker"]["user"], self.settings["broker"]["pass"])    

        self.client.loop_start()

    def debug(self, message, level=2):
        if self.settings["debug"] >= level:
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
            self.debug(self.roomba_active,3)

            if msg.topic.startswith(self.settings["topics"]["pos"]) and self.roomba_active:
                self.debug(str(msg.topic) + ': ' + str(msg.payload), 3)
                data = json.loads(msg.payload)
                if "point" in data:
                    self.roomba_pos = data["point"]
                    self.path.append( [data["point"]["x"], data["point"]["y"]])
                if "theta" in data:
                    self.heading.append(data["theta"])

            if msg.topic.startswith(self.settings["topics"]["signal"]) and self.roomba_active:
                self.debug(str(msg.topic) + ': ' + str(msg.payload), 3)
                data = json.loads(msg.payload)
                if "rssi" in data and self.roomba_pos:
                    self.values.append(data["rssi"])
                    self.points.append( [self.roomba_pos["x"], self.roomba_pos["y"]] )

            if msg.topic.startswith(self.settings["topics"]["status"]):
                self.debug(str(msg.topic) + ': ' + str(msg.payload), 3)
                data = json.loads(msg.payload)
                if "phase" in data:
                    if self.roomba_active and (data["phase"] not in ["run", "hmPostMsn", "pause"]):
                        self.debug("Captured path with {} positions.".format(len(self.path)), 2)
                        temp_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                        np.savez(os.path.dirname(os.path.abspath(__file__))+"/"+temp_name+"_wifi.npz", points=self.points, values=self.values)
                        np.savez(os.path.dirname(os.path.abspath(__file__))+"/"+temp_name+"_path.npz", points=self.path, values=self.heading)

                        # delete captured data
                        del self.points[:]
                        del self.values[:]
                        del self.path[:]
                        del self.heading[:]

                    self.roomba_active = (data["phase"] in ["run", "hmPostMsn", "pause"])

    def loop(self):
        """main loop"""
        while True:
            time.sleep(1)


if __name__ == '__main__':
    
    bridge = MissionLogger(settings)
    try:
        bridge.loop()
    except (KeyboardInterrupt, SystemExit):
        pass
