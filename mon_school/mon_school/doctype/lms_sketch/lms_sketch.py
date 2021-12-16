# -*- coding: utf-8 -*-
# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
import cairosvg
import frappe
import tempfile
import os
from frappe.model.document import Document
from ... import livecode

DEFAULT_IMAGE = """
<svg viewBox="0 0 300 300" width="300" xmlns="http://www.w3.org/2000/svg">
</svg>
"""
IMAGE_NOT_READY_URL = "/assets/mon_school/images/image-not-ready.png"

class LMSSketch(Document):
    IMAGE_SIZES_BY_MODE = {
        "s": (300, 300),
        "m": (600, 600),
        "w": (550, 300)
    }

    def before_save(self):
        if getattr(self, "_skip_before_save", None):
            return
        try:
            is_sketch = self.runtime == "sketch" # old version
            self.svg = livecode.livecode_to_svg(self.code, is_sketch=is_sketch)
            self.image_ready = False
        except Exception:
            frappe.log_error(f"Failed to save svg for sketch {self.name}")

    def after_insert(self):
        self.on_update()

    def on_update(self):
        if getattr(self, "_skip_before_save", None):
            return
        frappe.enqueue_doc(self.doctype, self.name, method="generate_images")

    def get_metrics(self):
        filters = {
            "reference_doctype": self.doctype,
            "reference_docname": self.name
        }
        rows = frappe.db.get_all("Simple Metric", filters=filters, fields=["key", "value"])
        return {row.key: row.value for row in rows}

    def update_metrics(self):
        comments = self.get_comment_count()
        self._update_metric("comments", comments)

    def _update_metric(self, key, value):
        filters = {
            "reference_doctype": self.doctype,
            "reference_docname": self.name,
            "key": key
        }
        try:
            doc = frappe.get_last_doc("Simple Metric", filters)
        except frappe.exceptions.DoesNotExistError:
            doc = frappe.get_doc(dict(filters, doctype="Simple Metric", value=value))
            doc.insert()
        else:
            doc.value = value
            doc.save()

    def get_comment_count(self):
        filters = {
            "reference_doctype": self.doctype,
            "reference_docname": self.name
        }
        topic = frappe.db.get_value("Discussion Topic", filters, 'name')
        return frappe.db.count("Discussion Reply", filters={"topic": topic})

    def render_svg(self):
        if self.svg:
            return self.svg

        h = hashlib.md5(self.code.encode('utf-8')).hexdigest()
        cache = frappe.cache()
        key = "sketch-" + h
        value = cache.get(key)
        if value:
            value = value.decode('utf-8')
        else:
            is_sketch = self.runtime == "sketch" # old version
            try:
                value = livecode.livecode_to_svg(self.code, is_sketch=is_sketch)
            except Exception as e:
                print(f"Failed to render {self.name} as svg: {e}")
                pass
            if value:
                cache.set(key, value)
        return value or DEFAULT_IMAGE

    @property
    def sketch_id(self):
        """Returns the numeric part of the name.

        For example, the skech_id will be "123" for sketch with name "SKETCH-123".
        """
        return self.name.replace("SKETCH-", "")

    def get_hash(self):
        """Returns the md5 hash of the code to use for caching.
        """
        return hashlib.md5(self.code.encode("utf-8")).hexdigest()

    def get_image_url(self, mode="s"):
        """Returns the image_url for this sketch.

        The mode argument could be one of "s" (for square)
        or "w" (for wide). The s is the default.
        """
        if not self.image_ready:
            return IMAGE_NOT_READY_URL
        hash_ = self.get_hash()
        return f"/s/{self.sketch_id}-{hash_}-{mode}.png"

    def get_owner(self):
        """Returns the owner of this sketch as a document.
        """
        return frappe.get_doc("User", self.owner)

    def get_owner_name(self):
        return self.get_owner().full_name

    def get_livecode_url(self):
        doc = frappe.get_cached_doc("LMS Settings")
        return doc.livecode_url

    def get_livecode_ws_url(self):
        url = urlparse(self.get_livecode_url())
        protocol = "wss" if url.scheme == "https" else "ws"
        return protocol + "://" + url.netloc + "/livecode"

    def to_svg(self):
        return self.svg or self.render_svg()

    def render_svg(self):
        h = hashlib.md5(self.code.encode('utf-8')).hexdigest()
        cache = frappe.cache()
        key = "sketch-" + h
        value = cache.get(key)
        if value:
            value = value.decode('utf-8')
        else:
            value = livecode.livecode_to_svg(self.code)
            if value:
                cache.set(key, value)
        return value or DEFAULT_IMAGE

    def generate_images(self, converter=None):
        """Generates PNG images of different sizes.
        """
        svg = self.svg or DEFAULT_IMAGE
        hash_ = self.get_hash()

        converter = converter or CairoImageConverter()

        self.to_png(converter, hash_, "s")
        self.to_png(converter, hash_, "m")
        self.to_png(converter, hash_, "w")
        self.image_ready = True
        self._skip_before_save = True
        self.save(ignore_permissions=True)

    def to_png(self, converter, hash_, mode):
        cache_dir = Path(frappe.local.site_path) / "sketch-cache"
        cache_dir.mkdir(exist_ok=True)

        filename = f"{self.sketch_id}-{hash_}-{mode}.png"
        path = cache_dir / filename

        svg = self.svg or DEFAULT_IMAGE
        w, h = self.IMAGE_SIZES_BY_MODE[mode]

        converter.convert_image(svg, w=w, h=h, output_filename=str(path))

    @staticmethod
    def get_recent_sketches(start=0, limit=100, owner=None):
        """Returns the recent sketches.
        """
        filters = {}
        if owner:
            filters = {"owner": owner}
        sketches = frappe.get_all(
            "LMS Sketch",
            filters=filters,
            fields='*',
            order_by='creation desc',
            start=start,
            page_length=limit,
        )
        return [frappe.get_doc(doctype='LMS Sketch', **doc) for doc in sketches]

    @staticmethod
    def get_total_count():
        """Returns the total number of sketches
        """
        return frappe.db.count("LMS Sketch")

    # def __repr__(self):
    #     return f"<LMSSketch {self.name}>"

