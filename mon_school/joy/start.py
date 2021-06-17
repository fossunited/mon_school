
from joy import *

def show(*shapes):
    markers = [
        Rectangle(width=300, height=300, stroke="#ddd"),
        Line(start=Point(x=-150, y=0), end=Point(x=150, y=0), stroke="#ddd"),
        Line(start=Point(x=0, y=-150), end=Point(x=0, y=150), stroke="#ddd")
    ]
    for s in shapes:
        if not isinstance(s, Shape):
            print(f"Error: unable to show {s} as it is not a shape.")
    shapes = markers + [s for s in shapes if isinstance(s, Shape)]

    img = SVG(shapes)
    sendmsg("image", image=img.render())

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
