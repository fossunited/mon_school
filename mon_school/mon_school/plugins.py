"""The plugin module implements various plugins to extend the behaviour
of community app.

The plugins provided by this module are:

    SketchsTab - additional tab to show on the profile pages
    LiveCodeExtension - injecting livecode css/js into lesson page
"""
import frappe
from community.plugins import PageExtension, ProfileTab

class SketchesTab(ProfileTab):
    def get_title(self):
        return "Sketches"

    def render(self):
        return "Coming Soon!"

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
    return f"<h2>Exercise: {argument}</h2>"

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