@frappe.whitelist()
def save_sketch(name, title, code):
    if not name or name == "new":
        doc = frappe.new_doc('LMS Sketch')
        doc.title = title
        doc.code = code
        doc.runtime = 'python-canvas'
        doc.insert(ignore_permissions=True)
        status = "created"
    else:
        doc = frappe.get_doc("LMS Sketch", name)

        if doc.owner != frappe.session.user:
            return {
                "ok": False,
                "error": "Permission Denied"
            }
        doc.title = title
        doc.code = code
        doc.svg = ''
        doc.save()
        status = "updated"
    return {
        "ok": True,
        "status": status,
        "name": doc.name,
        "id": doc.name.replace("SKETCH-", "")
    }

@frappe.whitelist()
def generate_images(doc):
    print("generate_images", doc)
    data = json.loads(doc)
    sketch = frappe.get_doc(data['doctype'], data['name'])
    sketch.before_save() # regenerate svg
    sketch.generate_images()
    frappe.msgprint(f"Successfully generated images for {sketch.doctype} {sketch.name}")

@frappe.whitelist()
def generate_images_with_svgexport(doc):
    print("generate_images", doc)
    data = json.loads(doc)
    sketch = frappe.get_doc(data['doctype'], data['name'])
    sketch.before_save() # regenerate svg
    sketch.generate_images(converter=SVGExportConverter())
    frappe.msgprint(f"Successfully generated images for {sketch.doctype} {sketch.name}")

class ImageConverter:
    """Base class to convert image from svg to png.
    """
    def convert_image(self, svg, w, h, output_filename):
        raise NotImplementedError()

class CairoImageConverter(ImageConverter):
    def convert_image(self, svg, w, h, output_filename):
        print("generating", output_filename, "using cariosvg")
        png = cairosvg.svg2png(svg, output_width=w, output_height=h)
        path = Path(output_filename)
        path.write_bytes(png)

class CLIConverter(ImageConverter):
    def get_command_pattern(self):
        raise NotImplementedError()

    def convert_image(self, svg, w, h, output_filename):
        print("generating", output_filename, "using", self.__class__.__name__)
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.svg"
            input_path.write_text(svg)
            input_filename = str(input_path)
            cmd = self.get_command_pattern().format(**locals())
            os.system(cmd)

class SVGExportConverter(CLIConverter):
    def get_command_pattern(self):
        return "svgexport {input_filename} {output_filename} format png output {w}:{h} viewbox pad"

def create_converter(name):
    converters = {
        "cairosvg": CairoImageConverter,
        "svgexport": SVGExportConverter
    }
    cls = converters[name]
    return cls()
