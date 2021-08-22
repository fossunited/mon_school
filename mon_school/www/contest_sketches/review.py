"""The webpages module provides an easier way to create custom pages using @route decorator.
"""
import frappe
import math
from urllib.parse import urlencode

def get_context(context):
    context.no_cache = 1

    try:
        contest_name = frappe.form_dict["contest"]
    except KeyError:
        context.template = "www/404.html"
        return

    tab = frappe.form_dict.get("tab", "bookmarks")
    if tab not in ['bookmarks', 'all']:
        tab = 'bookmarks'

    try:
        contest = frappe.get_doc("Contest", contest_name)
    except frappe.DoesNotExistError:
        context.template = "www/404.html"
        return

    try:
        page = int(frappe.form_dict.get("page", 1))
    except ValueError:
        page = 1

    page_size = 100
    start = (page-1)*page_size

    num_entries = contest.get_submitted_entries_count()
    entries = contest.get_submitted_entries(start=start, page_size=page_size)

    context.tab = tab
    context.contest = contest
    context.entries = entries
    context.page_context = {}
    context.metatags = get_metatags()
    context.page = page
    context.num_pages = math.ceil(num_entries/page_size)
    context.bookmarks = contest.get_bookmarked_entries()
    context.likes = {entry.name: True for entry in context.bookmarks}
    context.changequery = changequery

    context.all_entry_names = frappe.get_all(
        "Contest Entry",
        filters={"is_submitted": True},
        pluck='name',
        order_by='modified desc')

    if "entry" in frappe.form_dict:
        entry_name = frappe.form_dict["entry"]
    else:
        entry_name = None
    get_context_for_entry(context, entry_name)


def get_context_for_entry(context, entry_name):
    if entry_name is None:
        context.entry = None
        context.next_url = None
        context.prev_url = None
        context.index = None
    else:
        context.entry = frappe.get_doc("Contest Entry", entry_name)
        context.ratings = get_ratings(context.entry)

        if context.tab == "bookmarks":
            entries = list(context.likes)
        else:
            entries = context.all_entry_names

        # XXX-Anand: what if entry_name is not in likes?
        context.index = entries.index(entry_name)
        context.count = len(entries)

        context.prev_url = find_prev(entries, context.index, context.count)
        context.next_url = find_next(entries, context.index, context.count)

def get_ratings(entry):
    labels = ["Creative Elements", "Aesthetic", "Geometric Patterns", "Pookkalam Rules"]
    ratings = entry.get_ratings() or {}
    return [{"label": label, "rating": ratings.get(label, 0)} for label in labels]

def find_prev(entries, index, count):
    if index-1 >= 0:
        return changequery(entry=entries[index-1])

def find_next(entries, index, count):
    if index+1 < count:
        return changequery(entry=entries[index+1])


# def find_next_entry(context):
#     if context.tab == "bookmarks":
#         if context.index+1 >= context.count:
#             return None
#         else:
#             return changequery(entry=likes[index+1])
#     else:
#         entries = [e.name for e in context.entries]
#         try:
#             index = entries.index(context.entry.name)
#         except ValueError:
#             return changequery(entry=None)

#         if index+1 >= len(entries):
#             return changequery(entry=None, page=context.page+1)
#         else:
#             return changequery(entry=entries[index+1])

# def find_prev_entry(context):
#     if context.tab == "bookmarks":
#         likes = list(context.likes)
#         try:
#             index = likes.index(context.entry.name)
#         except ValueError:
#             return changequery(entry=None)

#         if index-1 <=0 :
#             return changequery(entry=None)
#         else:
#             return changequery(entry=likes[index-1])
#     else:
#         entries = [e.name for e in context.entries]
#         try:
#             index = entries.index(context.entry.name)
#         except ValueError:
#             return changequery(entry=None)

#         if index+1 >= len(entries):
#             return changequery(entry=None, page=context.page+1)
#         else:
#             return changequery(entry=entries[index+1])

def changequery(**kwargs):
    """Change the query parameters in the current query.
    """
    q = dict(frappe.form_dict)
    q.update(kwargs)

    # contest is already in the path
    del q['contest']

    q = {k: v for k, v in q.items() if v is not None} # remove Nones
    url = frappe.request.path + "?" + urlencode(q)
    return url

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
