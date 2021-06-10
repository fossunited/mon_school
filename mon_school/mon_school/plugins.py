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

