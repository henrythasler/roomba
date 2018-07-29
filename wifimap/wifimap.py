#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

# mqtt stuff
import paho.mqtt.client as mqtt

# global settings
from settings import settings

import json

import numpy as np

# pip3 install matplotlib
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from scipy.interpolate import griddata


class WifiMap(object):
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
            #print(self.roomba_active)

            if msg.topic.startswith(self.settings["topics"]["pos"]) and self.roomba_active:
                self.debug(str(msg.topic) + ': ' + str(msg.payload))
                data = json.loads(msg.payload)
                if "point" in data:
                    self.roomba_pos = data["point"]
                    self.path.append( [data["point"]["x"], data["point"]["y"]])
                if "theta" in data:
                    self.heading.append(data["theta"])

            if msg.topic.startswith(self.settings["topics"]["signal"]) and self.roomba_active:
                self.debug(str(msg.topic) + ': ' + str(msg.payload))
                data = json.loads(msg.payload)
                if "rssi" in data and self.roomba_pos:
                    self.values.append(data["rssi"])
                    self.points.append( [self.roomba_pos["x"], self.roomba_pos["y"]] )

            if msg.topic.startswith(self.settings["topics"]["status"]):
                self.debug(str(msg.topic) + ': ' + str(msg.payload))
                data = json.loads(msg.payload)
                if "phase" in data:
                    if self.roomba_active and data["phase"] == "stop":
                        print("Captured values: ", len(self.points))
                        if len(self.points) >= 4:
                            
                            self.points = np.array(self.points)
                            minx=np.amin(self.points, axis=0)[0]
                            maxx=np.amax(self.points, axis=0)[0]

                            miny=np.amin(self.points, axis=0)[1]
                            maxy=np.amax(self.points, axis=0)[1]

                            grid_x, grid_y = np.mgrid[minx:maxx:100j, miny:maxy:100j]
                            raw = griddata(self.points, self.values, (grid_x, grid_y), method='linear')

                            #im = plt.imshow(raw, interpolation='lanczos', vmax=abs(raw).max(), vmin=-abs(raw).max())
                            plt.imshow(raw.T, origin='lower', extent=(minx,maxx,miny,maxy))
                            plt.plot(self.points[:,0], self.points[:,1], 'k.', ms=5)

                            #plt.show()
                            plt.savefig("wifimap.png", dpi=150)     # save as file (800x600)
                            plt.close('all')     

                            np.savez("wifimap.npz", points=self.points, values=self.values)
                            np.savez("path.npz", points=self.path, values=self.heading)

                    self.roomba_active = (data["phase"] == "run") or (data["phase"] == "hmPostMsn")

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
