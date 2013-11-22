"""
    Run:  ping google.com > ~/google.txt
"""

import re
import os.path

from collections import deque

from bokeh.plotting import *
from bokeh.plotting import line
from bokeh.objects import GlyphRenderer

MAX_HISTORY = 1000
output_server("ping")

def tail_generator(filename=os.path.expanduser("~/google.txt"), interval=0.5):
    """
    Reads file and then `tails` it -- checking at interval seconds
    Adapted from: http://code.activestate.com/recipes/157035-tail-f-in-python/
    """
    with open(filename, 'r') as f:
        while True:
            where = f.tell()
            line = f.readline()
            if not line:
                time.sleep(interval)
                f.seek(where)
            else:
                yield line

def parse_line(line):
    """Find sequence and rtt -- return as int, float or return None"""
    regex = re.compile(r'icmp_seq=(?P<seq>[0-9]+) .* time=(?P<time>[0-9.]+) ms')
    m = regex.search(line)
    if not m:
       return None
    return int(m.groupdict()["seq"]), float(m.groupdict()["time"])

# Use a deque to limit to 100 o entries
x_store = deque(maxlen=MAX_HISTORY)
y_store = deque(maxlen=MAX_HISTORY)

# Unfortuantely, deques can't be serialized -- change to np array
x = list(x_store)
y = list(y_store)
line(x,y, tools="", title = "Ping google.com")
xaxis()[0].axis_label = "Sequence Number"
yaxis()[0].axis_label = "RTT in ms"

save()

renderer = [r for r in curplot().renderers if isinstance(r, GlyphRenderer)][0]
ds = renderer.data_source

f = tail_generator()
for line_ in f:
    
    data = parse_line(line_)
    if data is None:
        continue
    
    # Deques will auto-drop old values
    x_store.append(data[0])
    y_store.append(data[1])
    
    ds.data["x"] = list(x_store)
    ds.data["y"] = list(y_store)
   
    ds._dirty = True
    session().store_obj(ds)
    time.sleep(.002)
