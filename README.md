# roomba

This is about using the iRobot roomba 960 vacuum cleaner unit in your own MQTT-based home automation solution.

## installing dependencies

```
sudo apt install python3-pip python3-setuptools
pip3 install paho-mqtt matplotpy scipy
```

## modules

### bridge

Provides a convenient way of 2-way mirroring the mqtt states and commands from the robot unit to your local mqtt broker.

#### Setup

1. Install the mqtt module for root: `sudo pip3 install paho-mqtt`
2. modify bridge/settings.py according to your needs. Especially the `host`, `user` and `pass` settings.
3. modify `bridge/bridge.service` according to your needs.
4. copy service file to sysdemd-folder: `sudo cp bridge.service /etc/systemd/system/`
5. start service `sudo systemctl start bridge`

If encountering errors during startup, check logs with `sudo journalctl -u bridge`

## Unit measurements

\# | robot-units (x) | distance [mm] | factor
---|---|--|--
1 | 135 | 1600 | 11.85 
2 | 137 | 1620 | 11.82
3 | 137 | 1650 | 12.04
4 | 345 | 4050 | 11.74
5 | 350 | 4040 | 11.54

=> 1 robot-unit = 11.8 mm

## Command description

Command | Description
---|---
`start` | starts cleaning (see also `start`)
`clean` | start cleaning cycle (difference to `start` is yet unknown)
`stop` | stop cleaning
`pause` | pause mission
`resume` | resume mission
`dock` | Initiates the docking sequence. Same as pressing the `home` button.
`fbeep` * | emit a single beep
`find` * | Continuous emission of beeping sounds (to locate robot unit). Send `find` command again or press the `clean` button to turn off.
`off` | turn off robot unit. This will also interrupt any connections and disable wifi. Press the `clean` button on the robot unit to turn on again.
`sleep` | put robot unit into standby/sleep mode. Wifi connection will remain active and robot unit wakes up when receiving a command.
`wake` * | wakes the robot unit from standby/sleep mode. The `clean` button will flash several times.

*) does not work while the robot unit is charging at the dock

There are some other commands available (see https://github.com/koalazak/dorita980/issues/39) but I didn't dare to try them out.

## references
* https://github.com/koalazak/dorita980
* https://github.com/NickWaterton/Roomba980-Python
* https://www.hivemq.com/blog/seven-best-mqtt-client-tools
* https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files


