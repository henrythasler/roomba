# roomba

This is about using the iRobot roomba 960 vacuum cleaner unit in your own MQTT-based home automation solution.

## installing dependencies

```
sudo apt install python3-pip python3-setuptools python3-tk
pip3 install paho-mqtt matplotlib scipy scikit-image
```

## python3 modules

### bridge

Provides a convenient way of 2-way mirroring the mqtt states and commands from the robot unit to your local mqtt broker.

#### Setup

1. Install the mqtt module for root: `sudo pip3 install paho-mqtt`
2. modify bridge/settings.py according to your needs. Especially the `host`, `user` and `pass` settings.
3. modify `bridge/bridge.service` according to your needs.
4. copy service file to sysdemd-folder: `sudo cp bridge.service /etc/systemd/system/`
5. start service `sudo systemctl start bridge`

If encountering errors during startup, check logs with `sudo journalctl -u bridge`

### visuals/livepath

Read mission data from your local MQTT broker and return a livemap that updates every few seconds. You need to set-up the bridge component first.
![Live Map](docs/livemap1.png)

### dockerfile

Make sure you specify your local dns-resolver/wifi-router if you refer to domain names in your home network:
```
docker run --rm -ti --dns 192.168.1.1 -v /home/henry/dev/roomba:/roomba img-roomba:0.3 python3 /roomba/visuals/livepath.py
sudo docker run -d --restart=always --name livepath -v /home/henry/dev:/home/henry/dev --dns 192.168.178.1 192.168.178.27:5000/roomba-python python3 /home/henry/dev/roomba/visuals/livepath.py
```

push to local registry
```
docker tag img-roomba:0.3 localhost:5000/img-roomba:0.3
docker push localhost:5000/img-roomba:0.3
```

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
`start` | starts 2-pass cleaning mission (see also `clean`)
`clean` | start 2-pass cleaning mission (difference to `start` is yet unknown)
`quick` | start qick (1-pass) cleaning mission
`stop` | stop (abort) current mission
`pause` | pause current mission. Send `stop` to cancel the mission, before initiating another mission.
`resume` | resume current mission
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
* http://www.scipy-lectures.org/packages/scikit-image/index.html
* https://icaci.org/files/documents/ICC_proceedings/ICC2009/html/refer/19_2.pdf
* https://www.researchgate.net/publication/228846264_Field_deformation_in_an_agent-based_generalisation_model_The_GAEL_model



