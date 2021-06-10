
from joy import *

def show(*shapes):
    markers = [
        Rectangle(width=300, height=300, stroke="#ddd"),
        Line(start=Point(x=-150, y=0), end=Point(x=150, y=0), stroke="#ddd"),
        Line(start=Point(x=0, y=-150), end=Point(x=0, y=150), stroke="#ddd")
    ]
    shapes = markers + list(shapes)
    img = SVG(shapes)
    sendmsg("image", image=img.render())

env = dict(globals())

import json
def sendmsg(msgtype, **kwargs):
  """Sends a message to the frontend.

  The frontend will receive the specified message whenever
  this function is called. The frontend can decide to some
  action on each of these messages.
  """
  msg = dict(msgtype=msgtype, **kwargs)
  print("--MSG--", json.dumps(msg))

code = open("main.py").read()
exec(code, env)
