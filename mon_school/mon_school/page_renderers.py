"""Custom page renderers for Mon School.

The URLs that are handled here are:

/s/<sketch_id>.svg
/s/<sketch_id>-<hash>-s.png
/s/<sketch_id>-<hash>-w.png
"""
import frappe
import hashlib
import re
from pathlib import Path

import cairosvg
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response
from .doctype.lms_sketch.lms_sketch import DEFAULT_IMAGE

# This is refered from the hooks
page_renderer = [
	"mon_school.mon_school.page_renderers.SketchImage",
	"mon_school.mon_school.page_renderers.SketchPNG"
]

RE_SKETCH_IMAGE = re.compile(r"s/(\d+).(svg|png)$")

class SketchImage(BaseRenderer):
    """Class to render the sketch as SVG image for display and
    PNG image for twitter preview.
    """
    def can_render(self):
        return RE_SKETCH_IMAGE.match(self.path) is not None

    def render(self):
        m = RE_SKETCH_IMAGE.match(self.path)
        sketch_id = m.group(1)
        format = m.group(2)
        name = f"SKETCH-{sketch_id}"
        try:
            s = frappe.get_doc("LMS Sketch", name)
        except frappe.DoesNotExistError:
            s = None
            return Response("", status="404 Not Found")

        if format == "svg":
            return self.render_svg(s)
        elif format == "png":
            return self.render_png(s)
        else:
            return Response("", status="404 Not Found")

    def render_svg(self, sketch):
        svg = sketch.svg or DEFAULT_IMAGE
        return Response(svg, content_type="image/svg+xml")

    def render_png(self, sketch):
        headers = {"Location": f"{frappe.request.host_url}s/{sketch_id}-{sketch_hash}-{mode}.png"}
        return Response("", status="302 Found", headers=headers)

RE_SKETCH_SQUARE_IMAGE = re.compile(r"s/(.+)-([0-9a-f]+)-([smw]).png$")

class SketchPNG(BaseRenderer):
    """Class to render Sketch images as PNG.

    These images are for displaying the sketch in Recent Sketches page.
    The image name contains the sketch-id and hash of the code to allow
    it to be cached forever. Whenever the code of the sketch is changed,
    the url of of the image changes.

    This provides two versions of the image.
    1. square - with size 300x300
    2. wide - with size 550x300

    The square image is used to display images in recent sketches page
    and the wide image is used as preview image used in the meta tag.
    """
    IMAGE_SIZES_BY_MODE = {
        "s": (300, 300),
        "m": (600, 600),
        "w": (550, 300)
    }
    def can_render(self):
        return RE_SKETCH_SQUARE_IMAGE.match(self.path) is not None

    def get_sketch(self, sketch_id):
        if sketch_id.startswith("x"):
            doctype = "Contest Sketch"
            name = sketch_id.replace("x-", "")
        else:
            doctype = "LMS Sketch"
            name = "SKETCH-" + sketch_id
        try:
            print("doctype", doctype, name)
            return frappe.get_doc(doctype, name)
        except frappe.DoesNotExistError:
            pass

    def render(self):
        m = RE_SKETCH_SQUARE_IMAGE.match(self.path)
        sketch_id = m.group(1)
        hash_ = m.group(2)
        mode = m.group(3)
        name = f"SKETCH-{sketch_id}"

        filename = f"{sketch_id}-{hash_}-{mode}.png"

        sketch = self.get_sketch(sketch_id)
        if not sketch:
            return Response("", status="404 Not Found")

        sketch_hash = sketch.get_hash()
        if sketch_hash != hash_:
            headers = {"Location": f"{frappe.request.host_url}s/{sketch_id}-{sketch_hash}-{mode}.png"}
            return Response("", status="302 Found", headers=headers)

        return self.render_png(sketch, filename, mode)

    def to_png(self, sketch, filename, mode):
        cache_dir = Path(frappe.local.site_path) / "sketch-cache"
        cache_dir.mkdir(exist_ok=True)
        path = cache_dir / filename
        if path.exists():
            return path.read_bytes()

        svg = sketch.svg or DEFAULT_IMAGE
        w, h = self.IMAGE_SIZES_BY_MODE[mode]
        png = cairosvg.svg2png(svg, output_width=w, output_height=h)
        path.write_bytes(png)
        return png

    def render_png(self, sketch, filename, mode):
        png = self.to_png(sketch, filename, mode)

        # cache forever
        headers = {
            "Cache-Control": "public, max-age=31536000"
        }
        return Response(png, content_type="image/png", headers=headers)

