import frappe
import hashlib
from community.lms.doctype.lms_sketch.lms_sketch import LMSSketch, DEFAULT_IMAGE
import websocket
import json
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
            ws_url = self.get_livecode_ws_url()
            value = livecode_to_svg(ws_url, self.code)
            if value:
                cache.set(key, value)
        return value or DEFAULT_IMAGE

def livecode_to_svg(livecode_ws_url, code, *, timeout=3):
    """Renders the code as svg.
    """
    try:
        ws = websocket.WebSocket()
        ws.settimeout(timeout)
        ws.connect(livecode_ws_url)

        msg = {
            "msgtype": "exec",
            "runtime": "python",
            "code": code,
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
            print("MSG", msg)
            messages.append(json.loads(msg))
    except websocket.WebSocketTimeoutException as e:
        print("Error:", e)
        pass
    return messages
