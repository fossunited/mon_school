"""The webpages module provides an easier way to create custom pages using @route decorator.
"""
import frappe
import math

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
        context.template = "www/404.html"
        return

    try:
        page = int(frappe.form_dict.get("page", 1))
    except ValueError:
        page = 1

    page_size = 48
    start = (page-1)*page_size

    num_entries = contest.get_submitted_entries_count()
    entries = contest.get_submitted_entries(start=start, page_size=page_size)

    context.contest = contest
    context.entries = entries
    context.page_context = {}
    context.metatags = get_metatags()
    context.page = page
    context.num_pages = math.ceil(num_entries/page_size)

def get_metatags():
    """Returns the metatags for the current URL as specified in
    Website Route Meta document with the same route.
    """
    route = frappe.request.path[1:]
    try:
        doc = frappe.get_doc("Website Route Meta", route)
    except frappe.DoesNotExistError:
        return {}

    metatags = {tag.key: tag.value for tag in doc.meta_tags}
    metatags.setdefault("url", frappe.request.url)
    return metatags
