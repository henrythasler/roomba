#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# basic packages
import io
import time
from datetime import datetime

# mqtt stuff
import paho.mqtt.client as mqtt

# global settings
from settings import settings

# misc utils
import json
import numpy as np

# chart library
import matplotlib
# Force matplotlib to NOT use any Xwindows backend.
matplotlib.use('Agg')

from matplotlib import ticker, pyplot as plt
from scipy.interpolate import griddata

# width of vacuum opening
ROOMBA_WIDTH = 180

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

            if msg.topic.startswith(self.settings["topics"]["status"]):
                self.debug(str(msg.topic) + ': ' + str(msg.payload), 3)
                data = json.loads(msg.payload)
                if "phase" in data:
                    if self.roomba_active and (data["phase"] not in ["run", "hmPostMsn", "pause"]):
                        self.debug("Captured path with {} positions.".format(len(self.path)), 2)

                        # delete captured data
                        del self.path[:]
                        del self.heading[:]

                    self.roomba_active = (data["phase"] in ["run", "hmPostMsn", "pause"])

    def drawPath(self):
        points = np.array(self.path) * 11.8  # convert to mm
        values = np.array(self.heading)

        minx=np.amin(points, axis=0)[0]
        maxx=np.amax(points, axis=0)[0]

        miny=np.amin(points, axis=0)[1]
        maxy=np.amax(points, axis=0)[1]

        fig = plt.figure(figsize=(10,8), dpi=100)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        fig.add_axes(ax)    

        ax.set_aspect('equal')

        ax.set_xlim(minx-ROOMBA_WIDTH, maxx+ROOMBA_WIDTH)
        ax.set_ylim(miny-ROOMBA_WIDTH, maxy+ROOMBA_WIDTH)

        # set background colors
        fig.patch.set_facecolor('#065da2')
        ax.set_facecolor('#065da2')

        # setup grid
        ax.grid(which="both", linestyle="dotted", linewidth=1, alpha=.5, zorder=5)

        # spacing 0.5m
        ax.xaxis.set_major_locator(ticker.MultipleLocator(500))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(500))

        # all off
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)

        # call this before any transformations. reason is unknown
        fig.canvas.draw()   

        lw = ((ax.transData.transform((1, ROOMBA_WIDTH))-ax.transData.transform((0, 0)))*(72./fig.dpi))[1]
        plt.plot(points[:,0], points[:,1], '-', color="steelblue", linewidth=lw, alpha=.9, solid_capstyle="butt")

        # plot path (and position samples)
        plt.plot(points[:,0], points[:,1], '-', color="white", markersize=2, linewidth=.75, alpha=.5)

        # plot start and end position 
        start_pos = plt.Circle((points[0,0], points[0,1]), 100, color='white', linewidth=2, alpha=.5, zorder=100)
        ax.add_artist(start_pos)

        final_pos = plt.Circle((points[-1,0], points[-1,1]), 100, color='lime', linewidth=2, alpha=.5, zorder=101)
        ax.add_artist(final_pos)

        # use in-memory file to save plot
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')     # save as file (800x600)
        self.client.publish(self.settings["topics"]["livepath"], bytearray(buffer.getbuffer()), retain=True)
        buffer.close()
        plt.close('all')     

    def loop(self):
        """main loop"""
        while True:
            time.sleep(5)

            # update livepath
            if self.roomba_active and len(self.path)>2:
                self.drawPath()


if __name__ == '__main__':
    
    bridge = MissionLogger(settings)
    try:
        bridge.loop()
    except (KeyboardInterrupt, SystemExit):
        pass
