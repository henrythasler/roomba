settings = {
        "debug": 2, # 0=None, 1=Error, 2=Info, 3=Trace
        "roomba": {
            "host": "roomba.fritz.box",
            "port": 8883,
            "user": "1234",
            "pass": "1234",
            "ca": "/etc/ssl/certs/ca-certificates.crt",
            "enable_whitelist": False,      # Enable whitlisting via the "whitelist"-property below
            "whitelist": ["start", "stop"], # list of commands that the bridge is allowed to send to roomba
       },
        "upstream": {
            "host": "omv4.fritz.box",
            "port": 1883,
            "publish" : "home/roomba/state", # where to publish roomba topics to
            "subscribe" : "home/roomba/cmd",   # where to read roomba commands from
            "non_retain": ["pose", "signal"],   # these status messages will not be forwarded to the upstream broker as retained messages
        },
    }
