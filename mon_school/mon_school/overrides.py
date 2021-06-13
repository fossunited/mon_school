import frappe
import hashlib
from community.lms.doctype.lms_sketch.lms_sketch import LMSSketch, DEFAULT_IMAGE
from community.lms.doctype.exercise.exercise import Exercise as _Exercise
import websocket
import json
from urllib.parse import urlparse
from ..joy.build import get_livecode_files

class Sketch(LMSSketch):
    def render_svg(self):
        h = hashlib.md5(self.code.encode('utf-8')).hexdigest()
        cache = frappe.cache()
        key = "sketch-" + h
        value = cache.get(key)
        if value:
            value = value.decode('utf-8')
        else:
            is_sketch = self.runtime == "sketch" # old version
            value = livecode_to_svg(self.code, is_sketch=is_sketch)
            if value:
                cache.set(key, value)
        return value or DEFAULT_IMAGE

class Exercise(_Exercise):
    def before_save(self):
        self.image = livecode_to_svg(self.answer)

def get_livecode_url():
    doc = frappe.get_cached_doc("LMS Settings")
    return doc.livecode_url

def get_livecode_ws_url():
    url = urlparse(get_livecode_url())
    protocol = "wss" if url.scheme == "https" else "ws"
    return protocol + "://" + url.netloc + "/livecode"

def livecode_to_svg(code, *, timeout=3, is_sketch=False):
    """Renders the code as svg.
    """
    try:
        ws = websocket.WebSocket()
        ws.settimeout(timeout)
        livecode_ws_url = get_livecode_ws_url()
        ws.connect(livecode_ws_url)

        env = {}
        if is_sketch:
            env['SKETCH'] = "yes"

        msg = {
            "msgtype": "exec",
            "runtime": "python",
            "code": code,
            "env": env,
            "files": get_livecode_files(),
            "command": ["python", "start.py"]
        }
        ws.send(json.dumps(msg))

        messages = _read_messages(ws)
        commands = [m for m in messages if m['msgtype'] == 'image']
        if commands:
            return commands[0]['image']
        else:
            return ""
    except websocket.WebSocketException as e:
        frappe.log_error(frappe.get_traceback(), 'livecode_to_svg failed')

def _read_messages(ws):
    messages = []
    try:
        while True:
            msg = ws.recv()
            if not msg:
                break
            messages.append(json.loads(msg))
    except websocket.WebSocketTimeoutException as e:
        print("Error:", e)
        pass
    return messages
