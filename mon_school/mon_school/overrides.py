import frappe
import hashlib
import re
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response

from mon_school.mon_school.doctype.lms_sketch.lms_sketch import LMSSketch, DEFAULT_IMAGE
from community.lms.doctype.exercise.exercise import Exercise as _Exercise
from community.lms.doctype.exercise_submission.exercise_submission import ExerciseSubmission as _ExerciseSubmission
from community.lms.doctype.lms_batch_membership.lms_batch_membership import LMSBatchMembership as _LMSBatchMembership

import html
from urllib.parse import urlparse
from ..joy.build import get_livecode_files
from . import livecode

class Sketch(LMSSketch):
    def before_save(self):
        try:
            is_sketch = self.runtime == "sketch" # old version
            self.svg = livecode_to_svg(self.code, is_sketch=is_sketch)
        except Exception:
            frappe.log_error(f"Failed to save svg for sketch {self.name}")

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
                value = livecode_to_svg(self.code, is_sketch=is_sketch)
            except Exception as e:
                print(f"Failed to render {self.name} as svg: {e}")
                pass
            if value:
                cache.set(key, value)
        return value or DEFAULT_IMAGE

class Exercise(_Exercise):
    def before_save(self):
        self.image = livecode_to_svg(self.answer)

class ExerciseSubmission(_ExerciseSubmission):
    def before_save(self):
        self.image = livecode_to_svg(self.solution)

class LMSBatchMembership(_LMSBatchMembership):
    def validate_membership_in_different_batch_same_course(self):
        if self.member_type == "Mentor":
            return
        else:
            return super().validate_membership_in_different_batch_same_course()

def livecode_to_svg(code, is_sketch=False):
    """Renders the code as svg.
    """
    result = livecode.execute(code, is_sketch=is_sketch)
    if result.get('status') != 'success':
        return None

    return _render_svg(result['shapes'])

def _render_svg(shapes):
    return (
        '<svg width="300" height="300" viewBox="-150 -150 300 300" fill="none" stroke="black" xmlns="http://www.w3.org/2000/svg">\n'
        + "\n".join(_render_shape(s) for s in shapes)
        + '\n'
        + '</svg>\n')

def _render_shape(node):
    tag = node.pop("tag")
    children = node.pop("children", None)

    items = [(k.replace("_", "-"), html.escape(str(v))) for k, v in node.items() if v is not None]
    attrs = " ".join(f'{name}="{value}"' for name, value in items)

    if children:
        children_svg = "\n".join(_render_shape(c) for c in children)
        return f"<{tag} {attrs}>{children_svg}</{tag}>"
    else:
        return f"<{tag} {attrs} />"

RE_SKETCH_IMAGE = re.compile(r"s/(\d+).svg$")

class SketchImage(BaseRenderer):
    def can_render(self):
        return RE_SKETCH_IMAGE.match(self.path) is not None

    def render(self):
        m = RE_SKETCH_IMAGE.match(self.path)
        sketch_id = m.group(1)
        name = f"SKETCH-{sketch_id}"
        try:
            s = frappe.get_doc("LMS Sketch", name)
            svg = s.svg or _render_svg([])
            return Response(svg, content_type="image/svg+xml")
        except frappe.DoesNotExistError:
            s = None
            return Response("", status="404 Not Found")
