
from joy import *

def show_bg():
    def hline(y, **kwargs):
        return line(x1=-150, y1=y, x2=150, y2=y, stroke="#ddd", **kwargs)

    def vline(x, **kwargs):
        return line(x1=x, y1=-150, x2=x, y2=150, stroke="#ddd", **kwargs)

    markers = [
        hline(50), hline(100), hline(150),
        hline(-50), hline(-100), hline(-150),
        vline(50), vline(100), vline(150),
        vline(-50), vline(-100), vline(-150),
        hline(0, stroke_width=2), vline(0, stroke_width=2)
    ]
    shape = Group(markers)
    sendmsg("shape", shape=shape.as_dict())

BG_SHOWN = False

def show(*shapes):
    global BG_SHOWN
    if not BG_SHOWN:
        show_bg()
        BG_SHOWN = True

    for s in shapes:
        if not isinstance(s, Shape):
            print(f"show: {s} is not a shape")

    shapes = [s for s in shapes if isinstance(s, Shape)]
    shape = Group(shapes) | Scale(sx=1, sy=-1)
    sendmsg("shape", shape=shape.as_dict())

env = dict(globals())

import os
import json
def sendmsg(msgtype, **kwargs):
  """Sends a message to the frontend.

  The frontend will receive the specified message whenever
  this function is called. The frontend can decide to some
  action on each of these messages.
  """
  msg = dict(msgtype=msgtype, **kwargs)
  print("--MSG--", json.dumps(msg))

# legacy mode: support legacy sketches
is_sketch = os.getenv("SKETCH")
if is_sketch:
    exec("from sketch import circle, get_shape", env)

code = open("main.py").read()
exec(code, env)

# legacy mode: draw the shapes created so far
if is_sketch:
    exec("show(get_shape())", env)
