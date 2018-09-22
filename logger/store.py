import sys
import numpy as np
import psycopg2 as pg

if len(sys.argv) > 1:
    npzfile = np.load(sys.argv[1])

    points = npzfile["points"][:] * 11.8 / 1000 # convert to m
    heading = npzfile["values"][:]

    if len(points) > 20:
        with pg.connect("dbname='home' user='postgres' host='omv4' password='postgres'") as con:
            with con.cursor() as cur:
                translator = str.maketrans('[]','()')
                path = np.array2string(points, precision=3, separator=',', suppress_small=True)[1:-1]
                path = "["+path.translate(translator)+"]"  # must look like this: '[(11,54), (31,32), (0,0)]'
                cur.execute("INSERT INTO public.roombapath (heading, path) VALUES(%s, popen(path %s))", (heading.tolist(), path))
                print("done")
    else:
        print("Path too short.")
