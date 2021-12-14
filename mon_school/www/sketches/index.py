import math

import frappe
from mon_school.mon_school.doctype.lms_sketch.lms_sketch import LMSSketch as Sketch


def get_context(context):
    context.no_cache = 1

    page = get_page()
    limit = get_limit()

    num_sketches = Sketch.get_total_count()

    start = get_offset(page, page_length=limit)
    num_pages = get_num_pages(num_sketches, page_length=limit)

    context.page = page
    context.num_pages = num_pages
    context.sketches = Sketch.get_recent_sketches(start=start, limit=limit)


def get_page():
    try:
        page = int(frappe.form_dict.get("page", 1))
    except ValueError:
        page = 1

    return page


def get_limit(default=48):
    try:
        value = frappe.form_dict.get("limit", default)
        limit = int(value)
        return bound(limit, min_value=default, max_value=1000)
    except ValueError:
        return default


def bound(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value


def get_offset(page, page_length):
    return (page - 1) * page_length


def get_num_pages(total_items, page_length):
    # max(1, ...) so that there is at least 1 page, even with 0 items
    return max(1, math.ceil(total_items/page_length))
