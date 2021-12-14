"""Global context for templates injected by Mon School.

Adds a variable `monschool` to the context, which is an instance of
MonSchool containing all the utilities provided by the Mon School app.
"""
import frappe

def update_website_context(context):
    context.monschool = MonSchool()

class MonSchool:
    """Utilities to use in templates from monschool.

    If you want to include a function to be available to all the templates,
    including the web templates, add it here.
    """
    def ping(self):
        return "pong"

