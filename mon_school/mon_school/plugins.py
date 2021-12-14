"""The plugin module implements various plugins to extend the behaviour
of the school app.

The plugins provided by this module are:

    SketchsTab - additional tab to show on the profile pages
    LiveCodeExtension - injecting livecode css/js into lesson page
"""
import frappe
from school.plugins import PageExtension, ProfileTab
from school.widgets import Widgets
from .doctype.lms_sketch.lms_sketch import LMSSketch as Sketch
import json
import html

class SketchesTab(ProfileTab):
    def get_title(self):
        return "Sketches"

    def render(self):
        sketches = Sketch.get_recent_sketches(owner=self.user.name, limit=16)
        context = dict(sketches=sketches, widgets=Widgets())
        return frappe.render_template(
            "templates/profile/sketches.html",
            context)

class LiveCodeExtension(PageExtension):
    def render_header(self):
        livecode_url = frappe.get_value("LMS Settings", None, "livecode_url")
        context = {
            "livecode_url": livecode_url
        }
        return frappe.render_template(
            "templates/livecode/extension_header.html",
            context)

    def render_footer(self):
        livecode_url = frappe.get_value("LMS Settings", None, "livecode_url")
        context = {
            "livecode_url": livecode_url
        }
        return frappe.render_template(
            "templates/livecode/extension_footer.html",
            context)

def exercise_renderer(argument):
    exercise = frappe.get_doc("Exercise", argument)
    context = dict(exercise=exercise)
    return frappe.render_template("templates/exercise.html", context)

def image_renderer(argument):
    """Markdown macro for Image.

    Rendered the image of an exercise.

    This is a hack to extend the already exiting exercise infrastrcture
    to use for showing images. To distinguish between real exercises and
    the exercises used for showing images, the latter ones are prefixed
    with `image-`.

    usage:

        {{ Image("image-flag-of-germany") }}
    """
    exercise = frappe.get_doc("Exercise", argument)
    context = dict(exercise=exercise)
    return frappe.render_template("templates/image.html", context)


def youtube_video_renderer(video_id):
    return f"""
    <iframe width="560" height="315"
        src="https://www.youtube.com/embed/{video_id}"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
    """


def widget_renderer(widget_id):
    """Renders an interactive widget.

    A widget is written as a web template.
    """
    doc = frappe.get_doc("Web Template", widget_id)
    t = html.escape(json.dumps(doc.template))
    return f"<div class='widget' data-template='{t}'></div>"

