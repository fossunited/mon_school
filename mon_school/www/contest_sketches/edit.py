"""The webpages module provides an easier way to create custom pages using @route decorator.
"""
from urllib.parse import urlencode, urljoin

import frappe
from frappe.website.doctype.website_settings.website_settings import get_website_settings
from frappe.website.utils import build_response

DEFAULT_CODE = """\
c = circle()
show(c)
"""
def get_context(context):
    context.no_cache = 1

    try:
        contest_name = frappe.form_dict["contest"]
    except KeyError:
        context.template = "www/404.html"
        return

    try:
        contest = frappe.get_doc("Contest", contest_name)
    except frappe.DoesNotExistError:
        return render_template("www/404.html")

    if frappe.session.user == "Guest":
        context.error = "not-logged-in"
        context.contest = contest
        context.sketch = None
        context.page_context = {}
        return
    elif not contest.is_participant(frappe.session.user):
        context.error = "not-participant"
        context.contest = contest
        context.sketch = None
        context.page_context = {}
        return

    sketch = contest.get_user_submission()
    if not sketch:
        sketch = frappe.get_doc({
            "doctype": "Contest Entry",
            "name": "new",
            "contest": contest_name,
            "code": DEFAULT_CODE,
            "owner": frappe.session.user,
            "is_submitted": False
        })

    context.contest = contest
    context.sketch = sketch
    context.page_context = {}
    context.metatags = get_metatags(sketch)

def get_metatags(sketch):
    title = f"{sketch.title}  by {sketch.get_owner_name()}"
    image = sketch.get_image_url(mode="w")
    url = f"{frappe.request.host_url}sketches/{sketch.sketch_id}"
    return {
        "title": title,
        "description": sketch.code,
        "image": image,
        "url": url
    }
