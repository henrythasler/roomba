settings = {
        "debug": 2, # 0=None, 1=Error, 2=Info, 3=Trace
        "broker": {
            "host": "osmc",
            "port": 1883,
        },
        "topics": {
            "pos": "home/roomba/state/pose",
            "signal": "home/roomba/state/signal",
            "status": "home/roomba/state/cleanMissionStatus",
            "livepath": "home/roomba/state/livepath",
        },
    }