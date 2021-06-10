"""The plugin module implements various plugins to extend the behaviour
of community app.

The plugins provided by this module are:

    SketchsTab - additional tab to show on the profile pages
    LiveCodeExtension - injecting livecode css/js into lesson page
"""
from community.plugins import ProfileTab

class SketchesTab(ProfileTab):
    def get_title(self):
        return "Sketches"

    def render(self):
        return "Coming Soon!"
