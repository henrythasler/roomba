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

import matplotlib.pyplot as plt
from scipy.interpolate import griddata


class data_linewidth_plot():
    """ from https://stackoverflow.com/questions/19394505/matplotlib-expand-the-line-with-specified-width-in-data-unit#42972469 """
    def __init__(self, x, y, **kwargs):
        self.ax = kwargs.pop("ax", plt.gca())
        self.fig = self.ax.get_figure()
        self.lw_data = kwargs.pop("linewidth", 1)
        self.lw = 1
        self.fig.canvas.draw()
        self.timer = None

        self.ppd = 72./self.fig.dpi
        self.trans = self.ax.transData.transform
        self.linehandle, = self.ax.plot([],[],**kwargs)
        if "label" in kwargs: kwargs.pop("label")
        self.line, = self.ax.plot(x, y, **kwargs)
        self.line.set_color(self.linehandle.get_color())
        self._resize()
        self.cid = self.fig.canvas.mpl_connect('draw_event', self._resize)

    def _resize(self, event=None):
        lw =  ((self.trans((1, self.lw_data))-self.trans((0, 0)))*self.ppd)[1]
        if lw != self.lw:
            self.line.set_linewidth(lw)
            self.lw = lw
            self._redraw_later()

    def _callback(self):
        #print(self.lw)
        self.fig.canvas.draw_idle()

    def _redraw_later(self):
        """ this is some strange workaround for updating the figure """
        if not self.timer:
            self.timer = self.fig.canvas.new_timer(interval=2000)
            self.timer.single_shot = False
            self.timer.add_callback(self._callback)
            self.timer.start()

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
                    if self.roomba_active and (data["phase"] not in ["run", "hmPostMsn"]):
                        self.debug("Captured path with {} positions.".format(len(self.path)), 2)

                        temp_name = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                        np.savez(temp_name+"_path.npz", points=self.path, values=self.heading)

                        # delete captured data
                        del self.path[:]
                        del self.heading[:]

                    self.roomba_active = (data["phase"] in ["run", "hmPostMsn"])

    def drawPath(self):
        points = np.array(self.path) * 11.8  # convert to mm
        values = np.array(self.heading)

        fig, ax = plt.subplots()

        # fixed aspect ratio
        ax.set_aspect('equal')
        fig.set_size_inches(8, 6)

        # set background colors
        fig.patch.set_facecolor('#065da2')
        ax.set_facecolor('#065da2')

        # setup grid
        ax.grid(which="both", linestyle="dotted", linewidth=2, alpha=.5, zorder=5)
        ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))

        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)

        # plot robot path with respect to width of vacuum unit (180mm)
        data_linewidth_plot(points[:,0], points[:,1], ax=ax, linewidth=180, alpha=.9, color="steelblue", solid_capstyle="round")

        # plot path and position samples
        plt.plot(points[:,0], points[:,1], '-', color="white", markersize=2, linewidth=1, alpha=.5)

        start_pos = plt.Circle((points[0,0], points[0,1]), 100, color='white', linewidth=2, alpha=.5, zorder=100)
        ax.add_artist(start_pos)

        final_pos = plt.Circle((points[-1,0], points[-1,1]), 100, color='lime', linewidth=2, alpha=.5, zorder=101)
        ax.add_artist(final_pos)

        fig.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')     # save as file (800x600)
        self.client.publish(self.settings["topics"]["livepath"], bytearray(buffer.getbuffer()), retain=True)
        buffer.close()
        plt.close('all')     

    def loop(self):
        """main loop"""
        while True:
            time.sleep(5)

            if self.roomba_active and len(self.path)>2:
                self.drawPath()


if __name__ == '__main__':
    
    bridge = MissionLogger(settings)
    try:
        bridge.loop()
    except (KeyboardInterrupt, SystemExit):
        pass
