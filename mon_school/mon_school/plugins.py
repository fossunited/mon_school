"""The plugin module implements various plugins to extend the behaviour
of community app.

The plugins provided by this module are:

    SketchsTab - additional tab to show on the profile pages
    LiveCodeExtension - injecting livecode css/js into lesson page
"""
import frappe
from community.plugins import PageExtension, ProfileTab
from community.widgets import Widgets
from .overrides import Sketch

class SketchesTab(ProfileTab):
    def get_title(self):
        return "Sketches"

    def render(self):
        sketches = Sketch.get_recent_sketches(owner=self.user, limit=16)
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