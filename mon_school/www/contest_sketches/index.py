"""The webpages module provides an easier way to create custom pages using @route decorator.
"""
import frappe

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

    entries = contest.get_submitted_entries()

    print("submissions", contest_name, len(entries))
    context.contest = contest
    context.entries = entries
    context.page_context = {}
