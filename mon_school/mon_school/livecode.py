"""Interaction with livecode.
"""
from __future__ import annotations
import frappe
import json
from urllib.parse import urlparse
import websocket
from ..joy.build import get_livecode_files

@frappe.whitelist(allow_guest=True)
def execute(code: str, is_sketch=False) -> LiveCodeResult:
    """Executes the code and returns the output.

    The return value will be of the following format:

    {
        "status": "success",
        "output": [
            "1\n",
            "2\n"
        ],
        "shapes": [
            {"tag": "circle", "cx": 0, "cy": 0, "r": 50, "fill": "red"},
            {"tag": "rect", "x": -50, "y": 50, "width": 50, "height": 50, "fill": "red"}
        ]
    }
    """
    livecode_url = frappe.get_cached_doc("LMS Settings").livecode_url
    livecode = LiveCode(livecode_url)
    result = livecode.execute(code, is_sketch=is_sketch)
    return result.as_dict()

class LiveCodeResult:
    def __init__(self):
        self.status = "success"
        self.error_code = None
        self.output = []
        self.shapes = []

    def mark_failed(self, error_code):
        self.status = "failed"
        self.error_code = error_code

    def add_output(self, output):
        self.output.append(output)

    def add_shape(self, shape):
        self.shapes.append(shape)

    def as_dict(self):
        return dict(self.__dict__)

    def _render_shape(self, shape):
        tag = shape

    def as_svg(self):
        return (
            '<svg width="300" height="300" viewBox="-150 -150 300 300" fill="none" stroke="black" xmlns="http://www.w3.org/2000/svg">\n'
            + "\n".join(self._render_shape(s) for s in self.shapes)
            + '\n'
            + '</svg>\n')

class LiveCode:
    def __init__(self, livecode_url, timeout=3):
        self.livecode_url = livecode_url
        self.timeout = timeout

    def get_livecode_ws_url(self):
        url = urlparse(self.livecode_url)
        protocol = "wss" if url.scheme == "https" else "ws"
        return protocol + "://" + url.netloc + "/livecode"

    def execute(self, code, is_sketch=False):
        result = LiveCodeResult()
        try:
            ws = self.get_websocket()
        except (IOError, websocket.WebSocketException):
            result.mark_failed("connection-failed")
            return result

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
        try:
            ws.send(json.dumps(msg))
            messages = self._read_messages(ws)

            for m in messages:
                if m['msgtype'] == 'write':
                    result.add_output(m['data'])
                elif m['msgtype'] == 'shape':
                    result.add_shape(m['shape'])
        except (IOError, websocket.WebSocketException):
            result.mark_failed('connection-reset')

        return result

    def get_websocket(self):
        ws = websocket.WebSocket()
        ws.settimeout(self.timeout)
        livecode_ws_url = self.get_livecode_ws_url()
        ws.connect(livecode_ws_url)
        return ws

    def _read_messages(self, ws):
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